import importlib.util
import unittest
from datetime import datetime
from unittest.mock import patch
import urllib.error


ROOT = __import__("pathlib").Path(__file__).resolve().parents[1]
_REPO_LAYOUT = ROOT / "skills" / "soia-env-network-diagnose" / "scripts" / "probe_endpoints.py"
_PACKAGE_LAYOUT = ROOT / "scripts" / "probe_endpoints.py"
if _REPO_LAYOUT.exists():
    SCRIPT = _REPO_LAYOUT
elif _PACKAGE_LAYOUT.exists():
    SCRIPT = _PACKAGE_LAYOUT
else:
    raise FileNotFoundError(
        "找不到 probe_endpoints.py：仓布局 {} 与包布局 {} 均不存在".format(_REPO_LAYOUT, _PACKAGE_LAYOUT)
    )
SPEC = importlib.util.spec_from_file_location("probe_endpoints", SCRIPT)
probe_endpoints = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(probe_endpoints)


class ProbeEndpointTests(unittest.TestCase):
    def test_reachable_response_is_safe_json(self):
        class Response:
            status = 204

            def __enter__(self):
                return self

            def __exit__(self, *_):
                return False

        with patch.object(probe_endpoints.urllib.request, "urlopen", return_value=Response()):
            result = probe_endpoints.probe("https://example.test", 1)
        self.assertTrue(result["ok"])
        self.assertEqual(result["category"], "reachable")
        self.assertNotIn("body", result)
        self.assertIsNotNone(datetime.fromisoformat(result["checked_at"]).tzinfo)

    def test_http_error_is_classified(self):
        error = urllib.error.HTTPError("https://example.test", 503, "busy", {}, None)
        with patch.object(probe_endpoints.urllib.request, "urlopen", side_effect=error):
            result = probe_endpoints.probe("https://example.test", 1)
        self.assertFalse(result["ok"])
        self.assertEqual(result["category"], "http_error")
        self.assertEqual(result["status"], 503)

    def test_credentials_and_non_http_urls_are_rejected(self):
        self.assertEqual(probe_endpoints.probe("ftp://example.test", 1)["category"], "invalid_url")
        result = probe_endpoints.probe("https://user:pass@example.test/private", 1)
        self.assertEqual(result["category"], "invalid_url")
        self.assertEqual(result["url"], "https://example.test/private")
        self.assertNotIn("user", result["url"])
        self.assertNotIn("pass", result["url"])

    def test_query_and_fragment_are_not_returned(self):
        self.assertEqual(
            probe_endpoints.sanitized_url(
                "https://example.test/download?access_token=private#section"
            ),
            "https://example.test/download",
        )


if __name__ == "__main__":
    unittest.main()
