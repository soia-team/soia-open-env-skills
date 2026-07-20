import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (
    ROOT
    / "skills"
    / "soia-env-codex-install"
    / "scripts"
    / "inspect_installation.py"
)
SPEC = importlib.util.spec_from_file_location("codex_installation_inspection", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CodexInstallationInspectionTests(unittest.TestCase):
    def test_classifies_chatgpt_bundled_cli(self):
        command = Path("/Applications/ChatGPT.app/Contents/Resources/codex")
        method, directory = MODULE.classify_installation(command, command, None)
        self.assertEqual(method, "ChatGPT.app 内置（非独立 CLI）")
        self.assertEqual(directory, command.parent)

    def test_classifies_npm_global_cli(self):
        npm_root = Path("/home/example/.npm-global/lib/node_modules")
        command = Path("/home/example/.npm-global/bin/codex")
        resolved = npm_root / "@openai" / "codex" / "bin" / "codex.js"
        method, directory = MODULE.classify_installation(command, resolved, npm_root)
        self.assertEqual(method, "npm 全局安装")
        self.assertEqual(directory, npm_root / "@openai" / "codex")

    def test_selects_independent_cli_instead_of_chatgpt_app_binary(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            app_cli = root / "ChatGPT.app" / "Contents" / "Resources" / "codex"
            npm_cli = root / ".npm-global" / "bin" / "codex"
            app_cli.parent.mkdir(parents=True)
            npm_cli.parent.mkdir(parents=True)
            app_cli.write_text("#!/bin/sh\n", encoding="utf-8")
            npm_cli.write_text("#!/bin/sh\n", encoding="utf-8")
            app_cli.chmod(0o755)
            npm_cli.chmod(0o755)

            selected, detected_app = MODULE.select_independent_cli(
                [app_cli, npm_cli]
            )

            self.assertEqual(selected, npm_cli)
            self.assertEqual(detected_app, app_cli)

    def test_app_binary_alone_does_not_count_as_standalone_cli(self):
        with tempfile.TemporaryDirectory() as temp:
            app_cli = (
                Path(temp)
                / "ChatGPT.app"
                / "Contents"
                / "Resources"
                / "codex"
            )
            app_cli.parent.mkdir(parents=True)
            app_cli.write_text("#!/bin/sh\n", encoding="utf-8")
            app_cli.chmod(0o755)

            selected, detected_app = MODULE.select_independent_cli([app_cli])

            self.assertIsNone(selected)
            self.assertEqual(detected_app, app_cli)

    def test_inspection_reports_cli_missing_when_only_app_binary_exists(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            app_cli = (
                home
                / "ChatGPT.app"
                / "Contents"
                / "Resources"
                / "codex"
            )
            app_cli.parent.mkdir(parents=True)
            app_cli.write_text("#!/bin/sh\n", encoding="utf-8")
            app_cli.chmod(0o755)

            with (
                mock.patch.object(MODULE.Path, "home", return_value=home),
                mock.patch.object(MODULE, "npm_root", return_value=None),
                mock.patch.object(
                    MODULE,
                    "candidate_paths",
                    return_value=[app_cli],
                ),
            ):
                result = MODULE.inspect()

            self.assertEqual(result["current_status"], "未安装")
            self.assertEqual(result["cli_path"], "未取得")
            self.assertEqual(result["app_detected"], "是")

    def test_collapses_home_directory(self):
        home = Path("/home/example")
        self.assertEqual(
            MODULE.home_relative(home / ".codex", home),
            "~/.codex",
        )


if __name__ == "__main__":
    unittest.main()
