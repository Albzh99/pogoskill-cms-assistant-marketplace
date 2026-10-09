import importlib.util
import hashlib
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
        (self.root / "tests").mkdir()
        (self.root / "tests" / "valid.html").write_text("<article>valid sample</article>", encoding="utf-8")
        (self.root / "tests" / "invalid.html").write_text("<article>invalid sample</article>", encoding="utf-8")
        sections = "\n".join(f"## {name}\n本站已核对：无或有真实证据。" for name in MODULE.REQUIRED_CONTRACT_SECTIONS)
        (self.root / "html-contract.md").write_text("# Site article rules\n" + sections, encoding="utf-8")
        (self.root / "validate-html.py").write_text("import sys\nsys.exit(0)\n", encoding="utf-8")
        self.page = {
            "code": 0,
            "request_id": "original-cms-readback-id",
            "data": {"id": 789, "site_id": 123, "template_id": 456, "status": "4", "content": "<article>" + "sample section " * 12 + "</article>"},
        }
        self.profile = {
            "schema_version": 1,
            "profile_id": "example-com-how-to",
            "status": "ready",
            "profile_version": 1,
            "approval": {"confirmed_by": "site-operator", "confirmed_at": "2026-10-09T10:00:00+08:00"},
            "site": {"id": 123, "name": "Example", "language": "en", "base_url": "https://www.example.com"},
            "article_type": "how-to",
            "cms": {"template_id": 456, "draft_status": 5, "draft_sync_status": 1,
                    "product_ids": [], "required_fields": ["title", "content"]},
            "images": {"enabled": False},
            "references": [{"page_id": 789, "page_info_json": "evidence/reference.json"}],
            "html_contract": "html-contract.md",
            "validator": "validate-html.py",
            "validation_examples": {"valid_html": "tests/valid.html", "invalid_html": "tests/invalid.html"},
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

    def test_accepts_cms_string_ids(self):
        self.page["data"].update({"id": "789", "site_id": "123", "template_id": "456"})
        result = self.check()
        self.assertTrue(result["pass"], result["errors"])

    def test_rejects_reference_from_another_site(self):
        self.page["data"]["site_id"] = 324
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("site ID differs" in error for error in result["errors"]))

    def test_rejects_unpublished_reference(self):
        self.page["data"]["status"] = "5"
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("published page" in error for error in result["errors"]))

    def test_rejects_draft_profile(self):
        self.profile["status"] = "draft"
        self.assertFalse(self.check()["pass"])

    def test_rejects_unconfirmed_profile(self):
        self.profile.pop("approval")
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("approval.confirmed_by" in error for error in result["errors"]))

    def test_rejects_missing_version(self):
        self.profile.pop("profile_version")
        self.assertFalse(self.check()["pass"])

    def test_rejects_incomplete_html_contract(self):
        (self.root / "html-contract.md").write_text("# Empty contract\n## 标题与目录\n【未填写】", encoding="utf-8")
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("missing required section" in error for error in result["errors"]))
        self.assertTrue(any("unfilled template" in error for error in result["errors"]))

    def test_rejects_missing_negative_example(self):
        self.profile["validation_examples"]["invalid_html"] = "tests/missing.html"
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("validation_examples.invalid_html" in error for error in result["errors"]))

    def test_rejects_assets_outside_profile(self):
        self.profile["assets"] = ["../foreign-cta.html"]
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("inside profile directory" in error for error in result["errors"]))

    def test_accepts_uploaded_old_html_with_verified_cms_discovery(self):
        old_html = b"<html><body><h2>Article</h2>" + b"<p>Reference paragraph</p>" * 8 + b"</body></html>"
        (self.root / "evidence" / "old-article.html").write_bytes(old_html)
        self.profile["references"] = [{
            "kind": "html", "html_file": "evidence/old-article.html",
            "sha256": hashlib.sha256(old_html).hexdigest(),
        }]
        self.profile["cms_discovery"] = {
            "site_list_json": "evidence/sites.json",
            "template_list_json": "evidence/templates.json",
            "template_fields_json": "evidence/fields.json",
        }
        for name, data in (("sites.json", {"list": [{"id": 123}]}),
                           ("templates.json", {"list": [{"id": 456}]}),
                           ("fields.json", {"list": [{"name": "title"}]})):
            (self.root / "evidence" / name).write_text(json.dumps({
                "code": 0, "request_id": "cms-evidence-id", "data": data,
            }), encoding="utf-8")
        self.assertTrue(self.check()["pass"])

    def test_rejects_uploaded_html_without_cms_mapping(self):
        old_html = b"<html><body>" + b"paragraph" * 20 + b"</body></html>"
        (self.root / "evidence" / "old-article.html").write_bytes(old_html)
        self.profile["references"] = [{
            "kind": "html", "html_file": "evidence/old-article.html",
            "sha256": hashlib.sha256(old_html).hexdigest(),
        }]
        result = self.check()
        self.assertFalse(result["pass"])
        self.assertTrue(any("cms_discovery" in error for error in result["errors"]))

    def test_image_profile_requires_own_public_domain_and_markup(self):
        self.profile["images"] = {"enabled": True, "formats": ["jpg", "webp"],
                                  "cms_directories": {"article": "blog"},
                                  "publish_mode": "picture-upload-publish-id",
                                  "public_url_prefix": "https://images.example.com/blog/",
                                  "markup_asset": "assets/image-box.html"}
        (self.root / "assets").mkdir()
        (self.root / "assets" / "image-box.html").write_text("<picture><img src=\"...\"></picture>", encoding="utf-8")
        self.assertTrue(self.check()["pass"])
        self.profile["images"]["public_url_prefix"] = "https://site.p.cms.afirstsoft.cn/example/"
        self.assertFalse(self.check()["pass"])


if __name__ == "__main__":
    unittest.main()
