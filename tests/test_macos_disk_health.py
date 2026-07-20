import importlib.util
import pathlib
import unittest


SCRIPT = pathlib.Path(__file__).parents[1] / "skills/soia-env-codex-setup-support/scripts/check_macos_disk.py"
SPEC = importlib.util.spec_from_file_location("check_macos_disk", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class MacDiskHealthTests(unittest.TestCase):
    def test_healthy_output_is_observed(self):
        result = MODULE.analyze(
            """SMART overall-health self-assessment test result: PASSED
Percentage Used:                    12%
Available Spare:                    98%
Data Units Written:                 1,234,567 [632.61 TB]
Temperature:                        38 Celsius
""",
            "/dev/disk0",
        )
        self.assertEqual(result["status"], "observed")
        self.assertEqual(result["percentage_used"], 12)
        self.assertEqual(result["available_spare"], 98)
        self.assertEqual(result["temperature_c"], 38)
        self.assertEqual(result["warnings"], [])

    def test_warnings_are_explicit(self):
        result = MODULE.analyze(
            """SMART Health Status: FAILED
Percentage Used: 95%
Available Spare: 5%
Temperature Sensor 1: 72 C
"""
        )
        self.assertEqual(result["status"], "warning")
        self.assertEqual(
            result["warnings"],
            ["smart_health_not_passed", "percentage_used_high", "available_spare_low", "temperature_high"],
        )

    def test_unsupported_output_is_not_called_disk_failure(self):
        result = MODULE.analyze("SMART support is: Unavailable")
        self.assertEqual(result["status"], "unsupported_or_incomplete")
        self.assertEqual(result["warnings"], [])


if __name__ == "__main__":
    unittest.main()
