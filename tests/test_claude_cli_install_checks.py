"""soia-env-claude-cli-install 专属自包含测试。

只引用本技能文件与 Python 标准库，离线可跑（网络接缝用注入的 fake opener）。
覆盖两条核心承诺：只读检查如实分类（已安装/未安装、配置未创建、~ 脱敏），
最新版查询走官方元数据且失败不猜测。支持仓布局与市场包布局双解析。
"""
import importlib.util
import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
_CANDIDATES = [ROOT / "skills" / "soia-env-claude-cli-install" / "scripts", ROOT / "scripts"]
SCRIPTS = next((d for d in _CANDIDATES if (d / "inspect_cli.py").exists()), None)
if SCRIPTS is None:
    raise FileNotFoundError(f"找不到 inspect_cli.py：仓布局与包布局均不存在（尝试 {_CANDIDATES}）")


def load_module(name):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


check_latest = load_module("check_latest")

STUB_VERSION = "9.9.9"
SYSTEM_PATH = "/usr/bin:/bin:/usr/sbin:/sbin"


class FakeResponse:
    def __init__(self, payload):
        self._payload = json.dumps(payload).encode()

    def read(self, *a):
        return self._payload

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


class CheckLatestTests(unittest.TestCase):
    def test_npm_source_url_targets_official_registry(self):
        url = check_latest.source_url({"type": "npm", "package": "@anthropic-ai/claude-code"})
        self.assertEqual(url, "https://registry.npmjs.org/%40anthropic-ai%2Fclaude-code/latest")

    def test_unsupported_source_rejected(self):
        with self.assertRaises(ValueError):
            check_latest.source_url({"type": "carrier-pigeon"})

    def test_check_uses_injected_opener_and_strips_v_prefix(self):
        profile = {"display_name": "Claude Code CLI",
                   "latest": {"type": "npm", "package": "@anthropic-ai/claude-code"}}
        result = check_latest.check(
            profile, opener=lambda req, timeout: FakeResponse({"version": f"v{STUB_VERSION}"}))
        self.assertEqual(result["latest_version"], STUB_VERSION)
        self.assertEqual(result["status"], "available")
        self.assertEqual(result["source"], "npm")

    def test_github_tag_extraction(self):
        self.assertEqual(
            check_latest.extract_version("github", {"tag_name": "v1.2.3"}), "1.2.3")

    def test_missing_version_is_error_not_guess(self):
        with self.assertRaises(ValueError):
            check_latest.extract_version("npm", {"unexpected": True})


class InspectCliTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(prefix="claude-cli-install-test.")
        self.workdir = pathlib.Path(self._tmp.name)
        (self.workdir / "home").mkdir()

    def tearDown(self):
        self._tmp.cleanup()

    def run_inspect(self, path_dirs):
        env = {
            "HOME": str(self.workdir / "home"),
            "PATH": os.pathsep.join(path_dirs + [SYSTEM_PATH]),
            "TMPDIR": str(self.workdir),
        }
        return subprocess.run(
            [sys.executable, str(SCRIPTS / "inspect_cli.py"), "--json"],
            env=env, capture_output=True, text=True, timeout=60)

    def test_stub_binary_reported_installed_with_version(self):
        stub_dir = self.workdir / "bin"
        stub_dir.mkdir()
        stub = stub_dir / "claude"
        stub.write_text("#!/bin/sh\n"
                        f'if [ "$1" = "--version" ]; then echo "{STUB_VERSION} (Claude Code)"; exit 0; fi\n'
                        "exit 0\n")
        stub.chmod(stub.stat().st_mode | stat.S_IXUSR)
        result = self.run_inspect([str(stub_dir)])
        self.assertEqual(result.returncode, 0, result.stderr)
        data = json.loads(result.stdout)
        self.assertEqual(data["current_status"], "已安装")
        self.assertEqual(data["current_version"], STUB_VERSION)
        self.assertIn(str(stub_dir), data["command_path"])
        self.assertEqual(data["config_status"], "未创建", "临时 HOME 里不得把默认路径当已配置")
        self.assertTrue(str(data["config_path"]).startswith("~"),
                        "配置路径必须 ~ 脱敏，不暴露用户名")
        home = str(self.workdir / "home")
        self.assertNotIn(home, data["config_path"])

    def test_missing_binary_reported_not_installed(self):
        result = self.run_inspect([])
        data = json.loads(result.stdout)
        self.assertEqual(data["current_status"], "未安装")


if __name__ == "__main__":
    unittest.main()
