#!/usr/bin/env python3
"""汇总 hw_<label>.jsonl 采样为峰值/活跃均值。

用法: python3 hw_summary.py [label ...] [--workdir <dir>]
不带 label 时汇总结果目录下全部 hw_*.jsonl。
活跃段定义：GPU>5% 或 CPU>50% 的样本，避免空闲样本稀释均值。
"""

from __future__ import annotations

import argparse
import json

import bench_common as bc


def summarize(path) -> dict | None:
    records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()
               if line.strip()]
    if not records:
        return None
    rss = [r["rss_gb"] for r in records]
    cpu = [r["cpu_pct"] for r in records]
    gpu = [r["gpu_pct"] for r in records if r.get("gpu_pct") is not None]
    active = [r for r in records if (r.get("gpu_pct") or 0) > 5 or r["cpu_pct"] > 50]
    active_gpu = [r["gpu_pct"] for r in active if r.get("gpu_pct") is not None]
    active_cpu = [r["cpu_pct"] for r in active]
    return {
        "samples": len(records),
        "rss_peak_gb": round(max(rss), 1),
        "gpu_peak_pct": max(gpu) if gpu else 0,
        "gpu_active_avg_pct": round(sum(active_gpu) / len(active_gpu)) if active_gpu else 0,
        "cpu_peak_pct": round(max(cpu)),
        "cpu_active_avg_pct": round(sum(active_cpu) / len(active_cpu)) if active_cpu else 0,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("labels", nargs="*", help="要汇总的标签；缺省汇总全部")
    parser.add_argument("--workdir", help="结果目录，默认 ~/local-model-bench")
    parser.add_argument("--config", help="非秘密配置文件路径")
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args()

    config, _ = bc.load_config(args.config)
    resdir = bc.resolve_workdir(args.workdir, config) / "results"
    labels = args.labels or sorted(
        p.name[3:-6] for p in resdir.glob("hw_*.jsonl")) if resdir.is_dir() else []
    results = {}
    for label in labels:
        path = resdir / f"hw_{label}.jsonl"
        if not path.is_file():
            continue
        summary = summarize(path)
        if summary is None:
            continue
        results[label] = summary
        if not args.json:
            print(f"[{label}] 样本{summary['samples']} | RSS 峰值 {summary['rss_peak_gb']}GB | "
                  f"GPU 峰值 {summary['gpu_peak_pct']}% 活跃均值 {summary['gpu_active_avg_pct']}% | "
                  f"CPU 峰值 {summary['cpu_peak_pct']}% 活跃均值 {summary['cpu_active_avg_pct']}%")
    if args.json:
        print(json.dumps({"checked_at": bc.now_rfc3339(), "labels": results},
                         ensure_ascii=False, indent=2))
    elif not results:
        print("没有可汇总的 hw_*.jsonl（先用 hw_sampler.py 采样）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
