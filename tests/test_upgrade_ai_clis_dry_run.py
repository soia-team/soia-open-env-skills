"""soia-env-ai-cli-upgrade 专属自包含测试。

只引用本技能文件与 Python 标准库，离线可跑：用临时桩命令验证 dry-run 审计的
三条核心承诺——只读不升级、缺失工具如实报告、日志落盘。
支持仓布局与市场包布局双解析（进包后照常实跑）。
"""
import pathlib
import stat
import subprocess
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_REPO_LAYOUT = ROOT / "skills" / "soia-env-ai-cli-upgrade" / "scripts" / "upgrade-ai-clis.sh"
_PACKAGE_LAYOUT = ROOT / "scripts" / "upgrade-ai-clis.sh"
if _REPO_LAYOUT.exists():
    SCRIPT = _REPO_LAYOUT
elif _PACKAGE_LAYOUT.exists():
    SCRIPT = _PACKAGE_LAYOUT
else:
    raise FileNotFoundError(
        "找不到 upgrade-ai-clis.sh：仓布局 {} 与包布局 {} 均不存在".format(
            _REPO_LAYOUT, _PACKAGE_LAYOUT))

STUB_VERSION = "9.9.9"
STUB = "#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo {v}; exit 0; fi\nexit 1\n"


def run_script(env_overrides, workdir):
    """在受控 PATH 与临时 HOME 下跑脚本，返回 CompletedProcess。"""
    env = {
        "HOME": str(workdir / "home"),
        "PATH": env_overrides.pop("PATH", "/usr/bin:/bin:/usr/sbin:/sbin"),
        "TMPDIR": str(workdir / "tmp"),
        "DRY_RUN": "1",
        "NPM_PREFIX": str(workdir / "npm-absent"),
        "LOG_DIR": str(workdir / "logs"),
    }
    env.update(env_overrides)
    for key in ("HOME", "TMPDIR"):
        pathlib.Path(env[key]).mkdir(parents=True, exist_ok=True)
    return subprocess.run(
        ["bash", str(SCRIPT)], env=env, cwd=str(workdir),
        capture_output=True, text=True, timeout=120,
    )


class DryRunAuditTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="ai-cli-upgrade-test.")
        self.workdir = pathlib.Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _make_stub(self, name):
        stub_dir = self.workdir / "stub-bin"
        stub_dir.mkdir(exist_ok=True)
        stub = stub_dir / name
        stub.write_text(STUB.format(v=STUB_VERSION))
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        return stub_dir

    def test_script_syntax_is_valid(self):
        result = subprocess.run(["bash", "-n", str(SCRIPT)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_dry_run_audits_without_upgrading(self):
        """桩工具在 PATH 上：报 SKIP_DRY_RUN 与当前版本，不执行任何升级。"""
        stub_dir = self._make_stub("qodercli")
        result = run_script(
            {"TOOLS": "qodercli",
             "PATH": f"{stub_dir}:/usr/bin:/bin:/usr/sbin:/sbin"},
            self.workdir,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("SKIP_DRY_RUN", result.stdout)
        self.assertIn(STUB_VERSION, result.stdout)
        self.assertNotIn("NOT_INSTALLED", result.stdout)
        self.assertNotIn("FAILED", result.stdout)

    def test_missing_tool_reported_without_failure(self):
        """工具缺失：如实报 NOT_INSTALLED，且不视为脚本失败（退出码 0）。"""
        result = run_script({"TOOLS": "qodercli"}, self.workdir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("NOT_INSTALLED", result.stdout)
        self.assertIn("command not found", result.stdout)

    def test_log_file_is_written_to_log_dir(self):
        """每次运行落一份时间戳日志到 LOG_DIR。"""
        run_script({"TOOLS": "qodercli"}, self.workdir)
        logs = list((self.workdir / "logs").glob("cli-upgrade-*.log"))
        self.assertEqual(len(logs), 1, "应恰好产生一份日志文件")
        self.assertIn("Mode: DRY_RUN", logs[0].read_text())


if __name__ == "__main__":
    unittest.main()
