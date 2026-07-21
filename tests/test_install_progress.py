import importlib.util
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_SCRIPT = (
    ROOT / "templates" / "skill-template" / "scripts" / "record_install_progress.py"
)
SPEC = importlib.util.spec_from_file_location("install_progress", TEMPLATE_SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)

INSTALL_SKILLS = (
    "soia-env-codex-install",
    "soia-env-codex-setup-support",
    "soia-env-node-install",
    "soia-env-python-install",
    "soia-env-workbuddy-install",
)
PROGRESS_HEADER = "| 阶段 | 当前状态 | 更新时间 | 处理结果 |"


class InstallProgressTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.state_home = Path(self.temporary.name) / "state"
        self.env = {"SOIA_SKILLS_STATE_HOME": str(self.state_home)}
        self.skill = "soia-env-node-install"
        self.run_id = "install-fixture-0001"

    def tearDown(self):
        self.temporary.cleanup()

    def append(self, stage, status, *, latest=False, result_code=None):
        default_codes = {
            "checking": "checking_started",
            "planning": "plan_ready",
            "waiting_confirmation": "waiting_customer_confirmation",
            "installing": "installation_started",
            "updating": "update_started",
            "verifying": "verification_started",
            "completed": "operation_completed",
            "failed": "operation_failed",
            "blocked": "operation_blocked",
        }
        return MODULE.append_event(
            skill_name=self.skill,
            run_id=self.run_id,
            action="update",
            stage=stage,
            status=status,
            result_code=result_code or default_codes[stage],
            customer_requested_latest=latest,
            env=self.env,
            home=Path(self.temporary.name) / "home",
            platform_name="linux",
        )

    def test_read_only_path_resolution_does_not_create_state(self):
        path = MODULE.state_directory(
            self.skill,
            env=self.env,
            home=Path(self.temporary.name) / "home",
            platform_name="linux",
        )
        self.assertFalse(path.exists())
        self.assertFalse(self.state_home.exists())

    def test_update_cannot_enter_execution_without_explicit_latest_request(self):
        _, path = self.append("checking", "in_progress")
        with self.assertRaisesRegex(MODULE.ProgressError, "explicit customer request"):
            self.append("updating", "in_progress")
        self.assertEqual(len(path.read_text(encoding="utf-8").splitlines()), 1)

    def test_invalid_first_stage_does_not_create_state(self):
        with self.assertRaisesRegex(MODULE.ProgressError, "first progress stage"):
            self.append("planning", "in_progress")
        self.assertFalse(self.state_home.exists())

    def test_rejects_path_like_identity_and_relative_state_root(self):
        with self.assertRaisesRegex(MODULE.ProgressError, "canonical soia-env"):
            MODULE.append_event(
                skill_name="soia-env-../../escape",
                run_id=self.run_id,
                action="install",
                stage="checking",
                status="in_progress",
                result_code="checking_started",
                env=self.env,
            )
        with self.assertRaisesRegex(MODULE.ProgressError, "opaque"):
            MODULE.append_event(
                skill_name=self.skill,
                run_id="bad:run-id",
                action="install",
                stage="checking",
                status="in_progress",
                result_code="checking_started",
                env=self.env,
            )
        with self.assertRaisesRegex(MODULE.ProgressError, "absolute path"):
            MODULE.state_directory(
                self.skill,
                env={"SOIA_SKILLS_STATE_HOME": "relative/state"},
                home=Path(self.temporary.name) / "home",
                platform_name="linux",
            )
        self.assertFalse(self.state_home.exists())

    def test_latest_authorization_flag_is_rejected_for_install(self):
        with self.assertRaisesRegex(MODULE.ProgressError, "only to updates"):
            MODULE.append_event(
                skill_name=self.skill,
                run_id=self.run_id,
                action="install",
                stage="checking",
                status="in_progress",
                result_code="checking_started",
                customer_requested_latest=True,
                env=self.env,
            )
        self.assertFalse(self.state_home.exists())

    def test_success_cannot_skip_planning_execution_or_verification(self):
        self.append("checking", "in_progress")
        with self.assertRaisesRegex(MODULE.ProgressError, "invalid progress transition"):
            self.append("updating", "in_progress", latest=True)
        with self.assertRaisesRegex(MODULE.ProgressError, "invalid progress transition"):
            self.append("completed", "completed", latest=True)

    def test_waiting_confirmation_is_a_nonterminal_progress_stage(self):
        self.append("checking", "in_progress")
        self.append("planning", "in_progress")
        self.append("waiting_confirmation", "waiting")
        self.append("updating", "in_progress", latest=True)
        self.append("verifying", "in_progress", latest=True)
        event, _ = self.append("completed", "completed", latest=True)
        self.assertEqual(event["status"], "completed")

    def test_records_complete_authorized_update_with_private_marker(self):
        self.append("checking", "in_progress")
        self.append("planning", "in_progress")
        self.append("updating", "in_progress", latest=True)
        self.append("verifying", "in_progress", latest=True)
        event, path = self.append("completed", "completed", latest=True)

        lines = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
        self.assertEqual([item["stage"] for item in lines], [
            "checking", "planning", "updating", "verifying", "completed"
        ])
        self.assertTrue(event["customer_requested_latest"])
        marker = path.parents[1] / MODULE.MARKER_NAME
        self.assertEqual(
            json.loads(marker.read_text(encoding="utf-8"))["owner_skill"],
            self.skill,
        )
        if hasattr(stat, "S_IMODE"):
            self.assertEqual(stat.S_IMODE(path.stat().st_mode), 0o600)
        with self.assertRaisesRegex(MODULE.ProgressError, "terminal"):
            self.append("verifying", "in_progress", latest=True)

    def test_rejects_free_form_or_mismatched_result_before_writing_state(self):
        with self.assertRaisesRegex(MODULE.ProgressError, "does not match"):
            self.append(
                "checking",
                "in_progress",
                result_code="operation_completed",
            )
        self.assertFalse(self.state_home.exists())

    def test_rejects_mismatched_execution_stage(self):
        with self.assertRaisesRegex(MODULE.ProgressError, "must use the updating stage"):
            MODULE.append_event(
                skill_name=self.skill,
                run_id=self.run_id,
                action="update",
                stage="installing",
                status="in_progress",
                result_code="installation_started",
                customer_requested_latest=True,
                env=self.env,
            )

    def test_each_install_skill_carries_the_same_standalone_recorder(self):
        expected = TEMPLATE_SCRIPT.read_bytes()
        for skill in INSTALL_SKILLS:
            with self.subTest(skill=skill):
                script = ROOT / "skills" / skill / "scripts" / "record_install_progress.py"
                self.assertEqual(script.read_bytes(), expected)

    def test_cli_prints_a_customer_visible_progress_table(self):
        env = os.environ.copy()
        env["SOIA_SKILLS_STATE_HOME"] = str(self.state_home)
        process = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_SCRIPT),
                "--skill-name",
                self.skill,
                "--run-id",
                "cli-fixture-0001",
                "--action",
                "install",
                "--stage",
                "checking",
                "--status",
                "in_progress",
                "--result-code",
                "checking_started",
            ],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        self.assertIn(PROGRESS_HEADER, process.stdout)
        self.assertRegex(
            process.stdout,
            r"\| 检查 \| 进行中 \| \d{4}-\d{2}-\d{2}T[^|]+[+-]\d{2}:\d{2} \| 正在检查环境与安装来源 \|",
        )

    def test_recorder_owns_timestamps_and_json_hides_state_path(self):
        env = os.environ.copy()
        env["SOIA_SKILLS_STATE_HOME"] = str(self.state_home)
        process = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_SCRIPT),
                "--skill-name",
                self.skill,
                "--run-id",
                "json-fixture-0001",
                "--action",
                "install",
                "--stage",
                "checking",
                "--status",
                "in_progress",
                "--result-code",
                "checking_started",
                "--json",
            ],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(process.returncode, 0, process.stderr)
        payload = json.loads(process.stdout)
        self.assertNotIn("record_path", payload)
        self.assertIsNotNone(MODULE.parse_rfc3339(payload["checked_at"]))

        rejected = subprocess.run(
            [
                sys.executable,
                str(TEMPLATE_SCRIPT),
                "--skill-name",
                self.skill,
                "--run-id",
                "json-fixture-0002",
                "--action",
                "install",
                "--stage",
                "checking",
                "--status",
                "in_progress",
                "--result-code",
                "checking_started",
                "--checked-at",
                "2026-01-01T00:00:00+08:00",
            ],
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(rejected.returncode, 0)

    def test_timestamps_are_monotonic_and_run_action_cannot_change(self):
        self.append("checking", "in_progress")
        self.append("planning", "in_progress")
        _, path = self.append("updating", "in_progress", latest=True)
        timestamps = [
            MODULE.parse_rfc3339(json.loads(line)["checked_at"])
            for line in path.read_text(encoding="utf-8").splitlines()
        ]
        self.assertEqual(timestamps, sorted(timestamps))
        self.assertEqual(len(timestamps), len(set(timestamps)))
        with self.assertRaisesRegex(MODULE.ProgressError, "action changed"):
            MODULE.append_event(
                skill_name=self.skill,
                run_id=self.run_id,
                action="repair",
                stage="verifying",
                status="in_progress",
                result_code="verification_started",
                env=self.env,
            )

    def test_updateable_skills_require_latest_intent_and_live_progress(self):
        for skill in INSTALL_SKILLS:
            with self.subTest(skill=skill):
                text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("更新到最新", text)
                self.assertIn("record_install_progress.py", text)
                self.assertIn(PROGRESS_HEADER, text)

        orchestrator = (
            ROOT / "skills" / "soia-env-environment-setup" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("没有这句明确选择，不调用更新器", orchestrator)
        self.assertIn("持续追加阶段状态", orchestrator)

        codex = (
            ROOT / "skills" / "soia-env-codex-install" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("TOOLS=codex DRY_RUN=1", codex)
        self.assertIn("安装请求只授权安装缺失的 CLI，不授权更新现有 CLI", codex)


if __name__ == "__main__":
    unittest.main()
