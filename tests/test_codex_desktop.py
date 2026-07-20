import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "skills/soia-env-codex-setup-support/scripts/check_codex_desktop.py"
SPEC = importlib.util.spec_from_file_location("check_codex_desktop", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class CodexDesktopTests(unittest.TestCase):
    def test_chatgpt_bundle_is_codex_host(self):
        result = MODULE.summarize(
            exists=True,
            bundle_id="com.openai.codex",
            version="26.715.31925",
            signature_ok=True,
            location="system_applications",
        )
        self.assertEqual(result["status"], "ready")
        self.assertEqual(result["application"], "ChatGPT.app (Codex host)")

    def test_missing_app_is_not_downloaded(self):
        result = MODULE.summarize(
            exists=False,
            bundle_id=None,
            version=None,
            signature_ok=None,
            location="system_applications",
        )
        self.assertEqual(result["status"], "missing")

    def test_invalid_signature_is_not_ready(self):
        result = MODULE.summarize(
            exists=True,
            bundle_id="com.openai.codex",
            version="26.715.31925",
            signature_ok=False,
            location="system_applications",
        )
        self.assertEqual(result["status"], "invalid_signature")


if __name__ == "__main__":
    unittest.main()
