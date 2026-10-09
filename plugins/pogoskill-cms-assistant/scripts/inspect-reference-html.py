"""Summarize old HTML files so an agent can build a site-specific article contract."""

import argparse
import hashlib
import json
import re
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse


COMPONENT_WORDS = re.compile(r"buy|price|product|download|cta|table|faq|toc|catalog|related|author|image|img|step|guide", re.I)
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


class ArticleHTMLInventory(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.heading = None
        self.headings = []
        self.image_specs = []
        self.component_classes = Counter()
        self.table_specs = Counter()
        self.canonical_urls = []
        self.title_text = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        parent_classes = self.stack[-1][1] if self.stack else []
        if tag in {"h1", "h2", "h3", "h4"}:
            self.heading = {"level": tag, "class": attributes.get("class", ""), "text": ""}
        if tag == "title":
            self.in_title = True
        if tag == "link" and (attributes.get("rel") or "").lower() == "canonical" and attributes.get("href"):
            self.canonical_urls.append(attributes["href"])
        if tag == "meta" and attributes.get("property") in {"og:url", "twitter:url"} and attributes.get("content"):
            self.canonical_urls.append(attributes["content"])
        if tag == "img":
            self.image_specs.append({
                "src": attributes.get("data-src") or attributes.get("src") or "",
                "width": attributes.get("width") or "",
                "height": attributes.get("height") or "",
                "style": attributes.get("style") or "",
                "class": attributes.get("class") or "",
                "parent_classes": " ".join(parent_classes),
            })
        for class_name in classes:
            if COMPONENT_WORDS.search(class_name):
                self.component_classes[class_name] += 1
            if "table" in class_name.lower():
                self.table_specs[f"{tag}.{class_name}"] += 1
        if tag == "table":
            self.table_specs["native-table"] += 1
        if tag == "picture":
            self.component_classes["picture"] += 1
        if tag not in VOID_TAGS:
            self.stack.append((tag, classes))

    def handle_endtag(self, tag):
        if tag in {"h1", "h2", "h3", "h4"} and self.heading and self.heading["level"] == tag:
            self.heading["text"] = re.sub(r"\s+", " ", self.heading["text"]).strip()[:180]
            self.headings.append(self.heading)
            self.heading = None
        if tag == "title":
            self.in_title = False
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.heading:
            self.heading["text"] += data
        if self.in_title:
            self.title_text.append(data)


def inspect(path):
    source = Path(path).resolve()
    raw = source.read_bytes()
    declared = re.search(rb"charset\s*=\s*['\"]?([a-zA-Z0-9_-]+)", raw[:4096], re.I)
    encodings = ([declared.group(1).decode("ascii", errors="ignore")] if declared else []) + ["utf-8-sig", "gb18030", "big5"]
    markup = None
    for encoding in encodings:
        try:
            markup = raw.decode(encoding)
            break
        except (LookupError, UnicodeDecodeError):
            continue
    if markup is None:
        markup = raw.decode("utf-8", errors="replace")
    parser = ArticleHTMLInventory()
    parser.feed(markup)
    canonical_hosts = sorted({urlparse(url).hostname for url in parser.canonical_urls if urlparse(url).hostname})
    return {
        "file": str(source),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "title": re.sub(r"\s+", " ", "".join(parser.title_text)).strip()[:180],
        "canonical_urls": parser.canonical_urls,
        "canonical_hosts": canonical_hosts,
        "headings": parser.headings[:40],
        "heading_class_counts": dict(Counter(f'{item["level"]}.{item["class"] or "(none)"}' for item in parser.headings).most_common()),
        "table_structures": dict(parser.table_specs.most_common()),
        "component_classes": dict(parser.component_classes.most_common(80)),
        "image_count": len(parser.image_specs),
        "image_examples": parser.image_specs[:30],
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html_files", nargs="+")
    parser.add_argument("--out")
    args = parser.parse_args()
    report = {"references": [inspect(path) for path in args.html_files]}
    report["canonical_hosts"] = sorted({host for item in report["references"] for host in item["canonical_hosts"]})
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.out:
        Path(args.out).write_text(rendered + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
