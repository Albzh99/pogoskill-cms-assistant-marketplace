import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("site_profile_root", Path(__file__).with_name("site-profile-root.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class RootTests(unittest.TestCase):
    def test_stable_outside_versioned_plugin_cache(self):
        with tempfile.TemporaryDirectory() as temp:
            root = MODULE.profile_root(codex_home=Path(temp))
            self.assertEqual(Path(temp) / "tenorshare-cms" / "site-profiles", root)

    def test_rejects_relative_codex_home(self):
        with self.assertRaises(ValueError):
            MODULE.profile_root(codex_home="relative")


if __name__ == "__main__":
    unittest.main()
