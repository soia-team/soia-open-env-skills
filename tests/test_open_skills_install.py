"""Tests for the soia-env-open-skills-install inspect script."""

import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

_spec = importlib.util.spec_from_file_location(
    "inspect_soia_plugins",
    Path(__file__).parent.parent
    / "skills"
    / "soia-env-open-skills-install"
    / "scripts"
    / "inspect_soia_plugins.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)


class TestCheckClaude(unittest.TestCase):
    def test_claude_not_found(self):
        with patch("shutil.which", return_value=None):
            result = _mod.check_claude()
        self.assertFalse(result["available"])

    def test_claude_no_plugins(self):
        with patch("shutil.which", return_value="/usr/bin/claude"), \
             patch.object(_mod, "_run", return_value=(0, "Installed plugins:\n", "")):
            result = _mod.check_claude()
        self.assertTrue(result["available"])
        self.assertEqual(result["plugins"], [])
        self.assertFalse(result["market_connected"])

    def test_claude_with_soia_plugin(self):
        fake_out = (
            "Installed plugins:\n"
            "  ❯ soia-meta@soia\n"
            "    Version: 1.8.0\n"
            "    Status: ✘ disabled\n"
        )
        with patch("shutil.which", return_value="/usr/bin/claude"), \
             patch.object(_mod, "_run", return_value=(0, fake_out, "")):
            result = _mod.check_claude()
        self.assertTrue(result["available"])
        self.assertTrue(result["market_connected"])
        self.assertEqual(len(result["plugins"]), 1)
        self.assertEqual(result["plugins"][0]["name"], "soia-meta")

    def test_claude_list_failure_reports_disconnected(self):
        with patch("shutil.which", return_value="/usr/bin/claude"), \
             patch.object(_mod, "_run", return_value=(1, "", "boom")):
            result = _mod.check_claude()
        self.assertTrue(result["available"])
        self.assertFalse(result["market_connected"])


class TestCheckCodex(unittest.TestCase):
    def test_codex_not_found(self):
        with patch("shutil.which", return_value=None):
            result = _mod.check_codex()
        self.assertFalse(result["available"])

    def test_codex_with_soia_plugin(self):
        with patch("shutil.which", return_value="/usr/bin/codex"), \
             patch.object(_mod, "_run", return_value=(0, "soia-env@soia\n", "")):
            result = _mod.check_codex()
        self.assertTrue(result["market_connected"])
        self.assertEqual(result["plugins"][0]["name"], "soia-env")


class TestCheckWorkbuddy(unittest.TestCase):
    def test_no_workbuddy_dir(self):
        with tempfile.TemporaryDirectory() as tmp:
            with patch("pathlib.Path.home", return_value=Path(tmp)):
                result = _mod.check_workbuddy()
        self.assertFalse(result["available"])

    def test_workbuddy_with_experts(self):
        with tempfile.TemporaryDirectory() as tmp:
            wb = Path(tmp) / "Library/Application Support/WorkBuddy/my-experts"
            wb.mkdir(parents=True)
            (wb / "soia-meta").mkdir()
            with patch("pathlib.Path.home", return_value=Path(tmp)):
                result = _mod.check_workbuddy()
        self.assertTrue(result["available"])
        self.assertIn("soia-meta", result["experts"])


if __name__ == "__main__":
    unittest.main()
