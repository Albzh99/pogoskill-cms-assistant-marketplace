import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("validate-site-draft.py")
SPEC = importlib.util.spec_from_file_location("validate_site_draft", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class DraftProfileTests(unittest.TestCase):
    def setUp(self):
        self.profile = {"profile_id": "example-how-to", "site": {"id": 123},
                        "cms": {"template_id": 456, "draft_status": 5, "draft_sync_status": 1,
                                "product_ids": ["42"],
                                "required_fields": ["title", "content"]}}
        self.payload = {"site_id": 123, "template_id": 456, "product_id": ["42"],
                        "title": "Article", "url": "guide/article.html", "content": "<p>Complete article</p>"}

    def test_accepts_matching_payload_and_readback(self):
        response = {"code": 0, "request_id": "cms-read-id", "data": {
            **self.payload, "id": 789, "status": 5, "sync_status": 1}}
        result = MODULE.check_draft(self.profile, self.payload, response)
        self.assertTrue(result["pass"], result["errors"])

    def test_rejects_cross_site_product_and_template(self):
        self.payload.update({"site_id": 999, "template_id": 888, "product_id": ["43"]})
        result = MODULE.check_draft(self.profile, self.payload)
        self.assertFalse(result["pass"])
        self.assertEqual(len(result["errors"]), 3)

    def test_rejects_truncated_readback(self):
        response = {"code": 0, "request_id": "cms-read-id", "data": {
            **self.payload, "id": 789, "status": 5, "sync_status": 1,
            "content": "<p>Partial</p>"}}
        result = MODULE.check_draft(self.profile, self.payload, response)
        self.assertFalse(result["pass"])
        self.assertTrue(any("content differs" in error for error in result["errors"]))

    def test_uses_site_specific_draft_states(self):
        self.profile["cms"].update({"draft_status": 9, "draft_sync_status": 0})
        response = {"code": 0, "request_id": "cms-read-id", "data": {
            **self.payload, "id": 789, "status": 9, "sync_status": 0}}
        self.assertTrue(MODULE.check_draft(self.profile, self.payload, response)["pass"])


if __name__ == "__main__":
    unittest.main()
