#!/usr/bin/env python3
# @created_by  claude-fable-5
# @created_at  2026-08-08 14:10:00
# @version     2.1.0
# @description Audit and safely upgrade supported AI/developer CLIs (Python engine).
# @changelog   Platform-aware paths for native Windows (os.pathsep, npm prefix layout,
#              per-platform shell); agy install reported MANUAL on Windows.
#              Previously: port bash engine verbatim; ~/.opencode/bin fallback.
"""AI CLI 升级助手引擎（Python 版）。

与原 bash 引擎保持同一对外契约：环境变量、表格列、状态字、退出码、日志命名
与轮转。仅标准库，无第三方依赖——这是外部技能市场（文件白名单只收 .py）
的硬前提。行为差异只有一处显式增补：opencode 原生安装的 ~/.opencode/bin
探测回退（2026-08-08 真机实跑发现旧 shell PATH 缺失时误报未安装）。
"""

import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime
from pathlib import Path

HOME = Path.home()
IS_WINDOWS = os.name == "nt"
PATHSEP = os.pathsep
POSIX_SYSTEM_PATH = "/opt/homebrew/bin:/usr/local/bin:/usr/bin:/usr/sbin:/bin:/sbin"

# ---------------------------------------------------------------- config file

def load_config_env():
    """读取私有 config.yml 的 env: 段并写入 os.environ（与 bash eval export 同语义：
    配置覆盖既有环境变量）。"""
    config_file = os.environ.get("SOIA_ENV_AI_CLI_UPGRADE_CONFIG_FILE") or \
        os.environ.get("SOIA_ENV_AI_CLI_UPGRADE_ENV_FILE") or \
        os.environ.get("SOIA_DEV_AI_CLI_UPGRADE_CONFIG_FILE") or \
        os.environ.get("SOIA_DEV_AI_CLI_UPGRADE_ENV_FILE")
    if not config_file:
        new_cfg = HOME / ".config/soia-skills/soia-env-ai-cli-upgrade/config.yml"
        legacy = HOME / ".config/soia-skills/soia-open-skills/soia-dev/soia-dev-ai-cli-upgrade/config.yml"
        config_file = str(new_cfg if (new_cfg.is_file() or not legacy.is_file()) else legacy)
    path = Path(config_file).expanduser()
    if not path.is_file():
        return
    key_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    path_like = {"AGY_INSTALL_DIR", "LOG_DIR", "NPM_PREFIX"}
    in_env = False
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))
        if indent == 0:
            in_env = stripped == "env:"
            continue
        if not in_env or indent < 2 or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        key = key.strip()
        if not key_re.match(key):
            continue
        value = value.strip()
        if len(value) >= 2 and value[0] == value[-1] and value[0] in ("'", '"'):
            value = value[1:-1]
        else:
            value = value.split(" #", 1)[0].strip()
        if key in path_like:
            value = os.path.expandvars(os.path.expanduser(value))
        os.environ[key] = value


load_config_env()

# ---------------------------------------------------------------- settings

log_dir = Path(os.environ.get("LOG_DIR") or
               Path(tempfile.gettempdir()) / "soia-env-ai-cli-upgrade/logs")
log_dir.mkdir(parents=True, exist_ok=True)
log_keep = int(os.environ.get("LOG_KEEP", "10") or "10")
_old_logs = sorted(log_dir.glob("cli-upgrade-*.log"),
                   key=lambda p: p.stat().st_mtime, reverse=True)
for _stale in _old_logs[log_keep:]:
    try:
        _stale.unlink()
    except OSError:
        pass
log_file = log_dir / "cli-upgrade-{}-{}.log".format(
    datetime.now().strftime("%Y-%m-%d_%H-%M-%S"), os.getpid())

if os.environ.get("NPM_PREFIX"):
    npm_prefix = os.environ["NPM_PREFIX"]
elif IS_WINDOWS and os.environ.get("APPDATA"):
    npm_prefix = str(Path(os.environ["APPDATA"]) / "npm")
else:
    npm_prefix = str(HOME / ".npm-global")


def npm_bin_dir():
    """npm 全局可执行目录：Windows 直接放 prefix 根，POSIX 在 prefix/bin。"""
    return npm_prefix if IS_WINDOWS else f"{npm_prefix}/bin"
agy_install_dir = os.environ.get("AGY_INSTALL_DIR") or str(HOME / ".local/bin")
agy_install = os.environ.get("AGY_INSTALL", "0")
claude_channel = os.environ.get("CLAUDE_CHANNEL", "preserve")
if claude_channel not in ("preserve", "latest"):
    print(f"invalid CLAUDE_CHANNEL={claude_channel}; expected preserve or latest",
          file=sys.stderr)
    sys.exit(2)

dry_run = os.environ.get("DRY_RUN", "0")
run_mode = "DRY_RUN" if dry_run == "1" else "LIVE"

NPM_BIN = os.environ.get("NPM_BIN", "")
NPM_CLEAN_ENV = None


def _run(cmd, **kw):
    """subprocess.run 包一层：默认吞输出进日志文件。"""
    with open(log_file, "a", encoding="utf-8") as fh:
        return subprocess.run(cmd, stdout=fh, stderr=fh, **kw)


def _capture(cmd, env=None, timeout=60):
    try:
        return subprocess.run(cmd, capture_output=True, text=True,
                              env=env, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired):
        return None


def _find_arm64_npm():
    if not IS_WINDOWS:
        node = Path("/opt/homebrew/bin/node")
        npm = Path("/opt/homebrew/bin/npm")
        if npm.exists() and os.access(npm, os.X_OK) and node.exists() and os.access(node, os.X_OK):
            out = _capture(["file", str(node)])
            if out and "arm64" in out.stdout:
                return str(npm)
        for pattern in ("v24*", "v22*", "v2*"):
            for d in sorted((HOME / ".nvm/versions/node").glob(pattern)):
                cand_npm, cand_node = d / "bin/npm", d / "bin/node"
                if not (os.access(cand_npm, os.X_OK) and os.access(cand_node, os.X_OK)):
                    continue
                out = _capture(["file", str(cand_node)])
                if out and "arm64" in out.stdout:
                    return str(cand_npm)
    return shutil.which("npm") or ""


def ensure_npm():
    global NPM_BIN, NPM_CLEAN_ENV
    if not NPM_BIN:
        NPM_BIN = _find_arm64_npm()
    if not (NPM_BIN and os.access(NPM_BIN, os.X_OK)):
        return False
    if IS_WINDOWS:
        NPM_CLEAN_ENV = dict(os.environ, PATH=PATHSEP.join(
            [str(Path(NPM_BIN).parent), npm_bin_dir(), os.environ.get("PATH", "")]))
    else:
        NPM_CLEAN_ENV = {
            "HOME": str(HOME),
            "PATH": f"{Path(NPM_BIN).parent}:{npm_bin_dir()}:" + POSIX_SYSTEM_PATH,
        }
    return True


def log(message):
    print(message)
    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write(message + "\n")


VERSION_RE = re.compile(r"([0-9]+\.){1,}[0-9]+([.-][0-9A-Za-z._+-]+)?")


def extract_version(text):
    m = VERSION_RE.search(text)
    return m.group(0) if m else text


def resolve_bin(tool, cmd):
    from_path = shutil.which(cmd) or ""
    if tool == "agy":
        if from_path:
            return from_path
        return shutil.which(cmd, path=agy_install_dir) or ""
    prefixed = shutil.which(cmd, path=npm_bin_dir())
    if prefixed:
        return prefixed
    if from_path:
        return from_path
    if tool == "opencode":
        # 2026-08-08 真机实跑：原生安装落 ~/.opencode/bin，旧 shell 未刷 PATH 时
        # 误报未安装；与 agy 的安装目录回退同一策略。
        return shutil.which(cmd, path=str(HOME / ".opencode/bin")) or ""
    return ""


def get_version(binary):
    if not os.access(binary, os.X_OK):
        return None
    if os.path.normcase(str(Path(binary).parent)) == os.path.normcase(npm_bin_dir()):
        ensure_npm()
    components = ([str(Path(NPM_BIN).parent)] if NPM_BIN else []) + \
        [npm_bin_dir(), agy_install_dir]
    if IS_WINDOWS:
        clean_path = PATHSEP.join(components + [os.environ.get("PATH", "")])
    else:
        clean_path = ":".join(components) + ":" + POSIX_SYSTEM_PATH
    env = dict(os.environ, PATH=clean_path)
    for args in ([binary, "--version"], [binary, "version"]):
        out = _capture(args, env=env)
        if out and out.returncode == 0:
            return extract_version(out.stdout)
    return "UNKNOWN"


def binary_note(tool, cmd, binary):
    note = f"path={binary}"
    if tool == "agy":
        from_path = shutil.which(cmd) or ""
        if not from_path:
            note += "; PATH missing"
        elif not os.path.exists(from_path) or not os.path.samefile(from_path, binary):
            note += f"; PATH resolves to {from_path}"
    return note


def _readlink(binary):
    try:
        return os.readlink(binary)
    except OSError:
        return ""


def detect_claude_method(binary):
    link_target = _readlink(binary)
    if "/Application Support/Claude/" in binary or "/Application Support/Claude/" in link_target:
        return "desktop"
    if "/.local/share/claude/" in link_target or binary.startswith(str(HOME / ".local/share/claude/")):
        return "native"
    if binary.startswith(f"{npm_prefix}/") or "/node_modules/" in link_target:
        return "npm"
    if shutil.which("brew"):
        for cask in ("claude-code@latest", "claude-code"):
            if _run(["brew", "list", "--cask", cask]).returncode == 0:
                return "brew"
    return "unknown"


def detect_brew_claude_cask():
    if not shutil.which("brew"):
        return None
    for cask in ("claude-code@latest", "claude-code"):
        if _run(["brew", "list", "--cask", cask]).returncode == 0:
            return cask
    return None


def migrate_brew_claude_to_latest(current_cask):
    if current_cask == "claude-code@latest":
        return True
    if current_cask != "claude-code":
        return False
    if _run(["brew", "fetch", "--cask", "claude-code@latest"]).returncode != 0:
        return False
    if _run(["brew", "uninstall", "--cask", "claude-code"]).returncode != 0:
        return False
    if _run(["brew", "install", "--cask", "claude-code@latest"]).returncode == 0:
        return True
    with open(log_file, "a", encoding="utf-8") as fh:
        fh.write("claude @latest install failed; restoring stable cask\n")
    _run(["brew", "install", "--cask", "claude-code"])
    return False


def is_npm_install(binary):
    if os.path.normcase(binary).startswith(os.path.normcase(npm_prefix) + os.sep) or \
            binary.startswith(f"{npm_prefix}/"):
        return True
    return "/node_modules/" in _readlink(binary)


def recommend_install_note(tool, binary):
    if tool == "codex" and is_npm_install(binary):
        return ("npm detected (legacy); recommend: native curl installer "
                "(curl -fsSL https://chatgpt.com/codex/install.sh | sh)")
    if tool == "qwen" and is_npm_install(binary):
        return "npm detected; recommend: native curl installer"
    if tool == "opencode" and is_npm_install(binary):
        return ("npm detected; recommend: native curl installer "
                "(curl -fsSL https://opencode.ai/install | bash)")
    if tool == "kimi" and is_npm_install(binary):
        return "npm detected; recommend: brew install kimi-code"
    if tool == "claude" and detect_claude_method(binary) == "npm":
        return "npm detected (legacy); recommend: native installer (claude.ai/download)"
    return ""


def detect_brew_formula_from_bin(binary):
    if not shutil.which("brew"):
        return None
    out = _capture(["brew", "--prefix"])
    if not out or out.returncode != 0:
        return None
    try:
        homebrew_prefix = str(Path(out.stdout.strip()).resolve())
    except OSError:
        return None
    link_target = _readlink(binary)
    resolved_target = link_target
    if link_target:
        target_path = link_target if link_target.startswith("/") else \
            str(Path(binary).parent / link_target)
        target_dir, target_base = str(Path(target_path).parent), Path(target_path).name
        try:
            physical_dir = str(Path(target_dir).resolve(strict=True))
            resolved_target = f"{physical_dir}/{target_base}"
        except OSError:
            pass
    for check in (resolved_target, link_target, binary):
        if check and check.startswith(f"{homebrew_prefix}/Cellar/"):
            formula = check[len(f"{homebrew_prefix}/Cellar/"):].split("/", 1)[0]
            if formula:
                return formula
    return None


def install_agy():
    installer_url = "https://antigravity.google/cli/install.sh"
    if IS_WINDOWS:
        return False  # 官方安装器是 bash 脚本；原生 Windows 请走 WSL
    if not shutil.which("curl"):
        return False
    with tempfile.TemporaryDirectory(
            prefix="soia-agy-install.", dir=os.environ.get("TMPDIR", "/tmp")) as tmp:
        installer_file = Path(tmp) / "install.sh"
        staging_home = Path(tmp) / "home"
        staging_home.mkdir()
        if _run(["curl", "--proto", "=https", "--tlsv1.2", "-fsSL",
                 "-o", str(installer_file), installer_url]).returncode != 0:
            return False
        if _run(["bash", "-n", str(installer_file)]).returncode != 0:
            return False
        if _run(["bash", str(installer_file), "--dir", agy_install_dir],
                env=dict(os.environ, HOME=str(staging_home))).returncode != 0:
            return False
    return os.access(Path(agy_install_dir) / "agy", os.X_OK)


had_failure = False


def print_result(tool, cmd, old, new, status, note):
    global had_failure
    if status == "FAILED":
        had_failure = True
    log(f"{tool:<10} {cmd:<12} {old:<18} {new:<18} {status:<14} {note}")


def print_header():
    log("-" * 60)
    log("AI CLI Upgrade Log")
    log("Date: " + datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %z"))
    log(f"Mode: {run_mode}")
    log(f"Log: {log_file}")
    log("-" * 60)
    log(f"{'TOOL':<10} {'COMMAND':<12} {'OLD':<18} {'NEW':<18} {'STATUS':<14} NOTE")


TOOL_META = {
    "codex": ("codex", "@openai/codex"),
    "claude": ("claude", "@anthropic-ai/claude-code"),
    "gemini": ("gemini", "@google/gemini-cli"),
    "agy": ("agy", ""),
    "qwen": ("qwen", "@qwen-code/qwen-code"),
    "mmx": ("mmx", "mmx-cli"),
    "kimi": ("kimi", "@moonshot-ai/kimi-code"),
    "opencode": ("opencode", "opencode-ai"),
    "qodercli": ("qodercli", ""),
    "cursor": ("cursor", ""),
    "deepcode": ("deepcode", "@vegamo/deepcode-cli"),
    "pi": ("pi", "@earendil-works/pi-coding-agent"),
}


def npm_reinstall(package):
    if not ensure_npm():
        return "no-npm"
    rc = subprocess.run(
        [NPM_BIN, "install", "-g", "--prefix", npm_prefix, package],
        stdout=open(log_file, "a"), stderr=subprocess.STDOUT,
        env=NPM_CLEAN_ENV).returncode
    return "ok" if rc == 0 else "failed"


def upgrade_tool(tool):
    cmd, package = TOOL_META.get(tool, (tool, ""))

    binary = resolve_bin(tool, cmd)
    if not binary:
        if tool == "agy" and dry_run != "1" and agy_install == "1":
            if not install_agy():
                print_result(tool, cmd, "-", "-", "FAILED",
                             "official installer failed; see log")
                return
            binary = str(Path(agy_install_dir) / "agy")
            installed_version = get_version(binary)
            install_note = binary_note(tool, cmd, binary) + "; official installer"
            path_bin = shutil.which(cmd) or ""
            install_status = "INSTALLED"
            if not path_bin or not os.path.samefile(path_bin, binary):
                install_status = "MANUAL"
            if not installed_version or installed_version == "UNKNOWN":
                print_result(tool, cmd, "-", "-", "FAILED",
                             f"version check failed after official install; path={binary}")
            else:
                print_result(tool, cmd, "-", installed_version, install_status, install_note)
            return
        if tool == "agy" and dry_run != "1":
            print_result(tool, cmd, "-", "-", "MANUAL",
                         "not installed; set AGY_INSTALL=1 for official install")
        else:
            print_result(tool, cmd, "-", "-", "NOT_INSTALLED", "command not found")
        return

    old_version = get_version(binary)
    rec_note = recommend_install_note(tool, binary)

    if dry_run == "1":
        note = binary_note(tool, cmd, binary) + "; no upgrade"
        if tool == "claude" and detect_claude_method(binary) == "brew":
            cask = detect_brew_claude_cask()
            if cask:
                note += f"; channel={cask}"
                if cask == "claude-code" and claude_channel == "latest":
                    note += "; would switch to claude-code@latest"
                elif cask == "claude-code":
                    note += ("; preserved (set CLAUDE_CHANNEL=latest only with "
                             "channel-switch authorization)")
        if rec_note:
            note += f"; {rec_note}"
        print_result(tool, cmd, old_version, "N/A", "SKIP_DRY_RUN", note)
        return

    if tool in ("codex", "mmx"):
        if _run([binary, "update"]).returncode != 0:
            print_result(tool, cmd, old_version, old_version, "FAILED",
                         f"{cmd} update failed; path={binary}")
            return
    elif tool in ("gemini", "qwen", "opencode", "kimi", "deepcode"):
        brew_formula = detect_brew_formula_from_bin(binary)
        if brew_formula:
            if _run(["brew", "upgrade", brew_formula]).returncode != 0:
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"brew upgrade {brew_formula} failed; path={binary}")
                return
        elif is_npm_install(binary):
            npm_rc = npm_reinstall(package)
            if npm_rc == "no-npm":
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"npm not found for {package}")
                return
            if npm_rc == "failed":
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"npm install -g {package} failed")
                return
        else:
            if tool in ("gemini", "qwen"):
                if _run([binary, "update"]).returncode != 0:
                    print_result(tool, cmd, old_version, old_version, "FAILED",
                                 f"{cmd} update failed; path={binary}")
                    return
            elif tool == "kimi":
                if _run([binary, "upgrade"]).returncode != 0:
                    print_result(tool, cmd, old_version, old_version, "FAILED",
                                 f"kimi upgrade failed; path={binary}")
                    return
            elif tool == "opencode":
                print_result(tool, cmd, old_version, old_version, "MANUAL",
                             "native install; re-run: curl -fsSL https://opencode.ai/install"
                             f" | bash; path={binary}")
                return
    elif tool == "claude":
        install_method = detect_claude_method(binary)
        if install_method in ("native", "unknown"):
            if _run([binary, "update"]).returncode != 0:
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"claude update failed; path={binary}")
                return
        elif install_method == "brew":
            cask = detect_brew_claude_cask()
            if not cask:
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"brew cask detection failed; path={binary}")
                return
            if cask == "claude-code" and claude_channel == "latest":
                if not migrate_brew_claude_to_latest(cask):
                    print_result(tool, cmd, old_version, old_version, "FAILED",
                                 "Claude channel switch to claude-code@latest failed; "
                                 "stable cask restore attempted")
                    return
            elif _run(["brew", "upgrade", "--cask", cask]).returncode != 0:
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"brew upgrade --cask {cask} failed; path={binary}")
                return
        elif install_method == "npm":
            npm_rc = npm_reinstall(package)
            if npm_rc == "no-npm":
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"npm not found for {package}")
                return
            if npm_rc == "failed":
                print_result(tool, cmd, old_version, old_version, "FAILED",
                             f"npm install -g {package} failed")
                return
        elif install_method == "desktop":
            print_result(tool, cmd, old_version, old_version, "MANUAL",
                         f"Desktop-managed; update via Claude Desktop app; path={binary}")
            return
    elif tool == "agy":
        if _run([binary, "update"]).returncode != 0:
            print_result(tool, cmd, old_version, old_version, "FAILED",
                         f"agy update failed; path={binary}")
            return
    elif tool == "qodercli":
        if _run([binary, "update"]).returncode != 0:
            print_result(tool, cmd, old_version, old_version, "FAILED",
                         "qodercli update failed")
            return
    elif tool == "pi":
        if _run([binary, "update", "--self"]).returncode != 0:
            print_result(tool, cmd, old_version, old_version, "FAILED",
                         f"pi update --self failed; path={binary}")
            return
    elif tool == "cursor":
        cursor_cmd = os.environ.get("CURSOR_UPGRADE_CMD", "")
        if not cursor_cmd:
            print_result(tool, cmd, old_version, old_version, "MANUAL",
                         "no default updater; set CURSOR_UPGRADE_CMD")
            return
        shell_argv = ["cmd", "/c", cursor_cmd] if IS_WINDOWS else ["bash", "-lc", cursor_cmd]
        if _run(shell_argv).returncode != 0:
            print_result(tool, cmd, old_version, old_version, "FAILED",
                         "CURSOR_UPGRADE_CMD failed")
            return
    else:
        print_result(tool, cmd, old_version, old_version, "MANUAL", "no upgrader config")
        return

    binary = resolve_bin(tool, cmd)
    if not binary:
        print_result(tool, cmd, old_version, old_version, "FAILED",
                     "command missing after upgrade")
        return
    new_version = get_version(binary)
    if not new_version or new_version == "UNKNOWN":
        status, note, new_version = "FAILED", "version check failed after upgrade", old_version
    elif new_version != old_version:
        status, note = "UPDATED", "upgraded; " + binary_note(tool, cmd, binary)
    else:
        status, note = "ALREADY_LATEST", "no version delta; " + binary_note(tool, cmd, binary)
    if tool == "agy":
        path_bin = shutil.which(cmd) or ""
        if not path_bin or not os.path.samefile(path_bin, binary):
            status = "MANUAL"
            note = "update complete; " + binary_note(tool, cmd, binary)
    if rec_note:
        note += f"; {rec_note}"
    if tool == "claude" and detect_claude_method(binary) == "brew":
        final_cask = detect_brew_claude_cask()
        if final_cask:
            note += f"; channel={final_cask}"
        if final_cask == "claude-code" and claude_channel == "preserve":
            note += "; stable channel preserved"
    print_result(tool, cmd, old_version, new_version, status, note)


def main():
    print_header()
    default_tools = ["codex", "claude", "agy", "kimi", "mmx", "qwen",
                     "opencode", "qodercli", "cursor", "deepcode", "pi"]
    selector = os.environ.get("TOOLS") or os.environ.get("NPM_PACKAGES") or ""
    if selector:
        tools = [t.strip() for t in selector.split(",") if t.strip()]
    else:
        tools = default_tools
    for tool in tools:
        upgrade_tool(tool)
    if had_failure:
        log(f"DONE_WITH_FAILURES. detail log: {log_file}")
        sys.exit(1)
    log(f"DONE. detail log: {log_file}")


if __name__ == "__main__":
    main()
