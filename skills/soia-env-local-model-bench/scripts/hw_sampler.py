#!/usr/bin/env python3
"""硬件指标采样器：按固定间隔记录目标进程 RSS/CPU% 与 GPU 利用率（macOS）。

用法: python3 hw_sampler.py <label> <pid> [--interval 2] [--workdir <dir>]
输出: <workdir>/results/hw_<label>.jsonl；目标进程退出即自动停止，Ctrl-C 手动停。
只读采样：只跑固定白名单命令（ps / ioreg），不接受任意命令注入。
GPU 利用率来自 IOAccelerator 的 Device Utilization（仅 macOS；其他平台记 null）。
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import time

import bench_common as bc


def gpu_util():
    if not sys.platform.startswith("darwin"):
        return None
    try:
        output = subprocess.run(
            ["ioreg", "-r", "-d", "1", "-w", "0", "-c", "IOAccelerator"],
            capture_output=True, text=True, timeout=5).stdout
        match = re.search(r'"Device Utilization %"=(\d+)', output)
        return int(match.group(1)) if match else None
    except Exception:
        return None


def proc_stat(pid: str):
    try:
        output = subprocess.run(["ps", "-o", "rss=,%cpu=", "-p", pid],
                                capture_output=True, text=True, timeout=5).stdout.strip()
        if not output:
            return None, None
        rss_kb, cpu = output.split()
        return round(int(rss_kb) / 1024 / 1024, 2), float(cpu)
    except Exception:
        return None, None


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("label", help="结果标签")
    parser.add_argument("pid", help="被采样进程 pid（如推理引擎服务进程）")
    parser.add_argument("--interval", type=float, default=2.0, help="采样间隔秒，默认 2")
    parser.add_argument("--workdir", help="结果目录，默认 ~/local-model-bench")
    parser.add_argument("--config", help="非秘密配置文件路径")
    args = parser.parse_args()

    config, _ = bc.load_config(args.config)
    resdir = bc.resolve_workdir(args.workdir, config) / "results"
    resdir.mkdir(parents=True, exist_ok=True)
    out = resdir / f"hw_{args.label}.jsonl"
    print(f"采样中 -> {bc.fold_home(str(out))}（进程退出或 Ctrl-C 停止）", flush=True)

    with out.open("a", encoding="utf-8") as handle:
        while True:
            rss, cpu = proc_stat(args.pid)
            if rss is None:
                print("目标进程已退出，采样停止", flush=True)
                break
            record = {"ts": round(time.time(), 1), "rss_gb": rss,
                      "cpu_pct": cpu, "gpu_pct": gpu_util()}
            handle.write(json.dumps(record) + "\n")
            handle.flush()
            time.sleep(args.interval)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
