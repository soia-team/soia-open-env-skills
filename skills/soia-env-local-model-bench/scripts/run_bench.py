#!/usr/bin/env python3
"""本地模型题库评测执行器：对 OpenAI 兼容端点跑题库并自动判定。

用法示例:
  python3 run_bench.py nothink --model ~/mlx-models/<model-dir>
  python3 run_bench.py nothink --list            # 只列题与可跑状态，不执行
  python3 run_bench.py smoke --mock              # 无服务器自测整条管线

group 只是结果标签；推理深度等真实配置由启动引擎时的参数决定（见 SKILL.md）。
题库 = 技能包 questions/ 与私有题目录合并，qid 冲突私有覆盖；题库文件为唯一真源。
结果: <workdir>/results/<group>.jsonl（每题含完整 request/response 原文）与
      <workdir>/outputs/<group>/<qid>.md（content 与 reasoning 全量，不截断）。
速度口径: 端到端 HTTP（含 prefill），tok/s = completion_tokens / 墙钟。
断点续跑: 同 group 锁定同一模型；结果文件中的 model 与当前模型不一致时拒绝启动，
          防止旧模型数据静默冒充新模型（换新 group 名重跑即可）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import time
import urllib.request
from pathlib import Path

import bench_common as bc

STATUS_ICON = {True: "PASS", False: "FAIL", None: "MANUAL"}


def dim_of(qid: str) -> str:
    """qid 的维度 = 大写字母前缀（A1→A、D2b→D、C10→C）。"""
    match = re.match(r"^([A-Z]+)", qid)
    return match.group(1) if match else "?"


# ---------- 输出抽取 ----------

def extract_code(text: str) -> str:
    blocks = re.findall(r"```(?:[a-zA-Z]*)\n(.*?)```", text, re.S)
    if blocks:
        return blocks[-1].strip()
    return text.strip()


def extract_json(text: str):
    match = re.search(r"\{.*\}", extract_code(text), re.S)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


# ---------- 判定引擎（由题目 yaml 的 check 字段驱动） ----------

def run_node(code: str, test_snippet: str):
    src = code + "\n" + test_snippet
    try:
        proc = subprocess.run(
            ["node", "--input-type=module", "-e", src],
            capture_output=True, text=True, timeout=30,
        )
    except FileNotFoundError:
        return None, "缺 node，无法自动判定（安装 Node.js 后重跑）"
    except subprocess.TimeoutExpired:
        return False, "node 判定超时(30s)"
    out = (proc.stdout + proc.stderr).strip()
    return ("PASS" in proc.stdout, out[-500:])


def _json_path_get(data, path: str):
    current = data
    for part in path.split("."):
        if not isinstance(current, dict):
            return None, False
        names = part.split("|") if "|" in part else [part]
        for name in names:
            if name in current:
                current = current[name]
                break
        else:
            return None, False
    return current, True


_TYPE_MAP = {"str": str, "int": int, "list": list, "dict": dict, "float": float, "bool": bool}


def _check_json_expect(spec: dict, content: str):
    data = extract_json(content)
    if data is None:
        return False, "无法解析 JSON"
    brief = json.dumps(data, ensure_ascii=False)[:200]
    exact_keys = spec.get("exact_keys")
    if exact_keys and (not isinstance(data, dict) or set(data.keys()) != set(exact_keys)):
        return False, f"字段集不符: {brief}"
    for rule in spec.get("expects") or []:
        value, found = _json_path_get(data, str(rule.get("path", "")))
        label = rule.get("path")
        if not found:
            return False, f"缺字段 {label}: {brief}"
        if "equals" in rule and value != rule["equals"]:
            return False, f"{label} != {rule['equals']!r}: {brief}"
        if "in" in rule and value not in rule["in"]:
            return False, f"{label} 取值不符: {brief}"
        if "lower_in" in rule and str(value).lower() not in [str(x).lower() for x in rule["lower_in"]]:
            return False, f"{label} 取值不符: {brief}"
        expected_type = _TYPE_MAP.get(rule.get("type", ""))
        if expected_type and not isinstance(value, expected_type):
            return False, f"{label} 类型不是 {rule['type']}: {brief}"
        if "min" in rule and not (isinstance(value, (int, float)) and value >= rule["min"]):
            return False, f"{label} < {rule['min']}: {brief}"
        if "max" in rule and not (isinstance(value, (int, float)) and value <= rule["max"]):
            return False, f"{label} > {rule['max']}: {brief}"
        if "min_len" in rule and not (hasattr(value, "__len__") and len(value) >= rule["min_len"]):
            return False, f"{label} 长度 < {rule['min_len']}: {brief}"
        if "regex" in rule and not re.search(rule["regex"], str(value)):
            return False, f"{label} 不匹配 {rule['regex']}: {brief}"
    return True, brief


def _check_regex(spec: dict, content: str):
    tail = int(spec.get("tail") or 0)
    scope = content[-tail:] if tail else content
    matched = any(re.search(p, scope) for p in spec.get("any_patterns") or [])
    rejected = bool(spec.get("reject")) and bool(re.search(spec["reject"], content))
    if matched and rejected:
        # 正确与错误表述并存（典型：辟谣式讲解原文引用错误说法）——正则无法裁决真实结论，转人工
        return None, f"any 与 reject 同时命中（矛盾信号），转人工复核。结尾: ...{scope[-80:]}"
    return (matched and not rejected, f"结尾: ...{scope[-80:]}")


def _check_lines(spec: dict, content: str):
    lines = [line.strip() for line in content.strip().splitlines() if line.strip()]
    min_lines = int(spec.get("min_lines") or len(spec.get("lines") or []))
    if len(lines) < min_lines:
        return False, f"仅 {len(lines)} 行"
    for index, rule in enumerate(spec.get("lines") or []):
        line = lines[index]
        if "contains" in rule and str(rule["contains"]) not in line:
            return False, f"第{index + 1}行缺 {rule['contains']!r}: {line[:60]}"
        if "regex" in rule and not re.search(rule["regex"], line):
            return False, f"第{index + 1}行不匹配 {rule['regex']}: {line[:60]}"
    return True, " | ".join(lines[:3])[:200]


def run_check(question: dict, content: str):
    spec = question["check"]
    kind = spec["type"]
    try:
        if kind == "speed":
            return True, "计时题"
        if kind in ("save", "manual"):
            return None, "待人工评审"
        if kind == "node_snippet":
            code = extract_code(content)
            if spec.get("prepend_context"):
                code = (question.get("context_code") or "") + "\n" + code
            return run_node(code, spec.get("test") or "")
        if kind == "regex":
            return _check_regex(spec, content)
        if kind == "json_expect":
            return _check_json_expect(spec, content)
        if kind == "lines_expect":
            return _check_lines(spec, content)
    except Exception as exc:  # 判定器自身异常不终止整轮评测
        return False, f"校验异常: {exc}"
    return None, f"未知判定类型 {kind}"


# ---------- 请求 ----------

def build_payload(prompt: str, temp: float, max_tokens: int) -> dict:
    """请求 payload（不含 model 字段）；同一对象原样归档进结果 jsonl 的 request 字段。"""
    return {
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temp,
        "max_tokens": max_tokens,
    }


def call_endpoint(base_url: str, model: str, payload: dict, timeout: float) -> dict:
    request = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps({"model": model, **payload}).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.time()
    response = json.load(urllib.request.urlopen(request, timeout=timeout))
    wall = time.time() - started
    message = response["choices"][0]["message"]
    completion_tokens = response["usage"]["completion_tokens"]
    cached_tokens = (
        (response["usage"].get("prompt_tokens_details") or {}).get("cached_tokens")
    )
    return {
        "wall_s": round(wall, 1),
        "prompt_tokens": response["usage"]["prompt_tokens"],
        "completion_tokens": completion_tokens,
        "cached_tokens": cached_tokens,
        "tok_s": round(completion_tokens / wall, 1) if wall else 0.0,
        "content": message.get("content") or "",
        "reasoning": message.get("reasoning") or message.get("reasoning_content") or "",
        "finish": response["choices"][0].get("finish_reason"),
    }


def mock_call(question: dict) -> dict:
    content = question.get("mock_response") or f"mock output for {question['qid']}"
    return {
        "wall_s": 0.0,
        "prompt_tokens": len(question["prompt"]) // 3,
        "completion_tokens": max(1, len(content) // 3),
        "cached_tokens": None,
        "tok_s": 0.0,
        "content": content,
        "reasoning": "",
        "finish": "stop",
    }


# ---------- 主流程 ----------

def build_prompt(question: dict, config: dict):
    """返回 (prompt, skipped_reason)。占位题未配置 context_file 时跳过。"""
    template = question["prompt"]
    if "{context}" not in template:
        return template, None
    path = bc.context_file_for(question, config)
    if path is None:
        return None, "context_file 未配置（占位题，配置后才计入）"
    if not path.is_file():
        return None, f"context_file 不存在: {bc.fold_home(str(path))}"
    limit = int(question.get("max_context_chars") or 20000)
    context = path.read_text(encoding="utf-8", errors="ignore")[:limit]
    return template.replace("{context}", context), None


def list_questions(questions: dict, group: str, config: dict) -> None:
    print(f"{'qid':6} {'来源':9} {'判定':13} {'类别':14} 状态")
    for qid in sorted(questions):
        question = questions[qid]
        status = "可跑"
        if question.get("only_group") and question["only_group"] != group:
            status = f"跳过（仅 {question['only_group']} 组）"
        elif question.get("groups") and group not in question["groups"]:
            status = f"跳过（限 {','.join(question['groups'])} 组）"
        else:
            _, skipped = build_prompt(question, config)
            if skipped:
                status = f"跳过（{skipped}）"
        print(f"{qid:6} {question['_source']:9} {question['check']['type']:13} "
              f"{question['cat']:14} {status}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("group", help="结果标签，如 nothink / low / medium")
    parser.add_argument("--model", help="请求 payload 的 model 字段（mlx 需模型完整路径）")
    parser.add_argument("--base-url", help="OpenAI 兼容端点，默认 http://127.0.0.1:<port>/v1")
    parser.add_argument("--port", type=int, help=f"仅改端口时用，默认 {bc.DEFAULT_PORT}")
    parser.add_argument("--workdir", help="结果目录，默认 ~/local-model-bench")
    parser.add_argument("--config", help="非秘密配置文件路径（默认按技能配置目录扫描）")
    parser.add_argument("--questions-dir", help="公开题目录（默认技能包内 questions/）")
    parser.add_argument("--private-questions", help="私有题目录（默认按配置目录扫描）")
    parser.add_argument("--only", help="只跑这些 qid，逗号分隔")
    parser.add_argument("--timeout", type=float, default=1500, help="单题超时秒数，默认 1500")
    parser.add_argument("--mock", action="store_true", help="不发 HTTP，用题目 mock_response 自测管线")
    parser.add_argument("--list", action="store_true", help="只列出题目与可跑状态")
    args = parser.parse_args()

    config, config_path = bc.load_config(args.config)
    private_dir = bc.private_questions_dir(args.private_questions, config)
    packaged_dir = Path(args.questions_dir).expanduser() if args.questions_dir else None
    questions, notes = bc.load_questions(packaged_dir, private_dir)
    for note in notes:
        print(f"[题库] {note}", flush=True)
    if config_path:
        print(f"[配置] {bc.fold_home(str(config_path))}", flush=True)

    if args.list:
        list_questions(questions, args.group, config)
        return 0

    model = bc.resolve_model(args.model, config, mock=args.mock)
    base_url = bc.resolve_base_url(args.base_url, args.port, config)
    workdir = bc.resolve_workdir(args.workdir, config)
    outdir = workdir / "outputs" / args.group
    resdir = workdir / "results"
    outdir.mkdir(parents=True, exist_ok=True)
    resdir.mkdir(parents=True, exist_ok=True)
    resfile = resdir / f"{args.group}.jsonl"

    done: set[str] = set()
    seen_models: set[str] = set()
    if resfile.exists():
        for line in resfile.read_text(encoding="utf-8").splitlines():
            try:
                record = json.loads(line)
                done.add(record["qid"])
            except (json.JSONDecodeError, TypeError, KeyError):
                continue
            if record.get("model"):
                seen_models.add(record["model"])
    current_model = bc.fold_home(model)
    if seen_models and seen_models != {current_model}:
        raise SystemExit(
            f"[{args.group}] 续跑冲突：{bc.fold_home(str(resfile))} 已有模型 "
            f"{sorted(seen_models)} 的结果，当前模型为 {current_model}。"
            "同一 group 只对应一个模型（防止旧模型数据冒充新模型的结果）；"
            "请换一个新 group 名重跑，或移走旧结果文件。"
            "若确为同一模型只是路径写法不同，请沿用旧写法。"
        )
    if done and not seen_models:
        print(f"[{args.group}] 警告：既有结果缺 model 字段（旧格式），"
              "无法校验续跑模型一致性，请自行确认未换模型", flush=True)

    if not args.mock:
        print(f"[{args.group}] 预热（触发模型加载，不计时）...", flush=True)
        call_endpoint(base_url, model, build_payload("hi", 0.0, 5), timeout=600)

    only = {q.strip() for q in args.only.split(",")} if args.only else None
    counts = {"PASS": 0, "FAIL": 0, "MANUAL": 0, "skipped": 0, "error": 0}
    skipped_items: list[str] = []
    dim_auto: dict[str, list[int]] = {}  # 维度 -> [自动判定通过数, 自动判定总数]

    def append_record(record: dict) -> None:
        record["checked_at"] = bc.now_rfc3339()
        if args.mock:
            record["mock"] = True
        with resfile.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    for qid in sorted(questions):
        question = questions[qid]
        if only and qid not in only:
            continue
        if qid in done:
            print(f"[{args.group}] {qid} 已有结果，跳过（续跑模式）", flush=True)
            continue
        if question.get("only_group") and question["only_group"] != args.group:
            continue
        if question.get("groups") and args.group not in question["groups"]:
            continue
        prompt, skip_reason = build_prompt(question, config)
        if skip_reason:
            counts["skipped"] += 1
            skipped_items.append(f"{qid}（{skip_reason}）")
            append_record(dict(qid=qid, cat=question["cat"], group=args.group,
                               skipped=True, reason=skip_reason,
                               source=question["_source"], model=current_model))
            print(f"[{args.group}] {qid} SKIPPED {skip_reason}", flush=True)
            continue
        payload = build_payload(prompt, float(question["temp"]), int(question["max_tokens"]))
        try:
            reply = mock_call(question) if args.mock else call_endpoint(
                base_url, model, payload, args.timeout)
        except Exception as exc:
            counts["error"] += 1
            append_record(dict(qid=qid, cat=question["cat"], group=args.group,
                               error=str(exc)[:300], source=question["_source"],
                               model=current_model, request=payload))
            print(f"[{args.group}] {qid} 错误: {exc}", flush=True)
            continue
        verdict, note = run_check(question, reply["content"])
        counts[STATUS_ICON[verdict]] += 1
        if verdict is not None:  # MANUAL/skipped/error 不进分维度分母
            stats = dim_auto.setdefault(dim_of(qid), [0, 0])
            stats[1] += 1
            stats[0] += int(verdict)
        append_record(dict(
            qid=qid, cat=question["cat"], group=args.group,
            wall_s=reply["wall_s"], prompt_tokens=reply["prompt_tokens"],
            completion_tokens=reply["completion_tokens"],
            cached_tokens=reply["cached_tokens"], tok_s=reply["tok_s"],
            reasoning_chars=len(reply["reasoning"]), content_chars=len(reply["content"]),
            finish=reply["finish"], passed=verdict, note=note[:300],
            source=question["_source"], model=current_model,
            request=payload,
            response={"content": reply["content"], "reasoning": reply["reasoning"]}))
        (outdir / f"{qid}.md").write_text(
            f"# {qid} · {question['cat']} · {args.group}\n\n"
            f"耗时 {reply['wall_s']}s | 生成 {reply['completion_tokens']} tok | "
            f"{reply['tok_s']} tok/s | thinking {len(reply['reasoning'])} 字符 | 判定 {verdict}\n\n"
            f"## content\n\n{reply['content']}\n\n## reasoning\n\n{reply['reasoning']}\n",
            encoding="utf-8")
        if question["check"]["type"] == "save":
            ext = question["check"].get("ext") or "txt"
            (outdir / f"{qid}.{ext}").write_text(extract_code(reply["content"]), encoding="utf-8")
        print(f"[{args.group}] {qid} {STATUS_ICON[verdict]} {reply['wall_s']}s "
              f"{reply['tok_s']}tok/s think={len(reply['reasoning'])}ch "
              f"cache={reply['cached_tokens'] if reply['cached_tokens'] is not None else '-'} "
              f"{note[:60]}", flush=True)

    print(f"\n[{args.group}] 完成回执 更新时间 {bc.now_rfc3339()}")
    print(f"  自动判定: PASS {counts['PASS']} / FAIL {counts['FAIL']} / 待人工 {counts['MANUAL']}")
    if dim_auto:
        cells = " | ".join(f"{dim} {p}/{t}" for dim, (p, t) in sorted(dim_auto.items()))
        print(f"  分维度: {cells}（自动判定题 通过/总数；人工与 skipped 不计入）")
    print(f"  skipped: {counts['skipped']}"
          + (f" —— {'；'.join(skipped_items)}" if skipped_items else ""))
    print(f"  请求错误: {counts['error']}")
    print(f"  结果文件: {bc.fold_home(str(resfile))}（口径：端到端 HTTP 含 prefill）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
