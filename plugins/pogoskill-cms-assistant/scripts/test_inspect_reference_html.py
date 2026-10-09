import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("inspect-reference-html.py")
SPEC = importlib.util.spec_from_file_location("inspect_reference_html", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class HTMLInventoryTests(unittest.TestCase):
    def test_detects_distinct_site_components_and_image_size(self):
        sample = """<html><head><title>Example</title><link rel="canonical" href="https://www.example.com/guide/a.html"></head>
        <body><h2 class="section-title">Section</h2><div class="buy-box"><a>Buy</a></div>
        <div class="table-grid"><table><tr><td>1</td></tr></table></div>
        <picture><source srcset="a.webp"><img src="a.jpg" width="850" height="460"></picture></body></html>"""
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "article.html"
            path.write_text(sample, encoding="utf-8")
            report = MODULE.inspect(path)
        self.assertEqual(report["canonical_hosts"], ["www.example.com"])
        self.assertEqual(report["headings"][0]["class"], "section-title")
        self.assertIn("buy-box", report["component_classes"])
        self.assertIn("native-table", report["table_structures"])
        self.assertEqual(report["image_examples"][0]["width"], "850")


if __name__ == "__main__":
    unittest.main()
