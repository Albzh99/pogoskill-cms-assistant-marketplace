import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("extract_cms_reference", Path(__file__).with_name("extract-cms-reference-html.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ReferenceTests(unittest.TestCase):
    def setUp(self):
        self.response = {"code": 0, "request_id": "read-id", "data": {
            "id": "789", "site_id": "44", "template_id": "8019", "status": "4",
            "content": "<article>" + "real website paragraph " * 20 + "</article>"}}

    def test_extracts_published_same_site_html(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source = root / "info.json"
            source.write_text(json.dumps(self.response), encoding="utf-8")
            target = root / "reference.html"
            result = MODULE.extract(source, target, 44, 8019)
            self.assertEqual("789", result["page_id"])
            self.assertIn("real website paragraph", target.read_text(encoding="utf-8"))
            self.assertEqual(result, MODULE.extract(source, target, 44, 8019))

    def test_rejects_cross_site_reference(self):
        with self.assertRaises(ValueError):
            MODULE.verified_html(self.response, 456)

    def test_rejects_draft_reference(self):
        self.response["data"]["status"] = "5"
        with self.assertRaises(ValueError):
            MODULE.verified_html(self.response, 44)


if __name__ == "__main__":
    unittest.main()
