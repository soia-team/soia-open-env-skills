import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "soia-env-codex-install" / "scripts" / "render_status.py"


class CodexInstallStatusTests(unittest.TestCase):
    def render(self, *extra):
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--current-status",
                "已安装",
                "--current-version",
                "0.144.4",
                "--latest-version",
                "0.144.6",
                "--runtime-status",
                "正常",
                "--result",
                "可更新",
                *extra,
            ],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_renders_fixed_six_column_table(self):
        result = self.render()
        self.assertEqual(result.returncode, 0)
        lines = result.stdout.strip().splitlines()
        self.assertEqual(
            lines[0],
            "| 技能 | 当前状态 | 当前版本 | 最新版本 | 运行状态 | 处理结果 |",
        )
        self.assertEqual(lines[1].count("|"), 7)
        self.assertEqual(lines[2].count("|"), 7)
        self.assertIn("| Codex CLI | 已安装 | `0.144.4` | `0.144.6` | 正常 | 可更新 |", lines[2])

    def test_customer_output_does_not_add_dependency_rows(self):
        result = self.render()
        self.assertNotIn("Node.js", result.stdout)
        self.assertNotIn("| npm |", result.stdout)

    def test_escapes_markdown_cell_breaks(self):
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--current-status",
                "被阻塞",
                "--runtime-status",
                "未验证",
                "--result",
                "缺少依赖|等待处理\n不要重复安装",
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("缺少依赖／等待处理 不要重复安装", result.stdout)
        self.assertEqual(len(result.stdout.strip().splitlines()), 3)


if __name__ == "__main__":
    unittest.main()
