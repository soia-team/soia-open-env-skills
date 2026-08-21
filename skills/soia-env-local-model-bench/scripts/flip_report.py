#!/usr/bin/env python3
"""跨 group 逐题翻转对比：配对精确 McNemar 检验，判定质量差异有没有统计资格。

用法示例:
  python3 flip_report.py <workdir> <groupA> <groupB>
  python3 flip_report.py ~/local-model-bench nothink low

读取 <workdir>/results/<group>.jsonl，按 qid 配对（只比两边都有自动判定结果的题）；
skipped / 请求错误 / 待人工(MANUAL) 记录不进配对，同 qid 多条记录取最后一条（最新复测）。
配对分类: 同对 / 同错 / A对B错(regression) / A错B对(improvement)。

显著性口径（纯标准库 math.comb，无 scipy 依赖）:
  b、c 为两个方向的翻转数，n = b + c；
  双侧精确 McNemar: p = Σ C(n,k) / 2^n，k ∈ [0..min(b,c)] ∪ [max(b,c)..n]。
  n < 6 时不做检验——不足 6 题单向翻转不可能达到 p<0.05，直接判无统计资格。

结论三档: 「显著差异 (p<0.05)」「翻转存在但无统计资格」「无差异」。
表述规范见 references/report-contract.md「统计资格」。
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path

import bench_common as bc

ALPHA = 0.05
MIN_FLIPS = 6  # 低于此翻转数，双侧精确 McNemar 数学上不可能显著


def dim_of(qid: str) -> str:
    """qid 的维度 = 大写字母前缀（A1→A、D2b→D、C10→C）。"""
    match = re.match(r"^([A-Z]+)", qid)
    return match.group(1) if match else "?"


def mcnemar_exact_p(b: int, c: int) -> float:
    """双侧精确 McNemar：翻转数在 Binomial(n, 0.5) 下的双尾概率（索引并集去重）。"""
    n = b + c
    ks = set(range(0, min(b, c) + 1)) | set(range(max(b, c), n + 1))
    return sum(math.comb(n, k) for k in ks) / 2 ** n


def load_group(resdir: Path, group: str) -> dict[str, dict]:
    path = resdir / f"{group}.jsonl"
    if not path.is_file():
        raise SystemExit(f"结果文件不存在: {bc.fold_home(str(path))}")
    records: dict[str, dict] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        try:
            record = json.loads(line)
            qid = record["qid"]
        except (json.JSONDecodeError, TypeError, KeyError):
            continue
        records[qid] = record  # 同 qid 取最后一条
    if not records:
        raise SystemExit(f"结果文件无有效记录: {bc.fold_home(str(path))}")
    return records


def verdict_of(record: dict) -> tuple[bool | None, str]:
    """返回 (布尔判定或 None, 标签)；只有布尔判定可进配对。"""
    if record.get("skipped"):
        return None, "skipped"
    if "error" in record:
        return None, "请求错误"
    passed = record.get("passed", "缺字段")
    if passed is True:
        return True, "PASS"
    if passed is False:
        return False, "FAIL"
    if passed is None:
        return None, "待人工"
    return None, "缺 passed 字段"


def describe_model(records: dict[str, dict]) -> str:
    models = sorted({r.get("model") for r in records.values() if r.get("model")})
    text = " / ".join(models) if models else "<记录无 model 字段>"
    if any(r.get("mock") for r in records.values()):
        text += "（mock 数据，不作真实结论）"
    return text


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("workdir", help="评测工作目录（含 results/<group>.jsonl）")
    parser.add_argument("groupA", help="基线组标签，如 nothink")
    parser.add_argument("groupB", help="对比组标签，如 low")
    args = parser.parse_args()

    if args.groupA == args.groupB:
        raise SystemExit("groupA 与 groupB 相同，没有可对比的翻转")
    resdir = Path(args.workdir).expanduser() / "results"
    records_a = load_group(resdir, args.groupA)
    records_b = load_group(resdir, args.groupB)

    paired: list[tuple[str, bool, bool]] = []      # (qid, A判定, B判定)
    excluded: list[str] = []                       # 两边都有 qid 但进不了配对
    for qid in sorted(set(records_a) & set(records_b)):
        verdict_a, label_a = verdict_of(records_a[qid])
        verdict_b, label_b = verdict_of(records_b[qid])
        if verdict_a is None or verdict_b is None:
            reason_a = f"A={label_a}" if verdict_a is None else ""
            reason_b = f"B={label_b}" if verdict_b is None else ""
            excluded.append(f"{qid}（{'，'.join(x for x in (reason_a, reason_b) if x)}）")
        else:
            paired.append((qid, verdict_a, verdict_b))
    only_a = sorted(set(records_a) - set(records_b))
    only_b = sorted(set(records_b) - set(records_a))

    print(f"# 翻转对比 A={args.groupA} → B={args.groupB}")
    print(f"- A({args.groupA}) 模型: {describe_model(records_a)}")
    print(f"- B({args.groupB}) 模型: {describe_model(records_b)}")
    print(f"- 配对题数: {len(paired)}（两边都有自动判定结果）")
    if excluded:
        print(f"- 未进配对: {'；'.join(excluded)}")
    if only_a or only_b:
        print(f"- 单边存在不配对: 仅A {','.join(only_a) or '-'} | 仅B {','.join(only_b) or '-'}")
    if not paired:
        raise SystemExit("没有任何可配对的自动判定题，无法做翻转分析")

    both_pass = [q for q, a, b in paired if a and b]
    both_fail = [q for q, a, b in paired if not a and not b]
    regressions = [q for q, a, b in paired if a and not b]   # A对B错
    improvements = [q for q, a, b in paired if not a and b]  # A错B对

    print(f"\n{'qid':6} {'类别':12} {'A':5} {'B':5} 配对分类")
    tag = {(True, True): "同对", (False, False): "同错",
           (True, False): "A对B错(regression)", (False, True): "A错B对(improvement)"}
    for qid, verdict_a, verdict_b in paired:
        cat = str(records_a[qid].get("cat", "?"))
        print(f"{qid:6} {cat:12} {'PASS' if verdict_a else 'FAIL':5} "
              f"{'PASS' if verdict_b else 'FAIL':5} {tag[(verdict_a, verdict_b)]}")

    b_count = len(regressions)
    c_count = len(improvements)
    flips = b_count + c_count
    print("\n## 汇总")
    print(f"- 同对 {len(both_pass)} / 同错 {len(both_fail)}"
          + (f"（同错题 {','.join(both_fail)}：全配置同挂多为能力边界，翻转检验不覆盖）"
             if both_fail else ""))
    print(f"- A对B错(regression): {b_count}" + (f" —— {','.join(regressions)}" if regressions else ""))
    print(f"- A错B对(improvement): {c_count}" + (f" —— {','.join(improvements)}" if improvements else ""))
    print(f"- 翻转数 n = b + c = {flips}")

    print("\n## 分维度翻转（维度行仅定位差异所在，统计资格只看全局 n）")
    dim_cells: dict[str, list[int]] = {}  # 维度 -> [同对, 同错, A对B错, A错B对]
    cell_index = {(True, True): 0, (False, False): 1, (True, False): 2, (False, True): 3}
    for qid, verdict_a, verdict_b in paired:
        dim_cells.setdefault(dim_of(qid), [0, 0, 0, 0])[cell_index[(verdict_a, verdict_b)]] += 1
    for dim, (same_pass, same_fail, reg, imp) in sorted(dim_cells.items()):
        print(f"- {dim}: 同对{same_pass} 同错{same_fail} A对B错{reg} A错B对{imp}")

    print("\n## 结论")
    if flips == 0:
        print(f"无差异：配对 {len(paired)} 题全部同判"
              f"（同对 {len(both_pass)} / 同错 {len(both_fail)}），未观察到任何翻转。")
    elif flips < MIN_FLIPS:
        print(f"翻转存在但无统计资格：翻转数不足，差异无统计资格（±少量题=噪声）。"
              f"n={flips} (<{MIN_FLIPS}) 在双侧精确 McNemar 下不可能达到 p<{ALPHA}；"
              "合法表述是「本轮未观察到有统计资格的差异」。")
    else:
        p_value = mcnemar_exact_p(b_count, c_count)
        if p_value < ALPHA:
            direction = (f"B({args.groupB}) 相对 A({args.groupA}) "
                         + ("退步" if b_count > c_count else "进步"))
            print(f"显著差异 (p<{ALPHA})：双侧精确 McNemar p={p_value:.4g}，"
                  f"翻转 n={flips}（A对B错 {b_count} / A错B对 {c_count}），方向：{direction}。")
        else:
            print(f"翻转存在但无统计资格：翻转 n={flips}"
                  f"（A对B错 {b_count} / A错B对 {c_count}），双侧精确 McNemar "
                  f"p={p_value:.4g} ≥ {ALPHA}，两组不可分辨；"
                  "合法表述是「本轮未观察到有统计资格的差异」。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
