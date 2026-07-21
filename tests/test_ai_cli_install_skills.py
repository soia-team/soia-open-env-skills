import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = {
    "soia-env-claude-cli-install": ("claude", "@anthropic-ai/claude-code", "npm"),
    "soia-env-qoder-cli-install": ("qodercli", "@qoder-ai/qodercli", "npm"),
    "soia-env-antigravity-cli-install": ("agy", "", "antigravity-manifest"),
    "soia-env-opencode-cli-install": ("opencode", "opencode-ai", "github"),
    "soia-env-kimi-cli-install": ("kimi", "@moonshot-ai/kimi-code", "npm"),
    "soia-env-deepcode-cli-install": ("deepcode", "@vegamo/deepcode-cli", "npm"),
}
STATUS_HEADER = (
    "| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | "
    "安装目录 | 配置文件目录 | 更新时间 | 处理结果 |"
)


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


INSPECT = load_module(
    ROOT / "skills" / "soia-env-claude-cli-install" / "scripts" / "inspect_cli.py",
    "ai_cli_inspect",
)
LATEST = load_module(
    ROOT / "skills" / "soia-env-claude-cli-install" / "scripts" / "check_latest.py",
    "ai_cli_latest",
)


class FakeResponse(io.StringIO):
    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class AiCliInstallSkillTests(unittest.TestCase):
    def test_profiles_bind_the_expected_command_package_and_latest_source(self):
        commands = set()
        for skill, (command, package, latest_type) in SKILLS.items():
            with self.subTest(skill=skill):
                profile = json.loads(
                    (ROOT / "skills" / skill / "references" / "cli-profile.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(profile["command"], command)
                self.assertEqual(profile["package_name"], package)
                self.assertEqual(profile["latest"]["type"], latest_type)
                commands.add(command)
        self.assertEqual(len(commands), len(SKILLS))

    def test_generic_scripts_and_progress_recorder_do_not_drift(self):
        canonical = ROOT / "skills" / "soia-env-claude-cli-install" / "scripts"
        names = ("inspect_cli.py", "check_latest.py", "render_status.py")
        recorder = ROOT / "templates" / "skill-template" / "scripts" / "record_install_progress.py"
        for skill in SKILLS:
            with self.subTest(skill=skill):
                scripts = ROOT / "skills" / skill / "scripts"
                for name in names:
                    self.assertEqual((scripts / name).read_bytes(), (canonical / name).read_bytes())
                self.assertEqual((scripts / "record_install_progress.py").read_bytes(), recorder.read_bytes())

    def test_fake_native_cli_is_detected_and_version_is_parsed(self):
        profile = json.loads(
            (
                ROOT
                / "skills"
                / "soia-env-antigravity-cli-install"
                / "references"
                / "cli-profile.json"
            ).read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            executable = root / "agy"
            executable.write_text("#!/bin/sh\nprintf 'agy version 1.2.3\\n'\n", encoding="utf-8")
            executable.chmod(0o755)
            result = INSPECT.inspect(profile, env={"PATH": str(root)}, home=root / "home")
        self.assertEqual(result["current_status"], "已安装")
        self.assertEqual(result["current_version"], "1.2.3")
        self.assertEqual(result["runtime_status"], "正常")
        self.assertEqual(result["package_identity"], "not_applicable")

    def test_npm_package_identity_mismatch_is_blocking(self):
        profile = json.loads(
            (
                ROOT
                / "skills"
                / "soia-env-deepcode-cli-install"
                / "references"
                / "cli-profile.json"
            ).read_text(encoding="utf-8")
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            npm = root / "npm"
            global_root = root / "global"
            npm.write_text(f"#!/bin/sh\nprintf '{global_root}\\n'\n", encoding="utf-8")
            npm.chmod(0o755)
            status, path = INSPECT.package_identity(
                profile,
                resolved=root / "node_modules" / "other" / "dist" / "cli.js",
                install_method="npm 全局安装",
                env={"PATH": str(root)},
                home=root / "home",
            )
        self.assertEqual(status, "mismatch")
        self.assertEqual(path, "未取得")

    def test_latest_response_shapes_are_parsed_without_network(self):
        fixtures = {
            "npm": ({"version": "1.2.3"}, "1.2.3"),
            "pypi": ({"info": {"version": "2.3.4"}}, "2.3.4"),
            "github": ({"tag_name": "v3.4.5"}, "3.4.5"),
            "antigravity-manifest": ({"version": "4.5.6"}, "4.5.6"),
        }
        for kind, (payload, expected) in fixtures.items():
            with self.subTest(kind=kind):
                self.assertEqual(LATEST.extract_version(kind, payload), expected)
                response = FakeResponse(json.dumps(payload))
                self.assertEqual(
                    LATEST.fetch_json("https://example.invalid/latest", opener=lambda *_a, **_k: response),
                    payload,
                )

    def test_skill_contracts_and_openai_prompts_are_complete(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                skill_dir = ROOT / "skills" / skill
                text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                metadata = (skill_dir / "agents" / "openai.yaml").read_text(encoding="utf-8")
                self.assertIn(STATUS_HEADER, text)
                self.assertIn("更新到最新", text)
                self.assertIn("record_install_progress.py", text)
                self.assertIn("## 私密信息与中间数据", text)
                self.assertIn(f"${skill}", metadata)
                if skill != "soia-env-deepcode-cli-install":
                    self.assertIn("不直接执行网络响应", text)

    def test_deepcode_identity_is_unambiguous(self):
        text = (
            ROOT / "skills" / "soia-env-deepcode-cli-install" / "SKILL.md"
        ).read_text(encoding="utf-8")
        sources = (
            ROOT
            / "skills"
            / "soia-env-deepcode-cli-install"
            / "references"
            / "official-sources.md"
        ).read_text(encoding="utf-8")
        for value in ("lessweb/deepcode-cli", "@vegamo/deepcode-cli", "Node.js 22"):
            self.assertIn(value, text)
        self.assertIn("不是 DeepSeek 官方组织发布的 CLI", sources)
        self.assertNotIn("deepcode-hku", text + sources)

    def test_renderer_outputs_exactly_one_ten_column_row(self):
        script = ROOT / "skills" / "soia-env-deepcode-cli-install" / "scripts" / "render_status.py"
        result = subprocess.run(
            [
                sys.executable,
                str(script),
                "--current-status",
                "已安装",
                "--current-version",
                "0.1.34",
                "--latest-version",
                "0.1.34",
                "--runtime-status",
                "正常",
                "--install-method",
                "npm 全局安装",
                "--install-dir",
                "~/.local/bin",
                "--config-dir",
                "~/.deepcode",
                "--updated-at",
                "2026-07-21T18:00:00+08:00",
                "--result",
                "已是最新",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(lines[0], STATUS_HEADER)
        self.assertEqual(len(lines), 3)
        self.assertIn("| Deep Code CLI | 已安装 |", lines[2])


if __name__ == "__main__":
    unittest.main()
