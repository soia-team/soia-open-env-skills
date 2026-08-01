#!/usr/bin/env python3
"""
检查各宿主的 SOIA 市场接入状态与已安装插件列表。
输出 JSON（--json）或人类可读表格。
"""

import argparse
import json
import pathlib
import shutil
import subprocess
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
# WorkBuddy 自建专家唯一识别目录（与 install_workbuddy_experts.py 同源）
WORKBUDDY_EXPERTS = pathlib.PurePosixPath(".workbuddy/plugins/marketplaces/my-experts/plugins")


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
    # 输出为块状：插件名行（❯ name@market）后跟若干缩进属性行（Version:/Status:）
    plugins = []
    current = None
    for line in out.splitlines():
        stripped = line.strip()
        for d in SOIA_DOMAINS:
            if f"{d}@soia" in stripped:
                current = {"name": d, "version": ""}
                plugins.append(current)
                break
        else:
            if current and stripped.startswith("Version:"):
                current["version"] = stripped.removeprefix("Version:").strip()
                current = None
            elif "❯" in stripped:
                current = None  # 非 soia 插件块，丢弃其属性行
    return {
        "available": True,
        "market_connected": "@soia" in out,
        "plugins": plugins,
    }


def check_codex() -> dict:
    if not shutil.which("codex"):
        return {"available": False, "reason": "codex not found"}
    code, out, _ = _run(["codex", "plugin", "list"])
    if code != 0:
        return {"available": True, "market_connected": False, "plugins": []}
    # 输出为表格行：<name>@<market>  installed, enabled  <version>  <source>
    plugins = []
    for line in out.splitlines():
        cols = line.split()
        if not cols:
            continue
        for d in SOIA_DOMAINS:
            if cols[0] == f"{d}@soia":
                version = next(
                    (c for c in cols[1:] if c[0].isdigit() and "." in c), "")
                plugins.append({"name": d, "version": version})
    return {
        "available": True,
        "market_connected": any("@soia" in l for l in out.splitlines()),
        "plugins": plugins,
    }


def check_workbuddy() -> dict:
    experts_dir = pathlib.Path.home() / WORKBUDDY_EXPERTS
    if not experts_dir.exists():
        return {"available": False,
                "reason": f"~/{WORKBUDDY_EXPERTS} not found"}
    installed = sorted(p.name for p in experts_dir.iterdir() if p.is_dir())
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
            for e in experts:
                print(f"  {e}")
        else:
            plugins = info.get("plugins", [])
            market = "已接入" if info.get("market_connected") else "未接入"
            print(f"{host}: 可用，市场 {market}，已装域插件 {len(plugins)} 个")
            for p in plugins:
                print(f"  {p['name']} {p['version']}")


if __name__ == "__main__":
    main()
