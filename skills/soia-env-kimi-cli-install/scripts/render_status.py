#!/usr/bin/env python3
"""Render the required customer-facing AI CLI status table."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "cli-profile.json"
HEADER = (
    "| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | "
    "安装目录 | 配置文件目录 | 更新时间 | 处理结果 |"
)


def cell(value: str) -> str:
    return " ".join(value.split()).replace("|", "／")


def tool_name() -> str:
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    return str(profile["display_name"])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--current-status", required=True)
    parser.add_argument("--current-version", default="未取得")
    parser.add_argument("--latest-version", default="未取得")
    parser.add_argument("--runtime-status", required=True)
    parser.add_argument("--install-method", default="未取得")
    parser.add_argument("--install-dir", default="未取得")
    parser.add_argument("--config-dir", default="未取得")
    parser.add_argument("--updated-at", required=True)
    parser.add_argument("--result", required=True)
    args = parser.parse_args()
    values = [
        tool_name(),
        args.current_status,
        args.current_version,
        args.latest_version,
        args.runtime_status,
        args.install_method,
        args.install_dir,
        args.config_dir,
        args.updated_at,
        args.result,
    ]
    print(HEADER)
    print("|---|---|---|---|---|---|---|---|---|---|")
    print("| " + " | ".join(cell(value) for value in values) + " |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
