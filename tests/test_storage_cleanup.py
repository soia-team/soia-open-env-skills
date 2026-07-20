import importlib.util
import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "soia-env-storage-cleanup" / "scripts" / "storage_cleanup.py"
SPEC = importlib.util.spec_from_file_location("storage_cleanup", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class StorageCleanupTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.roots = {
            kind: self.base / kind
            for kind in ("config", "state", "cache", "temp")
        }
        for path in self.roots.values():
            path.mkdir(parents=True)
        self.now = datetime(2026, 7, 21, 8, 0, tzinfo=timezone.utc)

    def tearDown(self):
        self.temporary.cleanup()

    def write_file(self, path: Path, content: str = "data", age_days: float = 0) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        timestamp = (self.now - timedelta(days=age_days)).timestamp()
        os.utime(path, (timestamp, timestamp))
        return path

    def write_state_marker(self, directory: Path, *, cleanup_allowed=True) -> Path:
        marker = directory / MODULE.MANAGED_MARKER
        self.write_file(
            marker,
            json.dumps(
                {
                    "schema_version": 1,
                    "owner_skill": "soia-env-fixture",
                    "data_class": "audit_state",
                    "retention_days": 30,
                    "cleanup_allowed": cleanup_allowed,
                }
            ),
        )
        return marker

    def build_fixture_plan(self):
        config = self.write_file(self.roots["config"] / "config.yml", age_days=90)
        cache_old = self.write_file(self.roots["cache"] / "old.cache", "old-cache", age_days=8)
        cache_new = self.write_file(self.roots["cache"] / "new.cache", "new-cache", age_days=1)
        temp_old = self.write_file(self.roots["temp"] / "run-old" / "download.tmp", age_days=2)
        temp_new = self.write_file(self.roots["temp"] / "run-new" / "download.tmp", age_days=0)
        state_dir = self.roots["state"] / "soia-env-fixture"
        self.write_state_marker(state_dir)
        state_old = self.write_file(state_dir / "old-receipt.json", age_days=31)
        state_new = self.write_file(state_dir / "new-receipt.json", age_days=1)
        plan = MODULE.build_plan(
            self.roots,
            temp_days=1,
            cache_days=7,
            state_days=30,
            cache_max_bytes=1024 * 1024,
            now=self.now,
        )
        return plan, {
            "config": config,
            "cache_old": cache_old,
            "cache_new": cache_new,
            "temp_old": temp_old,
            "temp_new": temp_new,
            "state_old": state_old,
            "state_new": state_new,
        }

    def write_plan(self, plan, name="plan.json") -> Path:
        path = self.roots["state"] / "cleanup" / name
        MODULE.atomic_write_private_json(path, plan, self.roots["state"])
        return path

    def execute(
        self,
        plan,
        plan_path,
        *,
        now=None,
        acknowledgement=None,
        digest=None,
        confirmed_plan_id=None,
    ):
        return MODULE.execute_plan(
            plan_path,
            self.roots,
            expected_digest=digest or plan["plan_digest"],
            confirmed_plan_id=confirmed_plan_id or plan["plan_id"],
            authorization_id="auth-fixture-0001",
            authorized_at=(self.now + timedelta(minutes=1)).isoformat(),
            acknowledgement=acknowledgement or MODULE.ACKNOWLEDGEMENT,
            now=now or self.now + timedelta(minutes=2),
        )

    def test_scan_classifies_only_expired_managed_files(self):
        plan, paths = self.build_fixture_plan()
        candidates = {Path(item["path"]) for item in plan["candidates"]}
        self.assertEqual(
            candidates,
            {paths["cache_old"], paths["temp_old"], paths["state_old"]},
        )
        self.assertNotIn(paths["config"], candidates)
        self.assertNotIn(paths["cache_new"], candidates)
        self.assertNotIn(paths["temp_new"], candidates)
        self.assertNotIn(paths["state_new"], candidates)
        self.assertTrue(plan["authorization_required"])
        self.assertEqual(plan["plan_digest"], MODULE.digest_mapping(plan, "plan_digest"))

    def test_state_without_enabled_marker_is_not_cleanable(self):
        state_dir = self.roots["state"] / "soia-env-unmanaged"
        old = self.write_file(state_dir / "old.json", age_days=90)
        plan = MODULE.build_plan(self.roots, now=self.now)
        self.assertNotIn(old, {Path(item["path"]) for item in plan["candidates"]})

        self.write_state_marker(state_dir, cleanup_allowed=False)
        plan = MODULE.build_plan(self.roots, now=self.now)
        self.assertNotIn(old, {Path(item["path"]) for item in plan["candidates"]})

    def test_active_directory_and_symlink_are_blocked(self):
        active_dir = self.roots["temp"] / "active-run"
        old = self.write_file(active_dir / "old.tmp", age_days=5)
        self.write_file(active_dir / MODULE.ACTIVE_MARKER, age_days=0)
        outside = self.write_file(self.base / "outside.txt", age_days=10)
        link = self.roots["temp"] / "outside-link"
        try:
            link.symlink_to(outside)
        except OSError:
            self.skipTest("symlinks are unavailable on this platform")

        plan = MODULE.build_plan(self.roots, now=self.now)
        candidates = {Path(item["path"]) for item in plan["candidates"]}
        self.assertNotIn(old, candidates)
        self.assertNotIn(link, candidates)
        reasons = {item["reason"] for item in plan["blocked"]}
        self.assertIn("active_run_marker", reasons)
        self.assertIn("symlink_file", reasons)

    def test_cache_capacity_selects_oldest_files_until_under_limit(self):
        oldest = self.write_file(self.roots["cache"] / "a.cache", "12345", age_days=2)
        newer = self.write_file(self.roots["cache"] / "b.cache", "67890", age_days=1)
        plan = MODULE.build_plan(
            self.roots,
            cache_days=30,
            cache_max_bytes=5,
            now=self.now,
        )
        candidates = {Path(item["path"]): item for item in plan["candidates"]}
        self.assertIn(oldest, candidates)
        self.assertNotIn(newer, candidates)
        self.assertEqual(candidates[oldest]["reasons"], ["cache_capacity"])

    def test_state_count_limit_selects_oldest_marked_receipt(self):
        state_dir = self.roots["state"] / "soia-env-fixture"
        self.write_state_marker(state_dir)
        oldest = self.write_file(state_dir / "a.json", age_days=3)
        self.write_file(state_dir / "b.json", age_days=2)
        self.write_file(state_dir / "c.json", age_days=1)
        plan = MODULE.build_plan(
            self.roots,
            state_days=30,
            state_max_files=2,
            state_max_bytes=1024 * 1024,
            now=self.now,
        )
        candidates = {Path(item["path"]): item for item in plan["candidates"]}
        self.assertIn(oldest, candidates)
        self.assertEqual(candidates[oldest]["reasons"], ["state_count"])

    def test_execution_requires_exact_authorization_and_digest(self):
        plan, _ = self.build_fixture_plan()
        plan_path = self.write_plan(plan)
        with self.assertRaisesRegex(MODULE.CleanupError, "acknowledgement"):
            self.execute(plan, plan_path, acknowledgement="yes")
        with self.assertRaisesRegex(MODULE.CleanupError, "digest mismatch"):
            self.execute(plan, plan_path, digest="0" * 64)
        with self.assertRaisesRegex(MODULE.CleanupError, "plan_id does not match"):
            self.execute(plan, plan_path, confirmed_plan_id="cleanup-wrong-plan")

    def test_expired_plan_requires_fresh_scan_and_authorization(self):
        plan, _ = self.build_fixture_plan()
        plan_path = self.write_plan(plan)
        with self.assertRaisesRegex(MODULE.CleanupError, "expired"):
            self.execute(plan, plan_path, now=self.now + timedelta(minutes=31))

    def test_authorized_execution_deletes_only_planned_files_and_verifies(self):
        plan, paths = self.build_fixture_plan()
        plan_path = self.write_plan(plan)
        receipt = self.execute(plan, plan_path)

        self.assertEqual(receipt["status"], "completed")
        self.assertEqual(receipt["deleted_files"], 3)
        for key in ("cache_old", "temp_old", "state_old"):
            self.assertFalse(paths[key].exists())
        for key in ("config", "cache_new", "temp_new", "state_new"):
            self.assertTrue(paths[key].exists())

        receipt_path = Path(receipt["receipt_path"])
        self.assertTrue(receipt_path.is_file())
        verification = MODULE.verify_receipt(receipt_path, self.roots)
        self.assertTrue(verification["valid"])
        self.assertEqual(verification["deleted_files"], 3)

    def test_changed_candidate_is_skipped_instead_of_reinterpreted(self):
        old = self.write_file(self.roots["cache"] / "old.cache", age_days=8)
        plan = MODULE.build_plan(self.roots, cache_days=7, now=self.now)
        plan_path = self.write_plan(plan)
        old.write_text("changed-after-plan", encoding="utf-8")

        receipt = self.execute(plan, plan_path)
        self.assertEqual(receipt["status"], "completed_with_skips")
        self.assertEqual(receipt["deleted_files"], 0)
        self.assertTrue(old.exists())
        self.assertIn("changed after planning", receipt["skipped"][0]["reason"])

    def test_plan_and_receipt_files_are_immutable(self):
        plan, _ = self.build_fixture_plan()
        path = self.write_plan(plan)
        with self.assertRaisesRegex(MODULE.CleanupError, "refusing to overwrite"):
            MODULE.atomic_write_private_json(path, plan, self.roots["state"])

    def test_custom_root_requires_an_exact_managed_root_marker(self):
        env = {"SOIA_SKILLS_CACHE_HOME": str(self.roots["cache"])}
        with self.assertRaisesRegex(MODULE.CleanupError, "requires"):
            MODULE.validate_custom_roots(self.roots, env)

        marker = self.roots["cache"] / MODULE.ROOT_MARKER
        marker.write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "managed_by": "soia-skills",
                    "root_kind": "cache",
                }
            ),
            encoding="utf-8",
        )
        MODULE.validate_custom_roots(self.roots, env)

        plan = MODULE.build_plan(self.roots, cache_days=0, now=self.now)
        self.assertNotIn(marker, {Path(item["path"]) for item in plan["candidates"]})


if __name__ == "__main__":
    unittest.main()
