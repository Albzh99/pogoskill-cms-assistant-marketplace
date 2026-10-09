"""Check that a new CMS site/article-type contract is based on real page readbacks."""

import argparse
import hashlib
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse


SAFE_SLUG = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
REQUIRED_CONTRACT_SECTIONS = (
    "适用范围与证据", "CMS 字段与动态关联", "页面骨架与模块顺序", "标题与目录",
    "段落与列表", "图片与媒体", "表格", "产品区与下载", "FAQ 与特殊模块",
    "结论与链接", "校验与例外",
)


def positive_int(value):
    return type(value) is int and value > 0


def same_positive_id(value, expected):
    """CMS readbacks may encode database IDs as decimal strings."""
    return (positive_int(expected) and not isinstance(value, bool)
            and isinstance(value, (int, str)) and str(value) == str(expected))


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


def contains_id(value, target):
    if isinstance(value, dict):
        if same_positive_id(value.get("id"), target):
            return True
        return any(contains_id(child, target) for child in value.values())
    if isinstance(value, list):
        return any(contains_id(child, target) for child in value)
    return False


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
    if not positive_int(profile.get("profile_version")):
        errors.append("profile_version must be a positive integer")
    approval = profile.get("approval") if isinstance(profile.get("approval"), dict) else {}
    if not isinstance(approval.get("confirmed_by"), str) or not approval.get("confirmed_by").strip():
        errors.append("approval.confirmed_by is required before article use")
    confirmed_at = approval.get("confirmed_at")
    try:
        if not isinstance(confirmed_at, str) or datetime.fromisoformat(confirmed_at.replace("Z", "+00:00")).tzinfo is None:
            raise ValueError("timezone required")
    except ValueError:
        errors.append("approval.confirmed_at must be an ISO 8601 timestamp with timezone")

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
    if type(cms.get("draft_status")) is not int or type(cms.get("draft_sync_status")) is not int:
        errors.append("CMS draft status and sync status must be confirmed integer values")
    products = cms.get("product_ids")
    if not isinstance(products, list) or any(not isinstance(p, str) or not p.isdigit() for p in products):
        errors.append("cms.product_ids must be an array of string IDs (empty only if this site uses no product)")
    fields = cms.get("required_fields")
    if not isinstance(fields, list) or not fields or any(not isinstance(f, str) or not f.strip() for f in fields):
        errors.append("cms.required_fields must list field names confirmed for this template")
    images = profile.get("images") if isinstance(profile.get("images"), dict) else {}
    if type(images.get("enabled")) is not bool:
        errors.append("images.enabled must state whether this article type uses images")
    elif images["enabled"]:
        prefix = images.get("public_url_prefix")
        parsed_prefix = urlparse(prefix) if isinstance(prefix, str) else None
        if (not parsed_prefix or parsed_prefix.scheme != "https" or not parsed_prefix.hostname
                or not prefix.endswith("/") or parsed_prefix.hostname == "site.p.cms.afirstsoft.cn"):
            errors.append("images.public_url_prefix must be an HTTPS frontend directory ending in /")
        formats = images.get("formats")
        if not isinstance(formats, list) or not formats or any(ext not in {"jpg", "jpeg", "png", "webp"} for ext in formats):
            errors.append("images.formats must list the actual formats required by this site")
        directories = images.get("cms_directories")
        if not isinstance(directories, dict) or not directories or any(
            not isinstance(role, str) or not role or not isinstance(folder, str) or not folder.strip()
            for role, folder in directories.items()
        ):
            errors.append("images.cms_directories must map image roles to verified CMS directories")
        if images.get("publish_mode") != "picture-upload-publish-id":
            errors.append("images.publish_mode must describe the confirmed CMS image publication flow")
        try:
            local_file(root, images.get("markup_asset"))
        except ValueError as exc:
            errors.append(f"images.markup_asset: {exc}")

    references = profile.get("references")
    if not isinstance(references, list) or not references:
        errors.append("at least one CMS page/info reference is required")
        references = []
    page_ids = set()
    cms_reference_count = 0
    for index, reference in enumerate(references, 1):
        if not isinstance(reference, dict):
            errors.append(f"reference {index}: reference must be an object")
            continue
        kind = reference.get("kind", "cms")
        if kind == "html":
            try:
                evidence_path = local_file(root, reference.get("html_file"))
                if evidence_path.suffix.lower() not in {".html", ".htm"}:
                    errors.append(f"reference {index}: HTML file extension is required")
                raw = evidence_path.read_bytes()
                digest = hashlib.sha256(raw).hexdigest()
                if digest != reference.get("sha256"):
                    errors.append(f"reference {index}: HTML checksum differs from profile")
                if len(raw) < 100:
                    errors.append(f"reference {index}: HTML reference is too short")
            except (OSError, ValueError) as exc:
                errors.append(f"reference {index}: {exc}")
            continue
        if kind != "cms" or not positive_int(reference.get("page_id")):
            errors.append(f"reference {index}: kind must be cms with a positive page_id, or html with a local HTML file")
            continue
        cms_reference_count += 1
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
            if not same_positive_id(page.get("id"), page_id):
                errors.append(f"reference {index}: page ID differs from page/info")
            if not same_positive_id(page.get("site_id"), site_id):
                errors.append(f"reference {index}: site ID differs from profile")
            if not same_positive_id(page.get("template_id"), template_id):
                errors.append(f"reference {index}: template ID differs from profile")
            if str(page.get("status")) != "4":
                errors.append(f"reference {index}: CMS reference must be a published page (status 4)")
            if not isinstance(page.get("content"), str) or len(page["content"].strip()) < 100:
                errors.append(f"reference {index}: source HTML is absent or too short")
            if not evidence.get("request_id"):
                errors.append(f"reference {index}: request_id is absent")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"reference {index}: {exc}")

    if references and cms_reference_count == 0:
        discovery = profile.get("cms_discovery") if isinstance(profile.get("cms_discovery"), dict) else {}
        for field, expected_id in (("site_list_json", site_id), ("template_list_json", template_id)):
            try:
                evidence_path = local_file(root, discovery.get(field), ".json")
                evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
                if not isinstance(evidence, dict) or evidence.get("code") != 0 or not evidence.get("request_id"):
                    errors.append(f"cms_discovery.{field}: unsuccessful CMS response")
                elif not contains_id(evidence.get("data"), expected_id):
                    errors.append(f"cms_discovery.{field}: configured ID absent from CMS response")
            except (OSError, ValueError, TypeError) as exc:
                errors.append(f"cms_discovery.{field}: {exc}")
        try:
            evidence_path = local_file(root, discovery.get("template_fields_json"), ".json")
            evidence = json.loads(evidence_path.read_text(encoding="utf-8-sig"))
            if not isinstance(evidence, dict) or evidence.get("code") != 0 or not evidence.get("request_id"):
                errors.append("cms_discovery.template_fields_json: unsuccessful CMS response")
        except (OSError, ValueError, TypeError) as exc:
            errors.append(f"cms_discovery.template_fields_json: {exc}")

    for field, suffix in (("html_contract", ".md"), ("validator", ".py")):
        try:
            contract_path = local_file(root, profile.get(field), suffix)
            if field == "html_contract":
                contract = contract_path.read_text(encoding="utf-8-sig")
                headings = set(re.findall(r"^##\s+(.+?)\s*$", contract, flags=re.MULTILINE))
                for section in REQUIRED_CONTRACT_SECTIONS:
                    if section not in headings:
                        errors.append(f"html_contract missing required section: {section}")
                if "【未填写】" in contract:
                    errors.append("html_contract still contains unfilled template placeholders")
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

    examples = profile.get("validation_examples") if isinstance(profile.get("validation_examples"), dict) else {}
    if examples.get("valid_html") == examples.get("invalid_html"):
        errors.append("validation_examples must use distinct valid and invalid HTML files")
    for kind in ("valid_html", "invalid_html"):
        try:
            local_file(root, examples.get(kind), ".html")
        except ValueError as exc:
            errors.append(f"validation_examples.{kind}: {exc}")

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
