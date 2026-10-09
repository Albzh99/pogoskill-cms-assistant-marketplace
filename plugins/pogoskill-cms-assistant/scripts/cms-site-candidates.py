"""Narrow a real /cms/site/list readback without guessing among same-language sites."""

import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse


LANGUAGE_ALIASES = {
    "spanish": "es", "espanol": "es", "español": "es", "西班牙语": "es", "西语": "es",
    "english": "en", "英语": "en", "英文": "en",
    "german": "de", "德语": "de", "french": "fr", "法语": "fr",
    "japanese": "jp", "日语": "jp", "日文": "jp",
    "traditional chinese": "tw", "繁中": "tw", "繁体中文": "tw",
    "portuguese": "br", "葡萄牙语": "br", "意大利语": "it", "italian": "it",
    "korean": "kr", "韩语": "kr", "russian": "ru", "俄语": "ru",
}


def folded(value):
    value = re.sub(r"[^a-z0-9]+", "", str(value).lower())
    return {"4diggy": "4ddig", "4digg": "4ddig"}.get(value, value)


def locale_code(value):
    return LANGUAGE_ALIASES.get(str(value).strip().lower(), str(value).strip().lower())


def locale_matches(site, code):
    if not code:
        return True
    url = urlparse(str(site.get("url", "")))
    hostname = (url.hostname or "").lower()
    path = url.path.strip("/").lower().split("/")[0]
    name = str(site.get("site_name", "")).lower()
    if code == "en":
        return path in {"", "en"} and not re.search(r"(?:es|de|fr|jp|br|tw|kr|ru|it)$", name)
    return path == code or hostname.endswith("." + code) or name.endswith(code)


def candidates(response, product, language):
    if not isinstance(response, dict) or response.get("code") != 0:
        raise ValueError("site/list response is not code: 0")
    rows = response.get("data", {}).get("list", [])
    if not isinstance(rows, list):
        raise ValueError("site/list data.list is not an array")
    term = folded(product)
    if not term:
        raise ValueError("product name is required")
    code = locale_code(language)
    result = []
    for row in rows:
        if not isinstance(row, dict) or "弃" in str(row.get("site_name", "")):
            continue
        if str(row.get("status")) != "1":
            continue
        if term not in folded(row.get("site_name", "")) and term not in folded(row.get("url", "")):
            continue
        if not locale_matches(row, code):
            continue
        result.append({"id": row.get("id"), "site_name": row.get("site_name"), "url": row.get("url")})
    return {"product": product, "language": code, "candidates": result,
            "needs_site_choice": len(result) != 1, "request_id": response.get("request_id")}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("site_list_json")
    parser.add_argument("--product", required=True)
    parser.add_argument("--language", required=True)
    args = parser.parse_args()
    response = json.loads(Path(args.site_list_json).read_text(encoding="utf-8-sig"))
    print(json.dumps(candidates(response, args.product, args.language), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
