#!/usr/bin/env python3
"""Read the latest AI CLI version from an official machine-readable source."""

from __future__ import annotations

import argparse
import json
import platform
import sys
import urllib.parse
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "cli-profile.json"


def now_rfc3339() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    latest = value.get("latest") if isinstance(value, dict) else None
    if not isinstance(latest, dict) or "type" not in latest:
        raise ValueError("latest-version profile is incomplete")
    return value


def platform_key() -> str:
    os_name = {"darwin": "darwin", "linux": "linux"}.get(sys.platform)
    machine = platform.machine().lower()
    arch = "arm64" if machine in {"arm64", "aarch64"} else "amd64" if machine in {"x86_64", "amd64"} else None
    if not os_name or not arch:
        raise ValueError("official Antigravity manifest is unavailable for this platform")
    if os_name == "linux":
        libc_name = platform.libc_ver()[0].lower()
        return f"linux_{arch}_musl" if libc_name == "musl" else f"linux_{arch}"
    return f"darwin_{arch}"


def source_url(latest: dict[str, Any]) -> str:
    kind = latest["type"]
    if kind == "npm":
        package = urllib.parse.quote(str(latest["package"]), safe="")
        return f"https://registry.npmjs.org/{package}/latest"
    if kind == "pypi":
        package = urllib.parse.quote(str(latest["package"]), safe="")
        return f"https://pypi.org/pypi/{package}/json"
    if kind == "github":
        return f"https://api.github.com/repos/{latest['repo']}/releases/latest"
    if kind == "antigravity-manifest":
        return f"{latest['base_url'].rstrip('/')}/manifests/{platform_key()}.json"
    raise ValueError("unsupported latest-version source")


def fetch_json(url: str, *, opener=urllib.request.urlopen) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "soia-open-env-skills"},
    )
    with opener(request, timeout=10) as response:
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise ValueError("latest-version response is not an object")
    return payload


def extract_version(kind: str, payload: dict[str, Any]) -> str:
    if kind in {"npm", "antigravity-manifest"}:
        value = payload.get("version")
    elif kind == "pypi":
        info = payload.get("info")
        value = info.get("version") if isinstance(info, dict) else None
    elif kind == "github":
        value = payload.get("tag_name")
    else:
        value = None
    if not isinstance(value, str) or not value.strip():
        raise ValueError("latest version is missing")
    return value.strip().removeprefix("v")


def check(profile: dict[str, Any] | None = None, *, opener=urllib.request.urlopen) -> dict[str, Any]:
    details = load_profile() if profile is None else profile
    latest = details["latest"]
    url = source_url(latest)
    payload = fetch_json(url, opener=opener)
    return {
        "schema_version": 1,
        "tool": details["display_name"],
        "latest_version": extract_version(str(latest["type"]), payload),
        "source": str(latest["type"]),
        "status": "available",
        "checked_at": now_rfc3339(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = check()
    except Exception as exc:  # Network/parsing failures are reported without provider bodies.
        result = {
            "schema_version": 1,
            "latest_version": "未取得",
            "status": "blocked",
            "error_category": type(exc).__name__,
            "checked_at": now_rfc3339(),
        }
        exit_code = 2
    else:
        exit_code = 0
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(result["latest_version"])
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
