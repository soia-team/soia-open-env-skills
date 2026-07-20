#!/usr/bin/env python3
"""Read-only detection of the ChatGPT desktop app that hosts Codex on macOS."""

from __future__ import annotations

import argparse
import json
import os
import platform
import subprocess
from pathlib import Path
from typing import Any


EXPECTED_BUNDLE_ID = "com.openai.codex"


def summarize(
    *,
    exists: bool,
    bundle_id: str | None,
    version: str | None,
    signature_ok: bool | None,
    location: str,
) -> dict[str, Any]:
    """Classify metadata supplied by the platform probes."""

    result: dict[str, Any] = {
        "application": "ChatGPT.app (Codex host)",
        "location": location,
        "bundle_id": bundle_id,
        "version": version,
        "signature": "valid" if signature_ok is True else "invalid" if signature_ok is False else "not_checked",
        "status": "missing",
        "warnings": [],
    }
    if not exists:
        return result
    if bundle_id != EXPECTED_BUNDLE_ID:
        result["status"] = "unexpected_bundle"
        result["warnings"] = ["bundle_id_is_not_com_openai_codex"]
        return result
    if signature_ok is False:
        result["status"] = "invalid_signature"
        result["warnings"] = ["codesign_verification_failed"]
        return result
    if signature_ok is None:
        result["status"] = "signature_unverified"
        result["warnings"] = ["codesign_not_checked"]
        return result
    result["status"] = "ready"
    if not version:
        result["warnings"] = ["version_unavailable"]
    return result


def _run(command: list[str]) -> tuple[str | None, bool | None]:
    try:
        completed = subprocess.run(command, capture_output=True, text=True, timeout=5, check=False)
    except (OSError, subprocess.TimeoutExpired):
        return None, None
    return completed.stdout.strip() or None, completed.returncode == 0


def _mdls(path: Path, field: str) -> str | None:
    value, _ = _run(["mdls", "-raw", "-name", field, str(path)])
    if value in {None, "", "(null)"}:
        return None
    return value.strip('"')


def _signature(path: Path) -> bool | None:
    _, ok = _run(["codesign", "--verify", "--deep", "--strict", str(path)])
    return ok


def _location(path: Path) -> str:
    home_apps = Path.home() / "Applications"
    if path == Path("/Applications/ChatGPT.app"):
        return "system_applications"
    if path == home_apps / "ChatGPT.app":
        return "user_applications"
    return "custom"


def inspect(paths: list[Path] | None = None) -> dict[str, Any]:
    if platform.system() != "Darwin":
        return {
            "application": "ChatGPT.app (Codex host)",
            "location": "unsupported_platform",
            "bundle_id": None,
            "version": None,
            "signature": "not_checked",
            "status": "unsupported_platform",
            "warnings": ["macos_bundle_probe_not_applicable"],
        }
    candidates = paths or [Path("/Applications/ChatGPT.app"), Path.home() / "Applications" / "ChatGPT.app"]
    results = []
    for path in candidates:
        result = summarize(
            exists=path.is_dir(),
            bundle_id=_mdls(path, "kMDItemCFBundleIdentifier") if path.is_dir() else None,
            version=_mdls(path, "kMDItemVersion") if path.is_dir() else None,
            signature_ok=_signature(path) if path.is_dir() else None,
            location=_location(path),
        )
        results.append(result)
        if result["status"] == "ready":
            return result
    return next((item for item in results if item["status"] != "missing"), results[0])


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", action="append", help="additional ChatGPT.app path to inspect")
    parser.add_argument("--json", action="store_true", help="emit JSON output")
    args = parser.parse_args()
    paths = [Path(os.path.expanduser(path)) for path in args.path] if args.path else None
    result = inspect(paths)
    if args.json:
        print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    else:
        print(f"status={result['status']} location={result['location']} warnings={','.join(result['warnings']) or 'none'}")
    return 0 if result["status"] == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())
