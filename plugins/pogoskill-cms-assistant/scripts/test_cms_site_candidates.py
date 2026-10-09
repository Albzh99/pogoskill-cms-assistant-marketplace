import importlib.util
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("cms_site_candidates", Path(__file__).with_name("cms-site-candidates.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class CandidateTests(unittest.TestCase):
    def setUp(self):
        self.response = {"code": 0, "request_id": "read-id", "data": {"list": [
            {"id": 44, "site_name": "4ddiges", "url": "https://4ddig.tenorshare.com/es", "status": 1},
            {"id": 456, "site_name": "4ddigsubes", "url": "https://www.4ddig.es", "status": 1},
            {"id": 104, "site_name": "4ddiges(弃)", "url": "https://www.4ddig.esx", "status": 1},
            {"id": 45, "site_name": "4ddigde", "url": "https://4ddig.tenorshare.com/de", "status": 1},
        ]}}

    def test_spanish_4ddig_does_not_guess_between_two_live_sites(self):
        result = MODULE.candidates(self.response, "4diggy", "西语")
        self.assertEqual([44, 456], [item["id"] for item in result["candidates"]])
        self.assertTrue(result["needs_site_choice"])

    def test_single_german_site(self):
        result = MODULE.candidates(self.response, "4DDiG", "de")
        self.assertEqual([45], [item["id"] for item in result["candidates"]])
        self.assertFalse(result["needs_site_choice"])

    def test_rejects_failed_api_response(self):
        with self.assertRaises(ValueError):
            MODULE.candidates({"code": 60000}, "4ddig", "es")


if __name__ == "__main__":
    unittest.main()
