#!/usr/bin/env python3
"""Render the customer-facing Codex CLI status as a fixed Markdown table."""

from __future__ import annotations

import argparse
from datetime import datetime


HEADERS = (
    "技能",
    "当前状态",
    "当前版本",
    "最新版本",
    "运行状态",
    "安装方式",
    "安装目录",
    "配置文件目录",
    "更新时间",
    "处理结果",
)


def clean(value: str) -> str:
    return " ".join(value.replace("|", "／").split())


def version(value: str) -> str:
    value = clean(value)
    return value if value in {"未取得", "-", "不适用", "随 ChatGPT.app 更新"} else f"`{value}`"


def path(value: str) -> str:
    value = clean(value)
    return value if value in {"未取得", "-", "不适用"} else f"`{value}`"


def now_rfc3339() -> str:
    return datetime.now().astimezone().replace(microsecond=0).isoformat()


def render(
    current_status: str,
    current_version: str,
    latest_version: str,
    runtime_status: str,
    install_method: str,
    install_dir: str,
    config_dir: str,
    result: str,
    updated_at: str | None = None,
) -> str:
    row = (
        "Codex CLI",
        clean(current_status),
        version(current_version),
        version(latest_version),
        clean(runtime_status),
        clean(install_method),
        path(install_dir),
        path(config_dir),
        clean(updated_at or now_rfc3339()),
        clean(result),
    )
    header = "| " + " | ".join(HEADERS) + " |"
    divider = "|" + "|".join("---" for _ in HEADERS) + "|"
    values = "| " + " | ".join(row) + " |"
    return "\n".join((header, divider, values))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-status", required=True)
    parser.add_argument("--current-version", default="未取得")
    parser.add_argument("--latest-version", default="未取得")
    parser.add_argument("--runtime-status", required=True)
    parser.add_argument("--install-method", default="未取得")
    parser.add_argument("--install-dir", default="未取得")
    parser.add_argument("--config-dir", default="未取得")
    parser.add_argument("--updated-at")
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    print(
        render(
            args.current_status,
            args.current_version,
            args.latest_version,
            args.runtime_status,
            args.install_method,
            args.install_dir,
            args.config_dir,
            args.result,
            args.updated_at,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
