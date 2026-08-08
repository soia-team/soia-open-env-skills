import importlib.util
import pathlib
import subprocess
import unittest
from unittest.mock import patch


ROOT = pathlib.Path(__file__).resolve().parents[1]
_REPO_LAYOUT = ROOT / "skills" / "soia-env-network-diagnose" / "scripts" / "probe_runtimes.py"
_PACKAGE_LAYOUT = ROOT / "scripts" / "probe_runtimes.py"
if _REPO_LAYOUT.exists():
    SCRIPT = _REPO_LAYOUT
elif _PACKAGE_LAYOUT.exists():
    SCRIPT = _PACKAGE_LAYOUT
else:
    raise FileNotFoundError(
        "找不到 probe_runtimes.py：仓布局 {} 与包布局 {} 均不存在".format(_REPO_LAYOUT, _PACKAGE_LAYOUT)
    )
SPEC = importlib.util.spec_from_file_location("probe_runtimes", SCRIPT)
probe_runtimes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe_runtimes)


class Completed:
    def __init__(self, stdout="", stderr="", returncode=0):
        self.stdout = stdout
        self.stderr = stderr
        self.returncode = returncode


def runtime_args(name):
    return next(args for entry_name, _, args in probe_runtimes.RUNTIMES if entry_name == name)


class VersionParsingTests(unittest.TestCase):
    def test_real_world_outputs_are_parsed(self):
        """样本全部取自真机实测输出，含本地化文案与带路径输出。"""
        samples = {
            "v26.5.0": "26.5.0",
            "Python 3.14.6": "3.14.6",
            "pip 26.1.2 from /opt/homebrew/lib/python3.14/site-packages/pip": "26.1.2",
            "uv 0.11.2 (02036a8ba 2026-03-26 aarch64-apple-darwin)": "0.11.2",
            "go version go1.26.4 darwin/arm64": "1.26.4",
            "cargo 1.92.0 (344c4567c 2025-10-21)": "1.92.0",
            "Homebrew 6.0.15": "6.0.15",
            "curl 8.7.1 (x86_64-apple-darwin25.0) libcurl/8.7.1": "8.7.1",
            "UnZip 6.00 of 20 April 2009, by Info-ZIP": "6.00",
            "GNU Wget 1.25.0 在 darwin25.2.0 上编译。": "1.25.0",
            "GNU bash，版本 5.3.15(1)-release (aarch64-apple-darwin25.4.0)": "5.3.15",
            'openjdk version "24" 2025-03-18': "24",
        }
        for text, expected in samples.items():
            with self.subTest(text=text):
                self.assertEqual(probe_runtimes.extract_version(text), expected)

    def test_only_first_line_is_read(self):
        self.assertEqual(probe_runtimes.extract_version("rustup 1.28.2\ninfo: 9.9.9"), "1.28.2")

    def test_versionless_output_returns_none(self):
        self.assertIsNone(probe_runtimes.extract_version("command not found"))
        self.assertIsNone(probe_runtimes.extract_version(""))

    def test_version_comparison_handles_short_minimum(self):
        self.assertTrue(probe_runtimes.version_at_least("26.5.0", "22"))
        self.assertTrue(probe_runtimes.version_at_least("22.0.0", "22"))
        self.assertFalse(probe_runtimes.version_at_least("18.20.0", "22"))


class RuntimeTableTests(unittest.TestCase):
    def test_version_flags_match_measured_behaviour(self):
        """统一 `--version` 会挂：go 退出码 2，unzip 无长参数，java 只认 -version。"""
        self.assertEqual(runtime_args("go"), ("version",))
        self.assertEqual(runtime_args("unzip"), ("-v",))
        self.assertEqual(runtime_args("java"), ("-version",))
        self.assertEqual(runtime_args("node"), ("--version",))

    def test_every_runtime_declares_a_known_category(self):
        for name, category, args in probe_runtimes.RUNTIMES:
            with self.subTest(runtime=name):
                self.assertIn(category, probe_runtimes.CATEGORIES)
                self.assertTrue(args)

    def test_ai_cli_channels_only_require_declared_runtimes(self):
        declared = {name for name, _, _ in probe_runtimes.RUNTIMES}
        for cli in probe_runtimes.AI_CLIS:
            for label, requires in cli["channels"]:
                for runtime, _minimum in requires:
                    with self.subTest(cli=cli["name"], channel=label):
                        self.assertIn(runtime, declared)

    def test_npm_node_thresholds_match_upstream_official_sources(self):
        """门槛取自各安装技能 references/official-sources.md 的「已核对事实」段。

        这些包在 package.json 里声明了 engines.node，装在低版本 Node 上会失败；
        门槛漏填会让低版本机器误判「可安装」。上游改版本要同步改这里和本断言。
        """
        expected = {
            "Claude Code": "22",       # @anthropic-ai/claude-code 声明 Node.js 22+
            "Kimi Code CLI": "22.19",  # @moonshot-ai/kimi-code 声明 Node.js 22.19+
            "Qoder CLI": "20",         # @qoder-ai/qodercli 声明 Node.js 20+
            "Deep Code CLI": "22",     # @vegamo/deepcode-cli 声明 Node.js 22+
        }
        found = {}
        for cli in probe_runtimes.AI_CLIS:
            for label, requires in cli["channels"]:
                if "npm" not in label:
                    continue
                for runtime, minimum in requires:
                    if runtime == "node" and minimum:
                        found[cli["name"]] = minimum
        self.assertEqual(found, expected)


class PlatformInfoTests(unittest.TestCase):
    def test_reports_os_arch_without_leaking_identity(self):
        host = probe_runtimes.platform_info()
        self.assertEqual(set(host), {"os", "arch", "os_version"})
        for value in host.values():
            self.assertIsInstance(value, str)
            self.assertTrue(value)
        home = probe_runtimes.os.path.expanduser("~")
        self.assertNotIn(home, str(host))
        self.assertNotIn(probe_runtimes.os.path.basename(home), str(host))


class DetectTests(unittest.TestCase):
    def test_missing_command_is_absent(self):
        with patch.object(probe_runtimes.shutil, "which", return_value=None):
            result = probe_runtimes.detect("yarn", "node", ("--version",), 1)
        self.assertEqual(result["status"], "absent")
        self.assertIsNone(result["version"])
        self.assertNotIn("path", result)

    def test_timeout_is_not_reported_as_absent(self):
        """rustc 是 rustup shim，冷启动可能超时；超时必须与「没装」分开。"""
        error = subprocess.TimeoutExpired(cmd="rustc", timeout=1)
        with patch.object(probe_runtimes.shutil, "which", return_value="/usr/local/bin/rustc"), \
             patch.object(probe_runtimes.subprocess, "run", side_effect=error):
            result = probe_runtimes.detect("rustc", "rust", ("--version",), 1)
        self.assertEqual(result["status"], "timeout")
        self.assertNotEqual(result["status"], "absent")

    def test_stderr_is_used_only_when_stdout_is_empty(self):
        with patch.object(probe_runtimes.shutil, "which", return_value="/usr/bin/java"), \
             patch.object(probe_runtimes.subprocess, "run",
                          return_value=Completed(stdout="", stderr='openjdk version "24" 2025-03-18')):
            result = probe_runtimes.detect("java", "jvm", ("-version",), 1)
        self.assertEqual(result["version"], "24")

    def test_stdout_wins_over_noisy_stderr(self):
        with patch.object(probe_runtimes.shutil, "which", return_value="/usr/local/bin/rustup"), \
             patch.object(probe_runtimes.subprocess, "run",
                          return_value=Completed(stdout="rustup 1.28.2", stderr="info: 9.9.9")):
            result = probe_runtimes.detect("rustup", "rust", ("--version",), 1)
        self.assertEqual(result["version"], "1.28.2")

    def test_home_prefix_is_redacted_and_body_is_dropped(self):
        home = probe_runtimes.os.path.expanduser("~")
        with patch.object(probe_runtimes.shutil, "which", return_value=f"{home}/.cargo/bin/cargo"), \
             patch.object(probe_runtimes.subprocess, "run",
                          return_value=Completed(stdout="cargo 1.92.0 (344c4567c 2025-10-21)")):
            result = probe_runtimes.detect("cargo", "rust", ("--version",), 1)
        self.assertEqual(result["path"], "~/.cargo/bin/cargo")
        self.assertNotIn(home, str(result))
        self.assertNotIn("344c4567c", str(result))

    def test_nonzero_exit_without_version_is_exec_failed(self):
        with patch.object(probe_runtimes.shutil, "which", return_value="/usr/bin/go"), \
             patch.object(probe_runtimes.subprocess, "run",
                          return_value=Completed(stderr="flag provided but not defined: -version", returncode=2)):
            result = probe_runtimes.detect("go", "go", ("--version",), 1)
        self.assertEqual(result["status"], "exec_failed")


class InstallabilityTests(unittest.TestCase):
    @staticmethod
    def verdicts(results):
        return {entry["name"]: entry["verdict"] for entry in probe_runtimes.installability(results)}

    @staticmethod
    def runtimes(**statuses):
        rows = []
        for name, category, _args in probe_runtimes.RUNTIMES:
            status, version = statuses.get(name, ("absent", None))
            rows.append({"name": name, "category": category, "status": status, "version": version})
        return rows

    def test_bare_machine_still_installs_standalone_clis(self):
        """裸机没有 node/npm/brew，只有硬依赖 Node 的 Pi 与 Deep Code 被阻塞。"""
        verdicts = self.verdicts(self.runtimes())
        self.assertEqual(verdicts["Claude Code"], "可安装")
        self.assertEqual(verdicts["WorkBuddy"], "可安装")
        self.assertEqual(verdicts["Pi"], "被阻塞")
        self.assertEqual(verdicts["Deep Code CLI"], "被阻塞")

    def test_old_node_blocks_only_the_version_gated_cli(self):
        rows = self.runtimes(node=("available", "18.20.0"), npm=("available", "10.8.2"))
        verdicts = self.verdicts(rows)
        self.assertEqual(verdicts["Pi"], "可安装")
        self.assertEqual(verdicts["Deep Code CLI"], "被阻塞")
        blocked = next(e for e in probe_runtimes.installability(rows) if e["name"] == "Deep Code CLI")
        self.assertIn("node 18.20.0 < 22", blocked["channels"][0]["blockers"])

    def test_node_20_splits_the_pkg_channel_by_threshold(self):
        """Node 20 满足 Qoder 但不满足 Claude/Kimi/Deep Code——门槛漏填就会全判可装。"""
        rows = self.runtimes(node=("available", "20.19.0"), npm=("available", "10.8.2"))
        report = {entry["name"]: entry for entry in probe_runtimes.installability(rows)}

        def pkg_channel(name):
            return next(c for c in report[name]["channels"] if "npm" in c["label"])

        self.assertEqual(pkg_channel("Qoder CLI")["status"], "ok")
        self.assertEqual(pkg_channel("Claude Code")["status"], "blocked")
        self.assertIn("node 20.19.0 < 22", pkg_channel("Claude Code")["blockers"])
        self.assertIn("node 20.19.0 < 22.19", pkg_channel("Kimi Code CLI")["blockers"])
        # 官方独立安装渠道不受 Node 版本影响，整体仍判可安装。
        self.assertEqual(report["Claude Code"]["verdict"], "可安装")
        # Deep Code 只有 npm 一条渠道，没有兜底，直接被阻塞。
        self.assertEqual(report["Deep Code CLI"]["verdict"], "被阻塞")

    def test_timeout_downgrades_to_review_not_blocked(self):
        rows = self.runtimes(node=("timeout", None), npm=("available", "10.8.2"))
        self.assertEqual(self.verdicts(rows)["Pi"], "待复核")

    def test_homebrew_alone_unblocks_brew_capable_clis(self):
        rows = self.runtimes(brew=("available", "6.0.15"))
        report = {entry["name"]: entry for entry in probe_runtimes.installability(rows)}
        codex = report["Codex CLI"]
        self.assertEqual(codex["verdict"], "可安装")
        self.assertIn("Homebrew", [c["label"] for c in codex["channels"] if c["status"] == "ok"])


if __name__ == "__main__":
    unittest.main()
