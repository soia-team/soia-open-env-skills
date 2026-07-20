#!/usr/bin/env python3
"""Validate a portable readiness summary without reading private machine data."""

from __future__ import annotations

import json
import sys
from datetime import datetime
from typing import Any


REQUIRED = {"schema_version", "checked_at", "os", "arch", "shell", "tools", "network", "blockers", "next_handoff"}
TOOL_NAMES = {"node", "python", "codex", "workbuddy"}
STATUSES = {"ready", "missing", "update_available", "blocked"}


def timezone_aware_rfc3339(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return False
    return parsed.tzinfo is not None and parsed.utcoffset() is not None


def validate(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, dict):
        return ["summary must be a JSON object"]
    missing = REQUIRED - set(value)
    errors.extend(f"missing field: {name}" for name in sorted(missing))
    if value.get("schema_version") != 2:
        errors.append("schema_version must be 2")
    if not timezone_aware_rfc3339(value.get("checked_at")):
        errors.append("checked_at must be RFC3339 with an explicit timezone")
    tools = value.get("tools")
    if not isinstance(tools, dict):
        errors.append("tools must be an object")
    else:
        for name in sorted(TOOL_NAMES):
            item = tools.get(name)
            if not isinstance(item, dict):
                errors.append(f"tools.{name} must be an object")
            elif item.get("status") not in STATUSES:
                errors.append(f"tools.{name}.status must be one of {sorted(STATUSES)}")
    network = value.get("network")
    if not isinstance(network, dict) or network.get("status") not in {"ready", "degraded", "blocked"}:
        errors.append("network.status must be ready, degraded, or blocked")
    if not isinstance(value.get("blockers"), list):
        errors.append("blockers must be a list")
    return errors


def main() -> int:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(json.dumps({"valid": False, "errors": [f"invalid JSON: {exc.msg}"]}, ensure_ascii=False))
        return 2
    errors = validate(data)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
