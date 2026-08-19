#!/usr/bin/env python3
"""吞吐量专项：单流 TTFT（冷/热由调用者控制次序）+ 并发聚合吞吐。

用法示例:
  python3 throughput_bench.py final --model ~/mlx-models/<model-dir> --levels 1,2,4,8

口径声明（固定写入结果文件）：
  端到端 HTTP（含调度/Tokenizer/Prefill/逐 token 解码）；
  聚合吞吐 = 该并发批次全部请求的 completion_tokens 之和 / 批次墙钟时间。
服务器需以 decode 并发 >= 最大并发级别启动（mlx_lm.server --decode-concurrency N），
否则退化为排队串行。长 prompt TTFT 依赖用户配置的本地代码文件，未配置则跳过并标注。
测前排除后台重 IO：大文件下载抢内存带宽，实测拖慢单流 40% 以上。
"""

from __future__ import annotations

import argparse
import json
import threading
import time
import urllib.request

import bench_common as bc

SHORT_PROMPT = "写一段 300 字左右的说明文，解释为什么数据库需要索引，举一个具体例子。"
TTFT_SHORT_PROMPT = "你好，请自我介绍。"
CALIBER = "端到端 HTTP 含 prefill；聚合 = 批次总生成 token / 批次墙钟；每流 max_tokens 固定"


def one_request(base_url: str, model: str, max_tokens: int, results: dict, idx: int) -> None:
    payload = {"model": model, "messages": [{"role": "user", "content": SHORT_PROMPT}],
               "temperature": 0.0, "max_tokens": max_tokens}
    request = urllib.request.Request(
        f"{base_url}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    started = time.time()
    try:
        response = json.load(urllib.request.urlopen(request, timeout=900))
        results[idx] = {"wall": time.time() - started,
                        "tokens": response["usage"]["completion_tokens"]}
    except Exception as exc:
        results[idx] = {"error": str(exc)[:200]}


def ttft_streaming(base_url: str, model: str, prompt: str, label: str):
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}],
               "temperature": 0.0, "max_tokens": 50, "stream": True}
    request = urllib.request.Request(
        f"{base_url}/chat/completions", data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"})
    started = time.time()
    ttft = None
    with urllib.request.urlopen(request, timeout=900) as response:
        for line in response:
            # 首个增量块即算生成开始（reasoning 或 content 都算）
            if line.startswith(b"data: ") and (
                    b'"content"' in line or b'"reasoning"' in line or b'"delta"' in line):
                ttft = time.time() - started
                break
    print(f"  TTFT[{label}]: {ttft:.2f}s" if ttft else f"  TTFT[{label}]: 无内容块", flush=True)
    return round(ttft, 2) if ttft else None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label", nargs="?", default="default", help="结果标签")
    parser.add_argument("--model", help="请求 payload 的 model 字段")
    parser.add_argument("--base-url", help="OpenAI 兼容端点")
    parser.add_argument("--port", type=int, help=f"仅改端口时用，默认 {bc.DEFAULT_PORT}")
    parser.add_argument("--workdir", help="结果目录，默认 ~/local-model-bench")
    parser.add_argument("--config", help="非秘密配置文件路径")
    parser.add_argument("--levels", default="1,2,4,8", help="并发级别，默认 1,2,4,8")
    parser.add_argument("--stream-max-tokens", type=int, default=300,
                        help="并发测试每流生成上限，默认 300")
    parser.add_argument("--long-context-file", help="长 prompt TTFT 用的本地代码文件；"
                        "默认取 config 的 throughput.long_context_file 或 context_files.A2")
    parser.add_argument("--mock", action="store_true", help="不发 HTTP，用假数据自测管线")
    args = parser.parse_args()

    config, _ = bc.load_config(args.config)
    model = bc.resolve_model(args.model, config, mock=args.mock)
    base_url = bc.resolve_base_url(args.base_url, args.port, config)
    workdir = bc.resolve_workdir(args.workdir, config)
    levels = [int(x) for x in args.levels.split(",") if x.strip()]

    if args.mock:
        def one_request_fn(bu, mdl, mt, results, idx):
            results[idx] = {"wall": 0.5, "tokens": mt}

        def ttft_fn(bu, mdl, prompt, label):
            print(f"  TTFT[{label}]: 0.05s (mock)", flush=True)
            return 0.05
    else:
        one_request_fn, ttft_fn = one_request, ttft_streaming

    out = {"label": args.label, "model": bc.fold_home(model), "base_url": base_url,
           "caliber": CALIBER, "mock": args.mock, "levels": {}}

    print("预热...", flush=True)
    warm: dict = {}
    one_request_fn(base_url, model, 10, warm, 0)
    if "error" in warm.get(0, {}):
        raise SystemExit(f"预热失败: {warm[0]['error']}（先确认服务器已启动）")

    print("TTFT 测试:", flush=True)
    out["ttft_short_s"] = ttft_fn(base_url, model, TTFT_SHORT_PROMPT, "短prompt")
    long_file = args.long_context_file or (
        (config.get("throughput") or {}).get("long_context_file")) or (
        (config.get("context_files") or {}).get("A2"))
    if args.mock and not long_file:
        out["ttft_long_s"] = None
        out["ttft_long_skipped"] = "mock 模式未配置长文件"
    elif long_file:
        path = bc.context_file_for({"qid": "_ttft", "context_file": long_file}, config)
        if path and path.is_file():
            long_prompt = ("以下是资料：\n" + path.read_text(encoding="utf-8", errors="ignore")[:20000]
                           + "\n请用一句话总结。")
            out["ttft_long_s"] = ttft_fn(base_url, model, long_prompt, "6k prompt")
        else:
            out["ttft_long_s"] = None
            out["ttft_long_skipped"] = f"文件不存在: {bc.fold_home(str(path))}"
    else:
        out["ttft_long_s"] = None
        out["ttft_long_skipped"] = "未配置长 prompt 文件（config 的 throughput.long_context_file）"
    if out.get("ttft_long_skipped"):
        print(f"  TTFT[6k prompt]: skipped —— {out['ttft_long_skipped']}", flush=True)

    for level in levels:
        print(f"并发 {level} ...", flush=True)
        results: dict = {}
        threads = [threading.Thread(target=one_request_fn,
                                    args=(base_url, model, args.stream_max_tokens, results, i))
                   for i in range(level)]
        started = time.time()
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        batch_wall = time.time() - started
        ok = [v for v in results.values() if "tokens" in v]
        if args.mock and ok:
            batch_wall = max(v["wall"] for v in ok)  # mock 无真实墙钟，避免除近零出荒谬数
        errors = [v for v in results.values() if "error" in v]
        total_tokens = sum(v["tokens"] for v in ok)
        aggregate = total_tokens / batch_wall if batch_wall else 0
        per_stream = [round(v["tokens"] / v["wall"], 1) for v in ok if v["wall"]]
        out["levels"][level] = {
            "batch_wall_s": round(batch_wall, 1),
            "total_tokens": total_tokens,
            "aggregate_tok_s": round(aggregate, 1),
            "per_stream_tok_s": per_stream,
            "errors": len(errors),
        }
        print(f"  并发{level}: 聚合 {aggregate:.1f} tok/s | 单流 {per_stream} | "
              f"批次 {batch_wall:.1f}s | 失败 {len(errors)}", flush=True)

    out["checked_at"] = bc.now_rfc3339()
    resdir = workdir / "results"
    resdir.mkdir(parents=True, exist_ok=True)
    path = resdir / f"throughput_{args.label}.json"
    path.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"结果已存 {bc.fold_home(str(path))} 更新时间 {out['checked_at']}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
