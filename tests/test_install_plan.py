"""Selection-plan tests; no test invokes a real installer or mutates a host."""

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "plan_install",
    ROOT / "skills/soia-env-open-skills-install/scripts/plan_install.py",
)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class InstallPlanTests(unittest.TestCase):
    def test_missing_selection_never_defaults_to_all(self):
        plan = MODULE.build_plan({})
        self.assertTrue(plan["selection_required"])
        self.assertTrue(plan["pending"])
        self.assertEqual(plan["agents"], [])
        self.assertEqual(plan["matrix"], [])
        self.assertEqual(plan["state"], "selection_required")

    def test_project_single_skill_for_one_agent(self):
        plan = MODULE.build_plan({
            "scope": "project",
            "agents": ["codex"],
            "target": {"kind": "skill", "name": "soia-env-open-skills-install"},
        })
        self.assertFalse(plan["selection_required"])
        self.assertTrue(plan["pending"])
        self.assertEqual(plan["state"], "confirmation_required")
        self.assertEqual(len(plan["matrix"]), 1)
        self.assertEqual(plan["matrix"][0]["agent"], "codex")
        self.assertEqual(plan["matrix"][0]["status"], "planned")

    def test_explicit_global_all_expands_all_agents_but_stays_plan_only(self):
        plan = MODULE.build_plan({
            "scope": "global",
            "agents": ["*"],
            "target": {"kind": "all"},
            "confirmed": True,
        })
        self.assertEqual(plan["agents"], ["claude", "codex", "workbuddy"])
        self.assertFalse(plan["selection_required"])
        self.assertFalse(plan["pending"])
        self.assertTrue(plan["plan_only"])
        self.assertEqual([row["status"] for row in plan["matrix"]], ["planned"] * 3)

    def test_selected_agent_does_not_plan_other_hosts(self):
        plan = MODULE.build_plan({
            "scope": "global",
            "agents": ["claude"],
            "target": {"kind": "domain", "name": "soia-dev"},
        })
        self.assertEqual([row["agent"] for row in plan["matrix"]], ["claude"])

    def test_project_workbuddy_is_explicitly_blocked(self):
        plan = MODULE.build_plan({
            "scope": "project",
            "agents": ["workbuddy"],
            "target": {"kind": "skill", "name": "soia-env-open-skills-install"},
        })
        self.assertEqual(plan["matrix"][0]["status"], "blocked")
        self.assertEqual(plan["state"], "capability_blocked")

    def test_input_json_shape_is_consumed(self):
        plan = MODULE.build_plan({
            "scope": "global",
            "agents": ["claude_code"],
            "target": {"kind": "skill", "id": "soia-env-open-skills-install"},
        })
        self.assertEqual(plan["agents"], ["claude"])
        self.assertEqual(plan["target_name"], "soia-env-open-skills-install")


if __name__ == "__main__":
    unittest.main()
