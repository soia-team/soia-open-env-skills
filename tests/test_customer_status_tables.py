import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = (
    "soia-env-environment-setup",
    "soia-env-network-diagnose",
    "soia-env-node-install",
    "soia-env-python-install",
    "soia-env-workbuddy-install",
    "soia-env-storage-cleanup",
)
HEADER = "| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 更新时间 | 处理结果 |"
CODEX_HEADER = (
    "| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 安装方式 | "
    "安装目录 | 配置文件目录 | 更新时间 | 处理结果 |"
)


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
        self.assertIn("| 类别 | 检查项 | 结果 | 证据 | 风险 | 更新时间 | 下一步 |", text)

    def test_codex_install_defines_the_expanded_status_table(self):
        text = (
            ROOT / "skills" / "soia-env-codex-install" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn(CODEX_HEADER, text)
        self.assertIn("soia-dev-ai-cli-upgrade", text)
        self.assertIn(
            "ChatGPT.app/Contents/Resources/codex",
            text,
        )
        self.assertIn("不把它当作独立 Codex CLI", text)

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

    def test_all_skills_define_private_and_intermediate_storage(self):
        for skill_dir in sorted((ROOT / "skills").iterdir()):
            if not skill_dir.is_dir():
                continue
            with self.subTest(skill=skill_dir.name):
                text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
                self.assertIn("## 私密信息与中间数据", text)
                self.assertIn("更新时间", text)

    def test_new_skill_template_keeps_the_same_contract(self):
        text = (
            ROOT / "templates" / "skill-template" / "SKILL.md.template"
        ).read_text(encoding="utf-8")
        self.assertIn("### 私密信息与中间数据", text)
        self.assertIn(HEADER, text)
        for key in (
            "version:",
            "created_at:",
            "updated_at:",
            "created_by:",
            "updated_by:",
        ):
            self.assertIn(key, text)

    def test_storage_cleanup_requires_fresh_customer_authorization(self):
        text = (
            ROOT / "skills" / "soia-env-storage-cleanup" / "SKILL.md"
        ).read_text(encoding="utf-8")
        self.assertIn("初始“帮我清理”请求不能同时授权", text)
        self.assertIn("删除不可撤销", text)
        self.assertIn("CUSTOMER_APPROVED_IRREVERSIBLE_DELETE", text)
        self.assertIn("--confirmed-plan-id", text)
        self.assertIn("没有客户新回复，不得进入第 4 步", text)


if __name__ == "__main__":
    unittest.main()
