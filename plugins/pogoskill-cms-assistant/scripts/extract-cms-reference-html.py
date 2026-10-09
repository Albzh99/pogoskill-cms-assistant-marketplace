"""Turn a verified published page/info readback into a local HTML style reference."""

import argparse
import hashlib
import json
from pathlib import Path


def verified_html(response, site_id, template_id=None):
    if not isinstance(response, dict) or response.get("code") != 0 or not response.get("request_id"):
        raise ValueError("page/info must have code 0 and request_id")
    page = response.get("data")
    if not isinstance(page, dict) or str(page.get("site_id")) != str(site_id):
        raise ValueError("page/info site_id does not match target site")
    if template_id is not None and str(page.get("template_id")) != str(template_id):
        raise ValueError("page/info template_id does not match target article type")
    if str(page.get("status")) != "4":
        raise ValueError("Only a published page may establish the default HTML style")
    html = page.get("content")
    if not isinstance(html, str) or len(html.strip()) < 100:
        raise ValueError("page/info content is absent or too short")
    return html, page.get("id")


def extract(source, output, site_id, template_id=None):
    source = Path(source)
    output = Path(output)
    response = json.loads(source.read_text(encoding="utf-8-sig"))
    html, page_id = verified_html(response, site_id, template_id)
    encoded = html.encode("utf-8")
    if output.exists():
        if output.read_bytes() != encoded:
            raise FileExistsError("Existing reference HTML differs; choose a new path")
    else:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(encoded)
    return {"page_id": page_id, "site_id": site_id, "html_file": str(output),
            "sha256": hashlib.sha256(encoded).hexdigest(), "characters": len(html),
            "request_id": response["request_id"]}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("page_info_json")
    parser.add_argument("--output", required=True)
    parser.add_argument("--site-id", type=int, required=True)
    parser.add_argument("--template-id", type=int)
    args = parser.parse_args()
    print(json.dumps(extract(args.page_info_json, args.output, args.site_id, args.template_id),
        ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
