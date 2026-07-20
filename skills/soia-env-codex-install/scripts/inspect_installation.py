#!/usr/bin/env python3
"""Inspect the standalone Codex CLI separately from ChatGPT.app."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


APP_RESOURCE_MARKER = ".app/Contents/Resources/"


def home_relative(path: Path, home: Path) -> str:
    try:
        relative = path.expanduser().absolute().relative_to(home.expanduser().absolute())
    except ValueError:
        return str(path)
    return "~" if not relative.parts else str(Path("~") / relative)


def classify_installation(
    command_path: Path,
    resolved_path: Path,
    npm_root: Path | None,
) -> tuple[str, Path]:
    command_text = str(command_path)
    if is_app_bundled(command_path) or is_app_bundled(resolved_path):
        return "ChatGPT.app 内置（非独立 CLI）", command_path.parent

    if npm_root is not None:
        package_dir = npm_root / "@openai" / "codex"
        for candidate in (command_path, resolved_path):
            try:
                candidate.absolute().relative_to(package_dir.absolute())
                return "npm 全局安装", package_dir
            except ValueError:
                pass
        if "npm" in command_text and command_path.name == "codex":
            return "npm 全局安装", package_dir

    resolved_text = str(resolved_path)
    if "/Caskroom/codex/" in resolved_text:
        return "Homebrew cask", resolved_path.parent

    if "/.codex/packages/standalone/releases/" in resolved_text:
        install_dir = (
            resolved_path.parent.parent
            if resolved_path.parent.name == "bin"
            else resolved_path.parent
        )
        return "官方独立安装", install_dir

    return "独立安装（来源未知）", command_path.parent


def is_app_bundled(path: Path) -> bool:
    return APP_RESOURCE_MARKER in str(path)


def command_output(args: list[str]) -> str:
    try:
        result = subprocess.run(args, text=True, capture_output=True, check=False)
    except OSError:
        return ""
    return (result.stdout or result.stderr).strip()


def npm_root() -> Path | None:
    value = command_output(["npm", "root", "--global"]) if shutil.which("npm") else ""
    return Path(value) if value else None


def login_shell_codex() -> Path | None:
    if os.name == "nt":
        return None
    shell = os.environ.get("SHELL")
    if not shell or not Path(shell).is_file():
        return None
    value = command_output([shell, "-lic", "command -v codex"])
    first_line = value.splitlines()[0].strip() if value else ""
    return Path(first_line) if first_line.startswith("/") else None


def candidate_paths(home: Path, npm_global_root: Path | None) -> list[Path]:
    candidates: list[Path] = []

    def add(path: Path | None) -> None:
        if path is None or path in candidates:
            return
        candidates.append(path)

    add(login_shell_codex())
    add(Path(active) if (active := shutil.which("codex")) else None)

    if npm_global_root is not None:
        npm_prefix = npm_global_root.parent.parent
        add(npm_prefix / "bin" / ("codex.cmd" if os.name == "nt" else "codex"))

    executable_name = "codex.exe" if os.name == "nt" else "codex"
    add(home / ".local" / "bin" / executable_name)
    add(home / ".codex" / "bin" / executable_name)
    add(Path("/opt/homebrew/bin/codex"))
    add(Path("/usr/local/bin/codex"))
    add(Path("/Applications/ChatGPT.app/Contents/Resources/codex"))

    release_root = home / ".codex" / "packages" / "standalone" / "releases"
    if release_root.is_dir():
        releases = sorted(
            release_root.glob(f"*/bin/{executable_name}"),
            key=lambda path: path.stat().st_mtime if path.exists() else 0,
            reverse=True,
        )
        releases += sorted(
            release_root.glob(f"*/{executable_name}"),
            key=lambda path: path.stat().st_mtime if path.exists() else 0,
            reverse=True,
        )
        for release in releases:
            add(release)

    return candidates


def select_independent_cli(candidates: list[Path]) -> tuple[Path | None, Path | None]:
    existing = [
        candidate
        for candidate in candidates
        if candidate.is_file() and os.access(candidate, os.X_OK)
    ]
    app_path = next(
        (
            candidate
            for candidate in existing
            if is_app_bundled(candidate) or is_app_bundled(candidate.resolve())
        ),
        None,
    )
    for candidate in existing:
        resolved = candidate.resolve()
        if is_app_bundled(candidate) or is_app_bundled(resolved):
            continue
        return candidate, app_path
    return None, app_path


def inspect() -> dict[str, str]:
    home = Path.home()
    config_dir = Path(os.environ.get("CODEX_HOME", home / ".codex")).expanduser()
    npm_global_root = npm_root()
    candidates = candidate_paths(home, npm_global_root)
    command_path, app_path = select_independent_cli(candidates)
    if command_path is None:
        npm_package_dir = (
            npm_global_root / "@openai" / "codex"
            if npm_global_root is not None
            else None
        )
        package_without_command = bool(
            npm_package_dir is not None and npm_package_dir.is_dir()
        )
        return {
            "current_status": "被阻塞" if package_without_command else "未安装",
            "current_version": "未取得",
            "runtime_status": "异常" if package_without_command else "未验证",
            "install_method": "npm 全局安装" if package_without_command else "未取得",
            "install_dir": (
                home_relative(npm_package_dir, home)
                if npm_package_dir is not None and package_without_command
                else "未取得"
            ),
            "config_dir": home_relative(config_dir, home),
            "cli_path": "未取得",
            "login_status": "未验证",
            "app_detected": "是" if app_path is not None else "否",
            "app_path": (
                home_relative(app_path, home) if app_path is not None else "未取得"
            ),
        }

    resolved_path = command_path.resolve()
    method, install_dir = classify_installation(
        command_path,
        resolved_path,
        npm_global_root,
    )
    executable = str(command_path)
    version_output = command_output([executable, "--version"])
    version = version_output.split()[-1] if version_output else "未取得"
    help_ok = subprocess.run(
        [executable, "--help"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    login_ok = subprocess.run(
        [executable, "login", "status"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0
    return {
        "current_status": "已安装",
        "current_version": version,
        "runtime_status": "正常" if help_ok and login_ok else "异常",
        "install_method": method,
        "install_dir": home_relative(install_dir, home),
        "config_dir": home_relative(config_dir, home),
        "cli_path": home_relative(command_path, home),
        "login_status": "已登录" if login_ok else "未登录",
        "app_detected": "是" if app_path is not None else "否",
        "app_path": home_relative(app_path, home) if app_path is not None else "未取得",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    data = inspect()
    if args.json:
        print(json.dumps(data, ensure_ascii=False, sort_keys=True))
    else:
        for key, value in data.items():
            print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
