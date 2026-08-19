#!/usr/bin/env python3
"""只读环境检查：芯片/内存/磁盘/OS 事实 + 推理引擎与辅助工具盘点。

用法: python3 env_check.py [--json]
只跑固定白名单命令（macOS 上的 sysctl），其余全部来自标准库探测；
不安装、不下载、不改任何配置，输出不含用户绝对路径。
引擎推荐结论不在本脚本里：脚本报事实，选型对照 references/engines.md 由 Agent 给出。
提示：mlx-lm / vLLM 按「当前解释器」探测——装在 venv 里时请用该 venv 的
python3 运行本脚本（如 <venv>/bin/python3 scripts/env_check.py）。
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path

import bench_common as bc


def _sysctl(name: str) -> str | None:
    """macOS 专用，固定参数白名单调用。"""
    try:
        proc = subprocess.run(["sysctl", "-n", name],
                              capture_output=True, text=True, timeout=5)
        value = proc.stdout.strip()
        return value or None
    except Exception:
        return None


def _module_version(module: str, dist: str) -> tuple[bool, str | None]:
    if importlib.util.find_spec(module) is None:
        return False, None
    try:
        from importlib.metadata import version
        return True, version(dist)
    except Exception:
        return True, "unknown"


def host_facts() -> dict:
    system = platform.system()
    facts: dict = {
        "os": system,
        "os_release": platform.release(),
        "arch": platform.machine(),
        "python": platform.python_version(),
        "apple_silicon": system == "Darwin" and platform.machine() == "arm64",
    }
    if system == "Darwin":
        facts["chip"] = _sysctl("machdep.cpu.brand_string")
        mem = _sysctl("hw.memsize")
        facts["memory_gb"] = round(int(mem) / 1024 ** 3) if mem and mem.isdigit() else None
        cores = _sysctl("hw.ncpu")
        facts["cpu_cores"] = int(cores) if cores and cores.isdigit() else None
    else:
        facts["chip"] = platform.processor() or None
        facts["memory_gb"] = None
        facts["cpu_cores"] = None
    usage = shutil.disk_usage(str(Path.home()))
    facts["disk_total_gb"] = round(usage.total / 1024 ** 3)
    facts["disk_free_gb"] = round(usage.free / 1024 ** 3)
    return facts


def engine_inventory() -> list[dict]:
    engines: list[dict] = []

    present, version = _module_version("mlx_lm", "mlx-lm")
    engines.append({"name": "mlx-lm", "status": "installed" if present else "absent",
                    "detail": f"python 包 {version}" if present else "当前解释器未装（venv 里装的话用该 venv 的 python3 重跑）"})

    llama_server = shutil.which("llama-server")
    llama_cli = shutil.which("llama-cli")
    engines.append({"name": "llama.cpp",
                    "status": "installed" if (llama_server or llama_cli) else "absent",
                    "detail": "llama-server 可用" if llama_server
                    else ("仅 llama-cli" if llama_cli else "未发现 llama-server / llama-cli")})

    engines.append({"name": "Ollama", "status": "installed" if shutil.which("ollama") else "absent",
                    "detail": "ollama 命令可用" if shutil.which("ollama") else "未发现 ollama 命令"})

    vllm_present, vllm_version = _module_version("vllm", "vllm")
    engines.append({"name": "vLLM", "status": "installed" if vllm_present else "absent",
                    "detail": f"python 包 {vllm_version}" if vllm_present else "当前解释器未装"})

    lms = shutil.which("lms")
    lm_app = False
    if sys.platform.startswith("darwin"):
        lm_app = (Path("/Applications/LM Studio.app").exists()
                  or (Path.home() / "Applications" / "LM Studio.app").exists())
    engines.append({"name": "LM Studio", "status": "installed" if (lms or lm_app) else "absent",
                    "detail": "应用或 lms CLI 可用" if (lms or lm_app) else "未发现应用与 lms CLI"})

    engines.append({"name": "oMLX", "status": "installed" if shutil.which("omlx") else "absent",
                    "detail": "omlx 命令可用" if shutil.which("omlx") else "未发现 omlx 命令"})
    return engines


def helper_inventory() -> list[dict]:
    helpers = []
    for command, purpose in (
        ("aria2c", "多连接下载模型权重（强烈推荐）"),
        ("node", "题库 node_snippet 判定 harness"),
        ("git", "Agent 集成沙盒 reset"),
        ("curl", "端点连通性手工排查"),
    ):
        helpers.append({"name": command, "purpose": purpose,
                        "status": "installed" if shutil.which(command) else "absent"})
    try:
        import yaml  # noqa: F401
        yaml_ok = True
    except ImportError:
        yaml_ok = False
    helpers.append({"name": "PyYAML", "purpose": "题库/配置 yaml 解析",
                    "status": "installed" if yaml_ok else "absent"})
    return helpers


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--json", action="store_true", help="输出机器可读 JSON")
    args = parser.parse_args()

    report = {
        "host": host_facts(),
        "engines": engine_inventory(),
        "helpers": helper_inventory(),
        "checked_at": bc.now_rfc3339(),
    }
    if not report["host"]["apple_silicon"]:
        report["note"] = "本技能首版只在 Apple Silicon macOS 实测；当前平台仅报告事实，不给引擎推荐"

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0

    host = report["host"]
    print(f"主机: {host['os']} {host['os_release']} / {host['arch']}"
          f"{' / ' + host['chip'] if host.get('chip') else ''}")
    print(f"内存: {host['memory_gb']} GB | 磁盘剩余: {host['disk_free_gb']} / "
          f"{host['disk_total_gb']} GB | CPU 核心: {host['cpu_cores']}")
    print("\n推理引擎:")
    for engine in report["engines"]:
        print(f"  {'[有]' if engine['status'] == 'installed' else '[无]'} "
              f"{engine['name']:10} {engine['detail']}")
    print("\n辅助工具:")
    for helper in report["helpers"]:
        print(f"  {'[有]' if helper['status'] == 'installed' else '[无]'} "
              f"{helper['name']:8} {helper['purpose']}")
    if report.get("note"):
        print(f"\n注意: {report['note']}")
    print(f"\n更新时间: {report['checked_at']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
