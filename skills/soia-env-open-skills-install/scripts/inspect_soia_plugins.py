#!/usr/bin/env python3
"""
检查各宿主的 SOIA 市场接入状态与已安装插件列表。
输出 JSON（--json）或人类可读表格。
"""

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone


SOIA_MARKET = "soia-team/soia-open-skills"
SOIA_DOMAINS = [
    "soia-meta",
    "soia-dev",
    "soia-dev-design",
    "soia-pkm-vault",
    "soia-media-content",
    "soia-cwork-office",
    "soia-env",
    "soia-edu-course",
]


def _run(cmd: list[str]) -> tuple[int, str, str]:
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return r.returncode, r.stdout.strip(), r.stderr.strip()
    except FileNotFoundError:
        return -1, "", f"{cmd[0]}: command not found"
    except subprocess.TimeoutExpired:
        return -1, "", f"{cmd[0]}: timeout"


def check_claude() -> dict:
    if not shutil.which("claude"):
        return {"available": False, "reason": "claude not found"}
    code, out, _ = _run(["claude", "plugin", "list"])
    if code != 0:
        return {"available": True, "market_connected": False, "plugins": []}
    lines = out.splitlines()
    plugins = []
    for line in lines:
        for d in SOIA_DOMAINS:
            if f"{d}@soia" in line:
                parts = line.split()
                version = next((p for p in parts if p.startswith("Version:")), "")
                plugins.append({"name": d, "version": version.replace("Version:", "").strip()})
    market_connected = any(f"@soia" in l for l in lines)
    return {"available": True, "market_connected": market_connected, "plugins": plugins}


def check_codex() -> dict:
    if not shutil.which("codex"):
        return {"available": False, "reason": "codex not found"}
    code, out, _ = _run(["codex", "plugin", "list"])
    if code != 0:
        return {"available": True, "market_connected": False, "plugins": []}
    lines = out.splitlines()
    plugins = []
    for line in lines:
        for d in SOIA_DOMAINS:
            if f"{d}@soia" in line:
                plugins.append({"name": d, "version": ""})
    market_connected = any("@soia" in l for l in lines)
    return {"available": True, "market_connected": market_connected, "plugins": plugins}


def check_workbuddy() -> dict:
    import pathlib
    wb_path = pathlib.Path.home() / "Library/Application Support/WorkBuddy/my-experts"
    if not wb_path.exists():
        return {"available": False, "reason": "WorkBuddy my-experts directory not found"}
    installed = [p.name for p in wb_path.iterdir() if p.is_dir()]
    return {"available": True, "experts": installed}


def main():
    parser = argparse.ArgumentParser(description="Inspect SOIA plugin status across hosts")
    parser.add_argument("--json", action="store_true", help="Output JSON")
    args = parser.parse_args()

    result = {
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "hosts": {
            "claude": check_claude(),
            "codex": check_codex(),
            "workbuddy": check_workbuddy(),
        },
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    for host, info in result["hosts"].items():
        if not info.get("available"):
            print(f"{host}: 不可用 — {info.get('reason', '')}")
            continue
        if host == "workbuddy":
            experts = info.get("experts", [])
            print(f"workbuddy: 可用，已安装专家 {len(experts)} 个")
        else:
            plugins = info.get("plugins", [])
            market = "已接入" if info.get("market_connected") else "未接入"
            print(f"{host}: 可用，市场 {market}，已装域插件 {len(plugins)} 个")
            for p in plugins:
                print(f"  {p['name']} {p['version']}")


if __name__ == "__main__":
    main()
