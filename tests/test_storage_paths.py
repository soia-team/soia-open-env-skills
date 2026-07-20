import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "templates" / "skill-template" / "scripts" / "resolve_storage.py"
SPEC = importlib.util.spec_from_file_location("resolve_storage", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class StoragePathTests(unittest.TestCase):
    def test_linux_uses_xdg_roots_and_keeps_storage_out_of_repo(self):
        paths = MODULE.storage_paths(
            "soia-env",
            "soia-env-example-install",
            env={
                "XDG_CONFIG_HOME": "/portable/config",
                "XDG_STATE_HOME": "/portable/state",
                "XDG_CACHE_HOME": "/portable/cache",
            },
            home=Path("/portable/home"),
            platform_name="linux",
            temp_root=Path("/portable/tmp"),
        )
        suffix = Path("soia-open-env-skills/soia-env/soia-env-example-install")
        self.assertEqual(paths["config"], Path("/portable/config/soia-skills") / suffix)
        self.assertEqual(paths["state"], Path("/portable/state/soia-skills") / suffix)
        self.assertEqual(paths["cache"], Path("/portable/cache/soia-skills") / suffix)
        self.assertEqual(paths["temp"], Path("/portable/tmp/soia-skills") / suffix)
        for path in paths.values():
            self.assertFalse(str(path).startswith(str(ROOT)))

    def test_macos_uses_native_cache_and_xdg_config_state(self):
        paths = MODULE.storage_paths(
            "soia-env",
            "soia-env-example-install",
            env={},
            home=Path("/portable/home"),
            platform_name="darwin",
            temp_root=Path("/portable/tmp"),
        )
        self.assertEqual(
            paths["cache"],
            Path("/portable/home/Library/Caches/soia-skills/soia-open-env-skills/soia-env/soia-env-example-install"),
        )
        self.assertEqual(
            paths["config"],
            Path("/portable/home/.config/soia-skills/soia-open-env-skills/soia-env/soia-env-example-install"),
        )

    def test_windows_uses_appdata_and_localappdata(self):
        paths = MODULE.storage_paths(
            "soia-env",
            "soia-env-example-install",
            env={
                "APPDATA": "C:/Portable/Roaming",
                "LOCALAPPDATA": "C:/Portable/Local",
            },
            home=Path("C:/Portable/Home"),
            platform_name="win32",
            temp_root=Path("C:/Portable/Temp"),
        )
        self.assertEqual(
            paths["config"],
            Path("C:/Portable/Roaming/soia-skills/soia-open-env-skills/soia-env/soia-env-example-install"),
        )
        self.assertEqual(
            paths["state"],
            Path("C:/Portable/Local/soia-skills/state/soia-open-env-skills/soia-env/soia-env-example-install"),
        )

    def test_soia_root_overrides_take_precedence(self):
        paths = MODULE.storage_paths(
            "soia-env",
            "soia-env-example-install",
            env={
                "SOIA_SKILLS_CONFIG_HOME": "/custom/config",
                "SOIA_SKILLS_STATE_HOME": "/custom/state",
                "SOIA_SKILLS_CACHE_HOME": "/custom/cache",
            },
            home=Path("/portable/home"),
            platform_name="linux",
            temp_root=Path("/portable/tmp"),
        )
        self.assertEqual(
            paths["config"],
            Path("/custom/config/soia-open-env-skills/soia-env/soia-env-example-install"),
        )
        self.assertEqual(
            paths["state"],
            Path("/custom/state/soia-open-env-skills/soia-env/soia-env-example-install"),
        )
        self.assertEqual(
            paths["cache"],
            Path("/custom/cache/soia-open-env-skills/soia-env/soia-env-example-install"),
        )


if __name__ == "__main__":
    unittest.main()
