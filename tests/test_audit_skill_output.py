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
        "schema_version": 1,
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


if __name__ == "__main__":
    unittest.main()
