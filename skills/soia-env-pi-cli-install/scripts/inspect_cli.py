#!/usr/bin/env python3
"""Inspect one configured AI CLI without changing the machine."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


PROFILE_PATH = Path(__file__).resolve().parents[1] / "references" / "cli-profile.json"
VERSION_RE = re.compile(r"(?<!\d)v?(\d+(?:\.\d+){1,3}(?:[-+][0-9A-Za-z.-]+)?)")


def now_rfc3339() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def load_profile(path: Path = PROFILE_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    required = {
        "schema_version",
        "display_name",
        "command",
        "version_args",
        "default_config_paths",
        "config_env_vars",
        "known_user_paths",
        "package_ecosystem",
        "package_name",
        "native_installer",
        "latest",
    }
    if not isinstance(value, dict) or not required <= set(value):
        raise ValueError("CLI profile is incomplete")
    if value["schema_version"] != 1:
        raise ValueError("unsupported CLI profile schema")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", str(value["command"])):
        raise ValueError("CLI command is unsafe")
    if not isinstance(value["version_args"], list) or not all(
        isinstance(item, str) and item for item in value["version_args"]
    ):
        raise ValueError("version_args must be a non-empty string list")
    return value


def home_relative(path: Path, home: Path) -> str:
    try:
        return str(Path("~") / path.resolve(strict=False).relative_to(home.resolve(strict=False)))
    except (OSError, ValueError):
        return str(path)


def expand_profile_path(raw: str, *, home: Path, env: dict[str, str]) -> Path | None:
    value = raw.replace("%APPDATA%", env.get("APPDATA", ""))
    value = value.replace("%LOCALAPPDATA%", env.get("LOCALAPPDATA", ""))
    if value.startswith("~/"):
        return home / value[2:]
    if not value or value.startswith("<"):
        return None
    return Path(value).expanduser()


def package_manager_candidates(
    profile: dict[str, Any], *, env: dict[str, str]
) -> list[Path]:
    command = str(profile["command"])
    ecosystem = str(profile["package_ecosystem"])
    candidates: list[Path] = []
    npm = shutil.which("npm", path=env.get("PATH"))
    if ecosystem == "npm" and npm:
        try:
            process = run_executable(Path(npm), ["prefix", "-g"], env=env, timeout=8)
            if process.returncode == 0 and process.stdout.strip():
                prefix = Path(process.stdout.strip())
                candidates.extend(
                    [prefix / "bin" / command, prefix / command, prefix / f"{command}.cmd"]
                )
        except (OSError, subprocess.SubprocessError):
            pass
    return candidates


def run_executable(
    path: Path,
    args: list[str],
    *,
    env: dict[str, str],
    timeout: int = 10,
) -> subprocess.CompletedProcess[str]:
    command = [str(path), *args]
    if os.name == "nt" and path.suffix.lower() in {".cmd", ".bat"}:
        command = [env.get("COMSPEC", "cmd.exe"), "/d", "/s", "/c", str(path), *args]
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        timeout=timeout,
        check=False,
        env=env,
    )


def package_identity(
    profile: dict[str, Any],
    *,
    resolved: Path,
    install_method: str,
    env: dict[str, str],
    home: Path,
) -> tuple[str, str]:
    package = str(profile["package_name"])
    if profile["package_ecosystem"] != "npm" or "npm" not in install_method.lower():
        return "not_applicable", "未取得"
    expected_parts = tuple(part for part in package.split("/") if part)
    resolved_parts = tuple(part.lower() for part in resolved.parts)
    expected_lower = tuple(part.lower() for part in expected_parts)
    for index in range(len(resolved_parts) - len(expected_lower) + 1):
        if resolved_parts[index : index + len(expected_lower)] == expected_lower:
            package_dir = Path(*resolved.parts[: index + len(expected_lower)])
            return "matched", home_relative(package_dir, home)
    npm = shutil.which("npm", path=env.get("PATH"))
    if not npm:
        return "unknown", "未取得"
    try:
        process = run_executable(Path(npm), ["root", "-g"], env=env, timeout=8)
        root = Path(process.stdout.strip()) if process.returncode == 0 else None
        package_dir = root.joinpath(*expected_parts) if root and expected_parts else None
        if package_dir and (package_dir / "package.json").is_file():
            return "matched", home_relative(package_dir, home)
        return "mismatch", "未取得"
    except (OSError, subprocess.SubprocessError):
        return "unknown", "未取得"


def candidate_paths(
    profile: dict[str, Any],
    *,
    env: dict[str, str] | None = None,
    home: Path | None = None,
) -> list[Path]:
    values = dict(os.environ if env is None else env)
    user_home = Path.home() if home is None else home
    command = str(profile["command"])
    paths: list[Path] = []
    active = shutil.which(command, path=values.get("PATH"))
    if active:
        paths.append(Path(active))
    for raw in profile["known_user_paths"]:
        candidate = expand_profile_path(str(raw), home=user_home, env=values)
        if candidate is not None:
            paths.append(candidate)
    paths.extend(package_manager_candidates(profile, env=values))
    unique: list[Path] = []
    seen: set[str] = set()
    for path in paths:
        key = os.path.normcase(str(path))
        if key not in seen:
            seen.add(key)
            unique.append(path)
    return unique


def classify_installation(path: Path, resolved: Path, profile: dict[str, Any]) -> str:
    combined = f"{path} {resolved}".replace("\\", "/").lower()
    ecosystem = str(profile["package_ecosystem"])
    if "/cellar/" in combined or "/homebrew/" in combined:
        return "Homebrew 安装"
    if "node_modules" in combined or "/npm/" in combined:
        return "npm 全局安装"
    if "pipx/venvs" in combined:
        return "pipx 隔离安装"
    if ecosystem == "python" and ("site-packages" in combined or "/venv" in combined):
        return "Python 隔离环境安装"
    if bool(profile["native_installer"]) and "/.local/bin/" in combined:
        return "官方独立安装"
    if ecosystem == "npm":
        return "npm/独立安装（待核对）"
    if ecosystem == "python":
        return "Python 包安装（待核对）"
    return "官方独立安装（待核对）"


def parse_version(output: str) -> str:
    normalized = " ".join(output.split())[:160]
    match = VERSION_RE.search(normalized)
    return match.group(1) if match else (normalized or "未取得")


def config_candidate(
    profile: dict[str, Any], *, env: dict[str, str], home: Path
) -> Path | None:
    for name in profile["config_env_vars"]:
        value = env.get(str(name))
        if value:
            return Path(value).expanduser()
    defaults = profile["default_config_paths"]
    if not defaults:
        return None
    raw = str(defaults[0])
    return expand_profile_path(raw, home=home, env=env)


def config_path(profile: dict[str, Any], *, env: dict[str, str], home: Path) -> str:
    candidate = config_candidate(profile, env=env, home=home)
    if candidate is None:
        return "未取得"
    return home_relative(candidate, home)


def config_observation(
    profile: dict[str, Any], *, env: dict[str, str], home: Path
) -> dict[str, Any]:
    candidate = config_candidate(profile, env=env, home=home)
    if candidate is None:
        return {
            "config_exists": False,
            "config_status": "未取得",
            "config_file_status": "未取得",
            "config_file_paths": [],
        }

    file_paths: list[Path] = []
    for raw in profile.get("config_file_paths", []):
        path = expand_profile_path(str(raw), home=home, env=env)
        if path is not None:
            file_paths.append(path)
    existing_files = [path for path in file_paths if path.is_file()]
    credential_paths: list[Path] = []
    for raw in profile.get("credential_paths", []):
        path = expand_profile_path(str(raw), home=home, env=env)
        if path is not None:
            credential_paths.append(path)
    existing_credentials = [path for path in credential_paths if path.is_file()]
    return {
        "config_exists": candidate.exists(),
        "config_status": "已创建" if candidate.exists() else "未创建",
        "config_file_status": (
            "已存在" if existing_files else ("未创建" if file_paths else "未配置")
        ),
        "config_file_paths": [home_relative(path, home) for path in file_paths],
        "credential_status": (
            "已发现" if existing_credentials else ("未发现" if credential_paths else "未取得")
        ),
        "credential_paths": [home_relative(path, home) for path in credential_paths],
    }


def inspect(
    profile: dict[str, Any] | None = None,
    *,
    env: dict[str, str] | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    details = load_profile() if profile is None else profile
    values = dict(os.environ if env is None else env)
    user_home = Path.home() if home is None else home
    found = next((item for item in candidate_paths(details, env=values, home=user_home) if item.is_file()), None)
    base = {
        "schema_version": 1,
        "tool": details["display_name"],
        "command": details["command"],
        "config_path": config_path(details, env=values, home=user_home),
        **config_observation(details, env=values, home=user_home),
        "checked_at": now_rfc3339(),
        "blockers": [],
    }
    if found is None:
        return {
            **base,
            "current_status": "未安装",
            "current_version": "未取得",
            "runtime_status": "未验证",
            "install_method": "未取得",
            "command_path": "未取得",
            "install_dir": "未取得",
            "package_identity": "missing",
            "package_path": "未取得",
        }
    resolved = found.resolve(strict=False)
    install_method = classify_installation(found, resolved, details)
    identity, package_path = package_identity(
        details,
        resolved=resolved,
        install_method=install_method,
        env=values,
        home=user_home,
    )
    try:
        process = run_executable(found, details["version_args"], env=values)
        output = process.stdout.strip() or process.stderr.strip()
        version = parse_version(output)
        runtime = "正常" if process.returncode == 0 else "异常"
        blockers = [] if process.returncode == 0 else ["version_command_failed"]
    except (OSError, subprocess.SubprocessError):
        version = "未取得"
        runtime = "异常"
        blockers = ["version_command_failed"]
    if identity == "mismatch":
        blockers.append("package_identity_mismatch")
    return {
        **base,
        "current_status": "被阻塞" if identity == "mismatch" else "已安装",
        "current_version": version,
        "runtime_status": runtime,
        "install_method": install_method,
        "command_path": home_relative(found, user_home),
        "install_dir": home_relative(resolved.parent, user_home),
        "package_identity": identity,
        "package_path": package_path,
        "blockers": blockers,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    try:
        result = inspect()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"status": "blocked", "error": str(exc)}, ensure_ascii=False))
        return 2
    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(f"{result['tool']}: {result['current_status']} ({result['current_version']})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
