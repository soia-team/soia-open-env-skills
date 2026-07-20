import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "soia-env-codex-install",
    "soia-env-environment-setup",
    "soia-env-network-diagnose",
    "soia-env-node-install",
    "soia-env-python-install",
    "soia-env-workbuddy-install",
)
HEADER = "| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 处理结果 |"


class CustomerStatusTableTests(unittest.TestCase):
    def test_all_environment_skills_define_the_common_status_table(self):
        for skill in SKILLS:
            with self.subTest(skill=skill):
                text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(HEADER, text)

    def test_codex_diagnostics_keeps_its_detailed_result_table(self):
        text = (
            ROOT / "skills" / "soia-env-codex-setup-support" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("| 类别 | 检查项 | 结果 | 证据 | 风险 | 下一步 |", text)

    def test_install_skills_hide_unrequested_dependency_rows(self):
        expectations = {
            "soia-env-codex-install": "不增加 Node.js、npm",
            "soia-env-node-install": "不额外输出 npm",
            "soia-env-python-install": "不额外输出 pip",
            "soia-env-workbuddy-install": "不增加 Node.js、Python、npm",
        }
        for skill, sentence in expectations.items():
            with self.subTest(skill=skill):
                text = (ROOT / "skills" / skill / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn(sentence, text)


if __name__ == "__main__":
    unittest.main()
