import importlib.util
import tempfile
import unittest
from pathlib import Path


SPEC = importlib.util.spec_from_file_location("cms_macos", Path(__file__).with_name("cms-macos.py"))
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class MacTransportTests(unittest.TestCase):
    def test_multipart_contains_files_and_no_key(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "article-image.jpg"
            file.write_bytes(b"image-bytes")
            body, content_type = MODULE.multipart_image_body(44, "blog", [file])
        self.assertIn(b'filename="article-image.jpg"', body)
        self.assertIn(b"image-bytes", body)
        self.assertIn(b'name="site_id"', body)
        self.assertTrue(content_type.startswith("multipart/form-data; boundary="))

    def test_rejects_invalid_file_name(self):
        with tempfile.TemporaryDirectory() as temp:
            file = Path(temp) / "Bad Name.JPG"
            file.write_bytes(b"bytes")
            with self.assertRaises(ValueError):
                MODULE.multipart_image_body(44, "blog", [file])

    def test_response_requires_business_success_and_request_id(self):
        self.assertEqual(0, MODULE.checked_response(b'{"code":0,"request_id":"ok"}', "/cms/site/list")["code"])
        with self.assertRaises(RuntimeError):
            MODULE.checked_response(b'{"code":0}', "/cms/site/list")
        with self.assertRaises(RuntimeError):
            MODULE.checked_response(b'{"code":60001,"request_id":"bad"}', "/cms/site/list")

    def test_visible_newline_tokens_rejected_before_request(self):
        with self.assertRaises(ValueError):
            MODULE.request_json("/cms/page/add", {"content": "part 1\\npart 2"}, api_key="placeholder")

    def test_learning_mode_rejects_mutations_before_network(self):
        for endpoint in ("/cms/page/add", "/cms/page/update", "/cms/page/make",
                         "/cms/pagepublish/publish", "/cms/picture/upload", "/cms/file/createdir"):
            with self.subTest(endpoint=endpoint), self.assertRaises(ValueError):
                MODULE.learning_request_json(endpoint, {}, api_key="placeholder")

    def test_learning_mode_whitelist_matches_windows(self):
        script = Path(__file__).with_name("cms-learning-request.ps1").read_text(encoding="utf-8-sig")
        import re
        windows_paths = set(re.findall(r"'(/cms/[a-z0-9/_-]+)'", script))
        self.assertEqual(MODULE.LEARNING_READ_ONLY_PATHS, windows_paths)


if __name__ == "__main__":
    unittest.main()
