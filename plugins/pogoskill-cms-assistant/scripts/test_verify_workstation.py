import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("verify_workstation", Path(__file__).with_name("verify-workstation.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class PreflightTests(unittest.TestCase):
    def test_accepts_real_shape(self):
        self.assertEqual(2, MODULE.validate_site_response({"code": 0, "request_id": "r", "data": {"list": [{}, {}]}}))

    def test_requires_request_id(self):
        with self.assertRaises(RuntimeError):
            MODULE.validate_site_response({"code": 0, "data": {"list": []}})


if __name__ == "__main__":
    unittest.main()
