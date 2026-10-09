import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate-site-profile.py")
SPEC = importlib.util.spec_from_file_location("validate_site_profile", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class SiteProfileTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "evidence").mkdir()
        (self.root / "html-contract.md").write_text("# Site article rules\nUse h2 sections.", encoding="utf-8")
        (self.root / "validate-html.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        self.page = {
            "code": 0,
            "request_id": "original-cms-readback-id",
            "data": {"id": 789, "site_id": 123, "template_id": 456, "content": "<article>" + "sample section " * 12 + "</article>"},
        }
        self.profile = {
            "schema_version": 1,
            "profile_id": "example-com-how-to",
            "status": "ready",
            "site": {"id": 123, "name": "Example", "language": "en", "base_url": "https://www.example.com"},
            "article_type": "how-to",
            "cms": {"template_id": 456, "draft_status": 5, "draft_sync_status": 1,
                    "product_ids": [], "required_fields": ["title", "content"]},
            "references": [{"page_id": 789, "page_info_json": "evidence/reference.json"}],
            "html_contract": "html-contract.md",
            "validator": "validate-html.py",
            "assets": [],
        }

    def check(self):
        (self.root / "evidence" / "reference.json").write_text(json.dumps(self.page), encoding="utf-8")
        path = self.root / "profile.json"
        path.write_text(json.dumps(self.profile), encoding="utf-8")
        return MODULE.check_profile(path)

    def test_accepts_matching_cms_reference(self):
        result = self.check()
        self.assertTrue(result["pass"], result["errors"])

    def test_rejects_reference_from_another_site(self):
        self.page["data"]["site_id"] = 324
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("site ID differs" in error for error in result["errors"]))

    def test_rejects_draft_profile(self):
        self.profile["status"] = "draft"
        self.assertFalse(self.check()["pass"])

    def test_rejects_assets_outside_profile(self):
        self.profile["assets"] = ["../foreign-cta.html"]
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("inside profile directory" in error for error in result["errors"]))


if __name__ == "__main__":
    unittest.main()
