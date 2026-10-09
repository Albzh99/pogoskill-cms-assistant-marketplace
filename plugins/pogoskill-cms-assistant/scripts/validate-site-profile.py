"""Check that a new CMS site/article-type contract is based on real page readbacks."""

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse


SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def positive_int(value):
    return type(value) is int and value > 0


def local_file(root, name, suffix=None):
    if not isinstance(name, str) or not name.strip():
        raise ValueError("path is missing")
    relative = Path(name)
    if relative.is_absolute() or ".." in relative.parts:
        raise ValueError(f"path must stay inside profile directory: {name}")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()) or not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"profile file missing or empty: {name}")
    if suffix and path.suffix.lower() != suffix:
        raise ValueError(f"profile file must end in {suffix}: {name}")
    return path


def check_profile(profile_path):
    path = Path(profile_path).resolve()
    root = path.parent
    errors = []
    try:
        profile = json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError) as exc:
        return {"pass": False, "errors": [f"cannot read profile: {exc}"]}
    if not isinstance(profile, dict):
        return {"pass": False, "errors": ["profile root must be an object"]}

    if profile.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    for field in ("profile_id", "article_type"):
        value = profile.get(field)
        if not isinstance(value, str) or not SAFE_SLUG.fullmatch(value):
            errors.append(f"{field} must be a lowercase hyphenated slug")
    if profile.get("status") != "ready":
        errors.append("status must be ready before use for an article")

    site = profile.get("site") if isinstance(profile.get("site"), dict) else {}
    cms = profile.get("cms") if isinstance(profile.get("cms"), dict) else {}
    site_id = site.get("id")
    template_id = cms.get("template_id")
    if not positive_int(site_id):
        errors.append("site.id must be a positive integer")
    if not positive_int(template_id):
        errors.append("cms.template_id must be a positive integer")
    for field in ("name", "language"):
        if not isinstance(site.get(field), str) or not site[field].strip():
            errors.append(f"site.{field} is required")
    base_url = site.get("base_url")
    parsed = urlparse(base_url) if isinstance(base_url, str) else None
    if not parsed or parsed.scheme != "https" or not parsed.hostname:
        errors.append("site.base_url must be an HTTPS URL")
    if cms.get("draft_status") != 5 or cms.get("draft_sync_status") != 1:
        errors.append("CMS draft status must be 5 and draft sync status must be 1")
    products = cms.get("product_ids")
    if not isinstance(products, list) or any(not isinstance(p, str) or not p.isdigit() for p in products):
        errors.append("cms.product_ids must be an array of string IDs (empty only if this site uses no product)")
    fields = cms.get("required_fields")
    if not isinstance(fields, list) or not fields or any(not isinstance(f, str) or not f.strip() for f in fields):
        errors.append("cms.required_fields must list field names confirmed for this template")

    references = profile.get("references")
    if not isinstance(references, list) or not references:
        errors.append("at least one CMS page/info reference is required")
        references = []
    page_ids = set()
    for index, reference in enumerate(references, 1):
        if not isinstance(reference, dict) or not positive_int(reference.get("page_id")):
            errors.append(f"reference {index}: page_id must be a positive integer")
            continue
        page_id = reference["page_id"]
        if page_id in page_ids:
            errors.append(f"reference {index}: duplicate page_id {page_id}")
        page_ids.add(page_id)
        try:
            evidence_path = local_file(root, reference.get("page_info_json"), ".json")
            evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
            page = evidence.get("data") if isinstance(evidence, dict) else None
            if not isinstance(evidence, dict) or evidence.get("code") != 0 or not isinstance(page, dict):
                errors.append(f"reference {index}: page/info response is not successful")
                continue
            if page.get("id") != page_id:
                errors.append(f"reference {index}: page ID differs from page/info")
            if page.get("site_id") != site_id:
                errors.append(f"reference {index}: site ID differs from profile")
            if page.get("template_id") != template_id:
                errors.append(f"reference {index}: template ID differs from profile")
            if not isinstance(page.get("content"), str) or len(page["content"].strip()) < 100:
                errors.append(f"reference {index}: source HTML is absent or too short")
            if not evidence.get("request_id"):
                errors.append(f"reference {index}: request_id is absent")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"reference {index}: {exc}")

    for field, suffix in (("html_contract", ".md"), ("validator", ".py")):
        try:
            local_file(root, profile.get(field), suffix)
        except ValueError as exc:
            errors.append(f"{field}: {exc}")
    assets = profile.get("assets")
    if not isinstance(assets, list):
        errors.append("assets must be an array, even when this article type has no fixed components")
    else:
        for index, asset in enumerate(assets, 1):
            try:
                local_file(root, asset)
            except ValueError as exc:
                errors.append(f"asset {index}: {exc}")

    return {
        "pass": not errors,
        "profile_id": profile.get("profile_id"),
        "site_id": site_id,
        "article_type": profile.get("article_type"),
        "reference_count": len(references),
        "errors": errors,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("profile_json")
    args = parser.parse_args()
    result = check_profile(args.profile_json)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not result["pass"]:
        sys.exit(1)


if __name__ == "__main__":
    main()
