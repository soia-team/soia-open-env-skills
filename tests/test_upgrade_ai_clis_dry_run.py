"""soia-env-ai-cli-upgrade 专属自包含契约测试。

只引用本技能文件与 Python 标准库，离线可跑。契约锁定引擎的全部对外行为：
表格列、状态字、环境变量语义、退出码、日志落盘与轮转。测试对仓内存在的
每个引擎（bash 旧引擎 / Python 新引擎）逐一运行同一套断言——进市场包后
只剩 Python 引擎，套件自动收敛到它。支持仓布局与市场包布局双解析。
"""
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_SKILL_DIRS = [ROOT / "skills" / "soia-env-ai-cli-upgrade", ROOT]
SKILL_DIR = next((d for d in _SKILL_DIRS if (d / "scripts").is_dir()), None)
if SKILL_DIR is None:
    raise FileNotFoundError(f"找不到 scripts 目录：仓布局与包布局均不存在（尝试 {_SKILL_DIRS}）")

ENGINES = []
_SH = SKILL_DIR / "scripts" / "upgrade-ai-clis.sh"
_PY = SKILL_DIR / "scripts" / "upgrade_ai_clis.py"
if _SH.exists():
    ENGINES.append(("bash", ["bash", str(_SH)]))
if _PY.exists():
    ENGINES.append(("python", [sys.executable, str(_PY)]))
if not ENGINES:
    raise FileNotFoundError("找不到任何引擎：upgrade-ai-clis.sh 与 upgrade_ai_clis.py 均不存在")

STUB_VERSION = "9.9.9"
STUB_UPDATED_VERSION = "9.10.0"
IS_WINDOWS = os.name == "nt"
SYSTEM_PATH = os.environ.get("SystemRoot", "C:\\Windows") + "\\System32;" + \
    os.environ.get("SystemRoot", "C:\\Windows") if IS_WINDOWS else \
    "/usr/bin:/bin:/usr/sbin:/sbin"


def make_stub(stub_dir, name, update_behavior="noop"):
    """生成有状态桩命令：--version 读版本文件；update 按行为改状态或失败。
    POSIX 出 sh 脚本，Windows 出 .cmd——契约本身跨平台同一套断言。"""
    stub_dir.mkdir(parents=True, exist_ok=True)
    version_file = stub_dir / f"{name}.version"
    version_file.write_text(STUB_VERSION + "\n")
    if IS_WINDOWS:
        if update_behavior == "bump":
            update_line = f'>"%~dp0{name}.version" echo {STUB_UPDATED_VERSION}\r\nexit /b 0'
        elif update_behavior == "fail":
            update_line = "exit /b 1"
        else:
            update_line = "exit /b 0"
        stub = stub_dir / f"{name}.cmd"
        stub.write_text(
            "@echo off\r\n"
            f'if "%~1"=="--version" (type "%~dp0{name}.version" & exit /b 0)\r\n'
            f'if "%~1"=="update" ({update_line})\r\n'
            "exit /b 1\r\n")
        return stub_dir
    if update_behavior == "bump":
        update_lines = f'echo "{STUB_UPDATED_VERSION}" > "$d/{name}.version"; exit 0'
    elif update_behavior == "fail":
        update_lines = "exit 1"
    else:
        update_lines = "exit 0"
    stub = stub_dir / name
    stub.write_text(
        '#!/bin/sh\nd="$(cd "$(dirname "$0")" && pwd)"\n'
        f'case "$1" in\n  --version) cat "$d/{name}.version"; exit 0;;\n'
        f'  update) {update_lines};;\nesac\nexit 1\n')
    stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
    return stub_dir


class EngineContractTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="ai-cli-upgrade-test.")
        self.workdir = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def run_engine(self, argv, env_overrides, workdir=None):
        workdir = workdir or self.workdir
        env = {
            "HOME": str(workdir / "home"),
            "PATH": env_overrides.pop("PATH", SYSTEM_PATH),
            "TMPDIR": str(workdir / "tmp"),
            "NPM_PREFIX": str(workdir / "npm-absent"),
            "LOG_DIR": str(workdir / "logs"),
        }
        if IS_WINDOWS:
            env["USERPROFILE"] = env["HOME"]
            for passthrough in ("SystemRoot", "ComSpec", "windir", "TEMP", "TMP",
                                "PATHEXT", "SystemDrive"):
                if os.environ.get(passthrough):
                    env[passthrough] = os.environ[passthrough]
        env.update(env_overrides)
        for key in ("HOME", "TMPDIR"):
            pathlib.Path(env[key]).mkdir(parents=True, exist_ok=True)
        return subprocess.run(argv, env=env, cwd=str(workdir),
                              capture_output=True, text=True, timeout=120)

    def each_engine(self):
        for name, argv in ENGINES:
            with self.subTest(engine=name):
                yield name, argv

    # ---- 静态检查 --------------------------------------------------------

    def test_engine_sources_are_valid(self):
        for name, argv in self.each_engine():
            if name == "bash":
                result = subprocess.run(["bash", "-n", argv[1]],
                                        capture_output=True, text=True, timeout=30)
            else:
                result = subprocess.run(
                    [sys.executable, "-m", "py_compile", argv[1]],
                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)

    # ---- dry-run 契约 ----------------------------------------------------

    def test_dry_run_audits_without_upgrading(self):
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-{name}", "qodercli")
            result = self.run_engine(argv, {
                "DRY_RUN": "1", "TOOLS": "qodercli",
                "PATH": f"{stub_dir}" + os.pathsep + SYSTEM_PATH})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SKIP_DRY_RUN", result.stdout)
            self.assertIn(STUB_VERSION, result.stdout)
            self.assertNotIn("FAILED", result.stdout)
            version_file = stub_dir / "qodercli.version"
            self.assertEqual(version_file.read_text().strip(), STUB_VERSION,
                             "dry-run 不得触发升级改动状态")

    def test_header_and_mode_line(self):
        for name, argv in self.each_engine():
            result = self.run_engine(argv, {"DRY_RUN": "1", "TOOLS": "qodercli"})
            for column in ("TOOL", "COMMAND", "OLD", "NEW", "STATUS", "NOTE"):
                self.assertIn(column, result.stdout)
            self.assertIn("Mode: DRY_RUN", result.stdout)
            self.assertIn("DONE. detail log:", result.stdout)

    def test_missing_tool_reported_without_failure(self):
        for name, argv in self.each_engine():
            result = self.run_engine(argv, {"DRY_RUN": "1", "TOOLS": "qodercli"})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("NOT_INSTALLED", result.stdout)
            self.assertIn("command not found", result.stdout)

    # ---- LIVE 契约（桩内完成，不触网、不动真环境） ------------------------

    def test_live_no_delta_reports_already_latest(self):
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-al-{name}", "qodercli", "noop")
            result = self.run_engine(argv, {
                "TOOLS": "qodercli",
                "PATH": f"{stub_dir}" + os.pathsep + SYSTEM_PATH})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("ALREADY_LATEST", result.stdout)
            self.assertIn("Mode: LIVE", result.stdout)

    def test_live_version_delta_reports_updated(self):
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-up-{name}", "qodercli", "bump")
            result = self.run_engine(argv, {
                "TOOLS": "qodercli",
                "PATH": f"{stub_dir}" + os.pathsep + SYSTEM_PATH})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("UPDATED", result.stdout)
            self.assertIn(STUB_UPDATED_VERSION, result.stdout)

    def test_live_update_failure_sets_exit_code(self):
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-fail-{name}", "qodercli", "fail")
            result = self.run_engine(argv, {
                "TOOLS": "qodercli",
                "PATH": f"{stub_dir}" + os.pathsep + SYSTEM_PATH})
            self.assertEqual(result.returncode, 1, "FAILED 行必须带动非零退出码")
            self.assertIn("FAILED", result.stdout)
            self.assertIn("DONE_WITH_FAILURES", result.stdout)

    # ---- 环境变量语义 ----------------------------------------------------

    def test_invalid_claude_channel_rejected(self):
        for name, argv in self.each_engine():
            result = self.run_engine(argv, {"CLAUDE_CHANNEL": "nightly",
                                            "TOOLS": "qodercli"})
            self.assertEqual(result.returncode, 2)
            self.assertIn("invalid CLAUDE_CHANNEL", result.stderr + result.stdout)

    def test_npm_packages_alias_and_tools_priority(self):
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-alias-{name}", "qodercli")
            common = {"DRY_RUN": "1",
                      "PATH": str(stub_dir) + os.pathsep + SYSTEM_PATH}
            via_alias = self.run_engine(argv, dict(common, NPM_PACKAGES="qodercli"))
            self.assertIn("qodercli", via_alias.stdout)
            self.assertIn("SKIP_DRY_RUN", via_alias.stdout)
            tools_wins = self.run_engine(
                argv, dict(common, TOOLS="qodercli", NPM_PACKAGES="cursor"))
            self.assertIn("qodercli", tools_wins.stdout)
            self.assertNotIn("cursor", tools_wins.stdout)

    # ---- 日志契约 --------------------------------------------------------

    def test_log_file_written_and_rotated(self):
        for name, argv in self.each_engine():
            workdir = self.workdir / f"logs-case-{name}"
            log_dir = workdir / "logs"
            log_dir.mkdir(parents=True)
            for i in range(12):
                stale = log_dir / f"cli-upgrade-2020-01-01_00-00-{i:02d}-1.log"
                stale.write_text("old")
                os.utime(stale, (1577836800 + i, 1577836800 + i))
            result = self.run_engine(argv, {"DRY_RUN": "1", "TOOLS": "qodercli",
                                            "LOG_KEEP": "3"}, workdir=workdir)
            self.assertEqual(result.returncode, 0, result.stderr)
            logs = sorted(log_dir.glob("cli-upgrade-*.log"))
            self.assertLessEqual(len(logs), 4, "轮转后至多保留 LOG_KEEP+新一份")
            newest = max(logs, key=lambda p: p.stat().st_mtime)
            self.assertIn("Mode: DRY_RUN", newest.read_text())

    # ---- 2.2.0 新增行为（仅 Python 引擎） --------------------------------

    def test_python_engine_finds_opencode_native_dir(self):
        if IS_WINDOWS:
            self.skipTest("~/.opencode/bin 是 POSIX 原生安装布局，Windows 无此形态")
        py = dict(ENGINES).get("python")
        if py is None:
            self.skipTest("Python 引擎不在场")
        home = self.workdir / "home"
        make_stub(home / ".opencode" / "bin", "opencode")
        result = self.run_engine(py, {"DRY_RUN": "1", "TOOLS": "opencode"})
        self.assertIn("SKIP_DRY_RUN", result.stdout)
        self.assertIn(STUB_VERSION, result.stdout)
        self.assertNotIn("NOT_INSTALLED", result.stdout,
                         "~/.opencode/bin 未入 PATH 时也必须探测到")

    # ---- 2.3.3 新增行为：DeepSeek Harness (dsh) --------------------------

    def test_dsh_is_in_default_tool_list(self):
        for name, argv in self.each_engine():
            result = self.run_engine(argv, {"DRY_RUN": "1"})
            self.assertEqual(result.returncode, 0, result.stderr)
            row = next((ln for ln in result.stdout.splitlines()
                        if ln.strip().startswith("dsh ")), None)
            self.assertIsNotNone(row, "默认批次必须包含 dsh 行")
            self.assertIn("NOT_INSTALLED", row)

    def test_dsh_dry_run_audits_stub_without_upgrading(self):
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-dsh-dry-{name}", "dsh")
            result = self.run_engine(argv, {
                "DRY_RUN": "1", "TOOLS": "dsh",
                "PATH": f"{stub_dir}" + os.pathsep + SYSTEM_PATH})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("SKIP_DRY_RUN", result.stdout)
            self.assertIn(STUB_VERSION, result.stdout)
            version_file = stub_dir / "dsh.version"
            self.assertEqual(version_file.read_text().strip(), STUB_VERSION,
                             "dry-run 不得触发 dsh 升级改动状态")

    def test_dsh_live_unknown_channel_reports_manual(self):
        # 非 brew、非 npm prefix 的二进制没有已知升级通道，保守报 MANUAL 而不是误升级
        for name, argv in self.each_engine():
            stub_dir = make_stub(self.workdir / f"stub-dsh-live-{name}", "dsh")
            result = self.run_engine(argv, {
                "TOOLS": "dsh",
                "PATH": f"{stub_dir}" + os.pathsep + SYSTEM_PATH})
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("MANUAL", result.stdout)
            self.assertNotIn("FAILED", result.stdout)
            self.assertNotIn("UPDATED", result.stdout)


if __name__ == "__main__":
    unittest.main()
