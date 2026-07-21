import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "audit_skill_output.py"


def run_summary(summary):
    return subprocess.run(
        [sys.executable, str(SCRIPT)],
        input=json.dumps(summary),
        text=True,
        capture_output=True,
        check=False,
    )


def valid_summary():
    return {
        "schema_version": 2,
        "checked_at": "2026-07-21T00:00:00+08:00",
        "os": "macos",
        "arch": "arm64",
        "shell": "zsh",
        "tools": {
            name: {"status": "ready", "version": "1.0"}
            for name in ("node", "python", "codex", "workbuddy")
        },
        "network": {"status": "ready", "checked_sources": 2},
        "blockers": [],
        "next_handoff": "soia-open-skills",
    }


class ReadinessSummaryTests(unittest.TestCase):
    def test_valid_summary_passes(self):
        result = run_summary(valid_summary())
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["valid"], True)

    def test_missing_tool_status_fails(self):
        summary = valid_summary()
        del summary["tools"]["python"]["status"]
        result = run_summary(summary)
        self.assertEqual(result.returncode, 1)
        self.assertIn("tools.python.status", result.stdout)

    def test_update_available_status_passes(self):
        summary = valid_summary()
        summary["tools"]["codex"]["status"] = "update_available"
        result = run_summary(summary)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(json.loads(result.stdout)["valid"], True)

    def test_requested_optional_ai_cli_status_passes(self):
        summary = valid_summary()
        summary["tools"]["claude"] = {"status": "ready", "version": "2.1.216"}
        summary["tools"]["deepcode"] = {"status": "missing", "version": None}
        result = run_summary(summary)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_unknown_or_invalid_ai_cli_status_fails(self):
        summary = valid_summary()
        summary["tools"]["claude"] = {"status": "running", "version": "1.0"}
        summary["tools"]["unknown-cli"] = {"status": "ready", "version": "1.0"}
        result = run_summary(summary)
        self.assertEqual(result.returncode, 1)
        self.assertIn("tools.claude.status", result.stdout)
        self.assertIn("tools.unknown-cli is unsupported", result.stdout)

    def test_timestamp_requires_an_explicit_timezone(self):
        summary = valid_summary()
        summary["checked_at"] = "2026-07-21T00:00:00"
        result = run_summary(summary)
        self.assertEqual(result.returncode, 1)
        self.assertIn("explicit timezone", result.stdout)

    def test_missing_timestamp_fails(self):
        summary = valid_summary()
        del summary["checked_at"]
        result = run_summary(summary)
        self.assertEqual(result.returncode, 1)
        self.assertIn("missing field: checked_at", result.stdout)


if __name__ == "__main__":
    unittest.main()
