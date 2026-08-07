#!/usr/bin/env python3
"""Read-only local runtime inventory with secret-free, machine-readable output.

只读盘点本机脚本运行时，并推导「哪些 AI CLI 现在就能装」。
只执行固定白名单里的版本查询命令，不接受任意命令，不做任何安装或改配置。
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime

CATEGORIES = {
    "node": "Node.js 运行时",
    "python": "Python 运行时",
    "rust": "Rust 工具链",
    "go": "Go 工具链",
    "jvm": "JVM 运行时",
    "system": "系统与包管理器",
    "shell": "Shell",
}

# 版本参数逐个实测确定，不能统一写 `--version`：
#   go   `go --version` 退出码 2（flag provided but not defined），只认 `go version`
#   unzip 没有长参数，只认 `-v`
#   java  版本写进 stderr，stdout 为空（由 stdout→stderr 回退兜住）
#   rustc 是指向 rustup 的 shim，冷启动可能超过 10s——超时不等于缺失
RUNTIMES: tuple[tuple[str, str, tuple[str, ...]], ...] = (
    ("node", "node", ("--version",)),
    ("npm", "node", ("--version",)),
    ("npx", "node", ("--version",)),
    ("pnpm", "node", ("--version",)),
    ("yarn", "node", ("--version",)),
    ("bun", "node", ("--version",)),
    ("python3", "python", ("--version",)),
    ("pip3", "python", ("--version",)),
    ("uv", "python", ("--version",)),
    ("pipx", "python", ("--version",)),
    ("rustc", "rust", ("--version",)),
    ("cargo", "rust", ("--version",)),
    ("rustup", "rust", ("--version",)),
    ("go", "go", ("version",)),
    ("java", "jvm", ("-version",)),
    ("brew", "system", ("--version",)),
    ("git", "system", ("--version",)),
    ("curl", "system", ("--version",)),
    ("wget", "system", ("--version",)),
    ("unzip", "system", ("-v",)),
    ("tar", "system", ("--version",)),
    ("bash", "shell", ("--version",)),
    ("zsh", "shell", ("--version",)),
)

# 渠道依赖取自本仓各安装技能 SKILL.md 的「依赖与安装」表；
# Node 版本门槛取自各技能 references/official-sources.md 的「已核对事实」段。
# 上游改了要同步这里，别在这里凭印象填版本号。
# 关键事实：多数 AI CLI 有官方独立安装渠道，并不强依赖 Node.js；
# 只有 Pi 与 Deep Code 把 soia-env-node-install 列为 hard 依赖。
# 门槛为 None 表示「仓内尚未核对到具体版本」，不表示「没有要求」——见 runtimes.md。
AI_CLIS: tuple[dict[str, object], ...] = (
    {"name": "Claude Code", "source": "soia-env-claude-cli-install",
     # official-sources.md：@anthropic-ai/claude-code 当前包声明 Node.js 22 或更高
     "channels": (("官方独立安装", ()), ("npm 全局安装", (("node", "22"), ("npm", None))))},
    {"name": "Codex CLI", "source": "soia-env-codex-install",
     # official-sources.md 明确「Node 版本要求以官方页面与实际 codex --help 为准」，不写死
     "channels": (("官方独立安装", ()), ("Homebrew", (("brew", None),)),
                  ("npm 全局安装", (("node", None), ("npm", None))))},
    {"name": "Kimi Code CLI", "source": "soia-env-kimi-cli-install",
     # official-sources.md：@moonshot-ai/kimi-code 当前包声明 Node.js 22.19 或更高
     "channels": (("官方独立安装", ()), ("npm 全局安装", (("node", "22.19"), ("npm", None))))},
    {"name": "Qoder CLI", "source": "soia-env-qoder-cli-install",
     # official-sources.md：@qoder-ai/qodercli 当前包声明 Node.js 20 或更高
     "channels": (("官方独立安装", ()), ("Homebrew", (("brew", None),)),
                  ("npm 全局安装", (("node", "20"), ("npm", None))))},
    {"name": "OpenCode CLI", "source": "soia-env-opencode-cli-install",
     "channels": (("官方独立安装", ()), ("Homebrew", (("brew", None),)),
                  ("npm 全局安装", (("node", None), ("npm", None))))},
    {"name": "Antigravity CLI", "source": "soia-env-antigravity-cli-install",
     "channels": (("官方独立安装", ()),)},
    {"name": "WorkBuddy", "source": "soia-env-workbuddy-install",
     "channels": (("官方桌面安装包", ()),)},
    {"name": "Pi", "source": "soia-env-pi-cli-install",
     "channels": (("npm 全局安装", (("node", None), ("npm", None))),)},
    {"name": "Deep Code CLI", "source": "soia-env-deepcode-cli-install",
     # official-sources.md：@vegamo/deepcode-cli 要求 Node.js 22 或更高
     "channels": (("npm 全局安装", (("node", "22"), ("npm", None))),)},
)

_VERSION_DOTTED = re.compile(r"\d+(?:\.\d+)+")
_VERSION_BARE = re.compile(r"\d+")


def now_rfc3339() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def platform_info() -> dict[str, str]:
    """OS 与架构只作为事实上报，本技能不判断某个 CLI 是否支持该平台。

    多个安装技能把「官方支持的操作系统/架构」列为强依赖，但支持矩阵在各家官方
    清单里（例如 Antigravity 由自己的 check_latest.py 实时拉取），仓内没有静态真源。
    在这里编一张矩阵等于造事实，所以只提供 os/arch 供下游安装技能自行判断。
    """
    system = (platform.system() or "unknown").lower()
    if system == "darwin":
        version = platform.mac_ver()[0] or platform.release()
    elif system == "windows":
        version = platform.win32_ver()[0] or platform.release()
    else:
        version = platform.release()
    return {"os": system, "arch": platform.machine() or "unknown", "os_version": version or "unknown"}


def sanitized_path(path: str) -> str:
    """把 home 折成 ~，不回显客户私有绝对路径。"""
    home = os.path.expanduser("~")
    if home and path.startswith(home):
        return "~" + path[len(home):]
    return path


def extract_version(text: str) -> str | None:
    """只取首行里的版本号：输出可能被本地化（中文 wget/bash），不能匹配英文关键词。"""
    head = text.splitlines()[0] if text else ""
    match = _VERSION_DOTTED.search(head) or _VERSION_BARE.search(head)
    return match.group(0) if match else None


def version_tuple(version: str) -> tuple[int, ...]:
    return tuple(int(part) for part in version.split(".") if part.isdigit())


def version_at_least(actual: str, minimum: str) -> bool:
    return version_tuple(actual) >= version_tuple(minimum)


def detect(name: str, category: str, args: tuple[str, ...], timeout: float) -> dict[str, object]:
    base: dict[str, object] = {"name": name, "category": category, "probe": " ".join((name, *args))}
    path = shutil.which(name)
    if not path:
        return {**base, "status": "absent", "version": None}
    started = time.monotonic()
    try:
        run = subprocess.run([path, *args], capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        # rustc 这类 shim 冷启动会超时；这是「查不到版本」，不是「没装」。
        return {**base, "status": "timeout", "version": None, "path": sanitized_path(path),
                "elapsed_ms": round((time.monotonic() - started) * 1000)}
    except OSError:
        return {**base, "status": "exec_failed", "version": None, "path": sanitized_path(path)}
    elapsed_ms = round((time.monotonic() - started) * 1000)
    # java 把版本写进 stderr；stdout 为空才回退，避免读到 rustup 的 info 噪音。
    text = (run.stdout or "").strip() or (run.stderr or "").strip()
    version = extract_version(text)
    if version is not None:
        status = "available"
    elif run.returncode == 0:
        status = "version_unreadable"
    else:
        status = "exec_failed"
    # 只保留版本号：pip3 的原始输出带 site-packages 绝对路径，正文一律不落盘。
    return {**base, "status": status, "version": version, "path": sanitized_path(path),
            "elapsed_ms": elapsed_ms}


def inventory(selected: tuple[tuple[str, str, tuple[str, ...]], ...], timeout: float) -> list[dict[str, object]]:
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(detect, name, category, args, timeout) for name, category, args in selected]
        return [future.result() for future in futures]


def installability(results: list[dict[str, object]]) -> list[dict[str, object]]:
    found = {item["name"]: item for item in results}
    report: list[dict[str, object]] = []
    for cli in AI_CLIS:
        channels: list[dict[str, object]] = []
        for label, requires in cli["channels"]:  # type: ignore[index]
            missing: list[str] = []
            uncertain: list[str] = []
            for runtime, minimum in requires:
                item = found.get(runtime)
                if item is None or item["status"] == "absent":
                    missing.append(f"缺 {runtime}")
                elif item["status"] == "timeout":
                    uncertain.append(f"{runtime} 版本查询超时")
                elif item["status"] != "available":
                    missing.append(f"{runtime} 不可用")
                elif minimum and not version_at_least(str(item["version"]), minimum):
                    missing.append(f"{runtime} {item['version']} < {minimum}")
            status = "blocked" if missing else "uncertain" if uncertain else "ok"
            channels.append({"label": label, "status": status, "blockers": missing + uncertain})
        if any(channel["status"] == "ok" for channel in channels):
            verdict = "可安装"
        elif any(channel["status"] == "uncertain" for channel in channels):
            verdict = "待复核"
        else:
            verdict = "被阻塞"
        report.append({"name": cli["name"], "source": cli["source"], "verdict": verdict, "channels": channels})
    return report


MARKS = {"available": "✓", "absent": "✗", "timeout": "?", "exec_failed": "!", "version_unreadable": "!"}
LABELS = {"absent": "未安装", "timeout": "版本查询超时（不等于未安装，放宽 --timeout 复核）",
          "exec_failed": "执行失败", "version_unreadable": "版本无法解析"}


def render(results: list[dict[str, object]], report: list[dict[str, object]], timeout: float) -> None:
    host = platform_info()
    print(f"运行时盘点（{host['os']} {host['os_version']} / {host['arch']}，"
          f"timeout={timeout}s，{now_rfc3339()}）")
    for key, title in CATEGORIES.items():
        rows = [item for item in results if item["category"] == key]
        if not rows:
            continue
        print(f"\n{title}")
        for item in rows:
            mark = MARKS.get(str(item["status"]), "?")
            detail = item["version"] if item["status"] == "available" else LABELS.get(str(item["status"]), "")
            print(f"  {mark} {item['name']:<9} {detail}")
    print("\n可安装性推导（渠道依赖取自本仓各安装技能）")
    for entry in report:
        ok = [channel["label"] for channel in entry["channels"] if channel["status"] == "ok"]  # type: ignore[index]
        if ok:
            print(f"  ✓ {entry['name']:<16} {'、'.join(ok)}")
        else:
            reasons = "；".join(
                f"{channel['label']}：{'、'.join(channel['blockers'])}"  # type: ignore[index]
                for channel in entry["channels"]  # type: ignore[index]
            )
            print(f"  ✗ {entry['name']:<16} {entry['verdict']} — {reasons}")


def main() -> int:
    names = {name for name, _, _ in RUNTIMES}
    parser = argparse.ArgumentParser(description="Inventory local runtimes without changing anything")
    parser.add_argument("--only", action="append", choices=sorted(names), help="只探测指定运行时；可重复")
    parser.add_argument("--category", action="append", choices=sorted(CATEGORIES), help="只探测指定类别；可重复")
    parser.add_argument("--timeout", type=float, default=10.0)
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args()

    selected = tuple(
        entry for entry in RUNTIMES
        if (not args.only or entry[0] in args.only) and (not args.category or entry[1] in args.category)
    )
    if not selected:
        print("没有匹配的运行时", file=sys.stderr)
        return 2

    timeout = max(0.1, args.timeout)
    results = inventory(selected, timeout)
    report = installability(results)
    if args.json:
        print(json.dumps({"checked_at": now_rfc3339(), "timeout_s": timeout,
                          "host": platform_info(), "runtimes": results,
                          "installable": report}, ensure_ascii=False))
    else:
        render(results, report, timeout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
