import argparse
import html
import json
import re
import sys
from pathlib import Path


def normalize(text):
    text = html.unescape(re.sub(r"<[^>]+>", "", text))
    text = re.sub(r"\s+", "", text)
    text = re.sub(r"^(?:H[123]|標題)[:：]", "", text)
    return text


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("structure_json")
    parser.add_argument("page_json")
    parser.add_argument("--min-ratio", type=float, default=0.0)
    args = parser.parse_args()

    structure = json.loads(Path(args.structure_json).read_text(encoding="utf-8"))
    response = json.loads(Path(args.page_json).read_text(encoding="utf-8"))
    page = response["data"]
    content = page.get("content", "")
    plain = normalize(content)

    source_text = []
    for block in structure["blocks"]:
        if block["type"] == "paragraph" and block.get("text"):
            value = normalize(block["text"])
            if value:
                source_text.append(value)
        elif block["type"] == "table":
            for row in block["rows"]:
                source_text.extend(normalize(cell) for cell in row if normalize(cell))

    matches = [item for item in source_text if len(item) >= 12 and item in plain]
    comparable = [item for item in source_text if len(item) >= 12]
    missing = [item for item in comparable if item not in plain]
    image_urls = list(dict.fromkeys(re.findall(r'(?:src|srcset)="([^"]+)"', content, re.I)))
    headings = [
        normalize(item)
        for item in re.findall(r"<h[23][^>]*>(.*?)</h[23]>", content, re.I | re.S)
    ]
    payload = {
        "page": {key: page.get(key) for key in (
            "id", "subject", "title", "description", "url", "status", "sync_status",
            "version", "author_id", "classify_page_id", "sidebar_module_id", "related_id", "product_id"
        )},
        "source_comparable_blocks": len(comparable),
        "exact_block_matches": len(matches),
        "exact_block_match_ratio": round(len(matches) / len(comparable), 4) if comparable else 0,
        "missing_blocks": missing,
        "headings": headings,
        "image_urls": image_urls,
    }
    print(json.dumps(payload, ensure_ascii=True, indent=2))
    ratio = payload["exact_block_match_ratio"]
    if args.min_ratio and ratio < args.min_ratio:
        print(
            f"Source coverage {ratio:.4f} is below required {args.min_ratio:.4f}",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
