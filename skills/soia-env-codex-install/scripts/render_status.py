#!/usr/bin/env python3
"""Render the customer-facing Codex CLI status as a fixed Markdown table."""

from __future__ import annotations

import argparse


HEADERS = ("技能", "当前状态", "当前版本", "最新版本", "运行状态", "处理结果")


def clean(value: str) -> str:
    return " ".join(value.replace("|", "／").split())


def version(value: str) -> str:
    value = clean(value)
    return value if value in {"未取得", "-"} else f"`{value}`"


def render(
    current_status: str,
    current_version: str,
    latest_version: str,
    runtime_status: str,
    result: str,
) -> str:
    row = (
        "Codex CLI",
        clean(current_status),
        version(current_version),
        version(latest_version),
        clean(runtime_status),
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
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    print(
        render(
            args.current_status,
            args.current_version,
            args.latest_version,
            args.runtime_status,
            args.result,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
