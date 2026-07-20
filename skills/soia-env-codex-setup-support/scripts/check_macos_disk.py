#!/usr/bin/env python3
"""Parse selected smartctl output without executing privileged commands."""

from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any


HEALTH_RE = re.compile(
    r"(?:SMART overall-health[^:]*|SMART Health Status)\s*:\s*(\S+)",
    re.IGNORECASE,
)
PERCENTAGE_USED_RE = re.compile(r"Percentage Used\s*:\s*(\d+)\s*%", re.IGNORECASE)
AVAILABLE_SPARE_RE = re.compile(r"Available Spare\s*:\s*(\d+)\s*%", re.IGNORECASE)
WRITTEN_RE = re.compile(r"Data Units Written\s*:\s*(.+?)\s*$", re.IGNORECASE)
TEMPERATURE_RE = re.compile(
    r"Temperature(?:\s+Sensor\s+\d+)?\s*:\s*(-?\d+)\s*(?:Celsius|C)\b",
    re.IGNORECASE,
)


def analyze(text: str, device: str | None = None) -> dict[str, Any]:
    """Return a safe, small summary from already-filtered smartctl text."""

    result: dict[str, Any] = {
        "device": device or "unknown",
        "overall_health": None,
        "percentage_used": None,
        "available_spare": None,
        "data_units_written": None,
        "temperature_c": None,
        "warnings": [],
        "status": "unsupported_or_incomplete",
    }

    for line in text.splitlines():
        if result["overall_health"] is None:
            health = HEALTH_RE.search(line)
            if health:
                result["overall_health"] = health.group(1).upper()
        if result["percentage_used"] is None:
            used = PERCENTAGE_USED_RE.search(line)
            if used:
                result["percentage_used"] = int(used.group(1))
        if result["available_spare"] is None:
            spare = AVAILABLE_SPARE_RE.search(line)
            if spare:
                result["available_spare"] = int(spare.group(1))
        if result["data_units_written"] is None:
            written = WRITTEN_RE.search(line)
            if written:
                result["data_units_written"] = written.group(1).strip()
        if result["temperature_c"] is None:
            temperature = TEMPERATURE_RE.search(line)
            if temperature:
                result["temperature_c"] = int(temperature.group(1))

    warnings: list[str] = []
    health = result["overall_health"]
    if health and health not in {"PASSED", "OK", "PASS"}:
        warnings.append("smart_health_not_passed")
    used = result["percentage_used"]
    if used is not None and used >= 90:
        warnings.append("percentage_used_high")
    spare = result["available_spare"]
    if spare is not None and spare < 10:
        warnings.append("available_spare_low")
    temperature = result["temperature_c"]
    if temperature is not None and temperature >= 70:
        warnings.append("temperature_high")

    recognized = any(
        result[key] is not None
        for key in (
            "overall_health",
            "percentage_used",
            "available_spare",
            "data_units_written",
            "temperature_c",
        )
    )
    if recognized:
        result["status"] = "warning" if warnings else "observed"
    result["warnings"] = warnings
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stdin", action="store_true", help="read selected smartctl output from stdin")
    parser.add_argument("--input", help="read selected smartctl output from a local file")
    parser.add_argument("--device", help="device label to include in the summary")
    parser.add_argument("--json", action="store_true", help="emit JSON instead of a short text summary")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.stdin and args.input:
        print("choose only one of --stdin or --input", file=sys.stderr)
        return 2
    if args.input:
        with open(args.input, encoding="utf-8") as handle:
            text = handle.read()
    elif args.stdin:
        text = sys.stdin.read()
    else:
        print("provide --stdin or --input", file=sys.stderr)
        return 2

    result = analyze(text, args.device)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"status={result['status']} device={result['device']} warnings={','.join(result['warnings']) or 'none'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
