"""Check a CMS draft payload and optional page/info readback against its site profile."""

import argparse
import importlib.util
import json
import sys
from pathlib import Path


PROFILE_VALIDATOR = Path(__file__).with_name("validate-site-profile.py")
SPEC = importlib.util.spec_from_file_location("validate_site_profile", PROFILE_VALIDATOR)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def product_ids(value):
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except json.JSONDecodeError:
            value = [part.strip() for part in value.split(",") if part.strip()]
    if not isinstance(value, list):
        return None
    return [str(item) for item in value]


def check_draft(profile, payload, page_response=None):
    errors = []
    site_id = profile["site"]["id"]
    cms = profile["cms"]
    required = cms["required_fields"]
    if payload.get("site_id") != site_id:
        errors.append("payload.site_id does not match profile")
    if payload.get("template_id") != cms["template_id"]:
        errors.append("payload.template_id does not match profile")
    if product_ids(payload.get("product_id", [])) != cms["product_ids"]:
        errors.append("payload.product_id does not match profile")
    for field in required:
        value = payload.get(field)
        if value is None or value == "" or value == []:
            errors.append(f"required payload field is missing: {field}")
    url = payload.get("url")
    if not isinstance(url, str) or not url.strip() or "://" in url or ".." in url.split("/"):
        errors.append("payload.url must be a safe relative path")
    for field, expected in (("status", 5), ("sync_status", 1)):
        if field in payload and payload[field] != expected:
            errors.append(f"payload.{field} must be {expected}")

    if page_response is not None:
        page = page_response.get("data") if isinstance(page_response, dict) else None
        if not isinstance(page_response, dict) or page_response.get("code") != 0 or not isinstance(page, dict):
            errors.append("page/info response is not successful")
        else:
            if not page_response.get("request_id"):
                errors.append("page/info request_id is missing")
            for field, expected in (("site_id", site_id), ("template_id", cms["template_id"]),
                                    ("url", payload.get("url")), ("status", 5), ("sync_status", 1),
                                    ("content", payload.get("content"))):
                if page.get(field) != expected:
                    errors.append(f"page/info {field} differs from expected draft")
            if product_ids(page.get("product_id", [])) != cms["product_ids"]:
                errors.append("page/info product_id does not match profile")
            for field in required:
                if field not in {"status", "sync_status"} and page.get(field) != payload.get(field):
                    errors.append(f"page/info required field differs from payload: {field}")
    return {"pass": not errors, "errors": errors, "site_id": site_id,
            "profile_id": profile["profile_id"], "readback_checked": page_response is not None}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile_json")
    parser.add_argument("payload_json")
    parser.add_argument("--page-info")
    args = parser.parse_args()
    profile_check = MODULE.check_profile(args.profile_json)
    if not profile_check["pass"]:
        print(json.dumps(profile_check, ensure_ascii=False, indent=2))
        sys.exit(1)
    profile = json.loads(Path(args.profile_json).read_text(encoding="utf-8-sig"))
    payload = json.loads(Path(args.payload_json).read_text(encoding="utf-8-sig"))
    response = json.loads(Path(args.page_info).read_text(encoding="utf-8-sig")) if args.page_info else None
    result = check_draft(profile, payload, response)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
