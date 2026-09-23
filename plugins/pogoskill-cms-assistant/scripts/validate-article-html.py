import argparse
import html
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urlparse


VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "param", "source", "track", "wbr"}


def classes(attrs):
    value = dict(attrs).get("class", "")
    return set(value.split())


class StructureParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.errors = []
        self.h1 = 0
        self.h2 = 0
        self.sections = []
        self.toc_hrefs = []
        self.h3_classes = []
        self.table_parent_ok = []
        self.bare_uls = 0
        self.in_toc_depth = None

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        attrs_dict = dict(attrs)
        cls = classes(attrs)
        if tag == "h1":
            self.h1 += 1
        elif tag == "h2":
            self.h2 += 1
        elif tag == "h3":
            self.h3_classes.append(cls)
        elif tag == "section":
            self.sections.append(attrs_dict.get("id", ""))
        elif tag == "ul":
            if not cls:
                self.bare_uls += 1
            if {"list-filled-dot", "nav-list1"}.issubset(cls):
                self.in_toc_depth = len(self.stack) + 1
        elif tag == "a" and self.in_toc_depth is not None:
            href = attrs_dict.get("href", "")
            if href.startswith("#part"):
                self.toc_hrefs.append(href[1:])
        elif tag == "table":
            parent_cls = self.stack[-1][1] if self.stack else set()
            self.table_parent_ok.append({"table-box", "overflow-auto"}.issubset(parent_cls))

        if tag not in VOID_TAGS:
            self.stack.append((tag, cls))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag.lower() not in VOID_TAGS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag in VOID_TAGS:
            return
        if not self.stack:
            self.errors.append(f"unexpected closing tag </{tag}>")
            return
        current, _ = self.stack[-1]
        if current != tag:
            self.errors.append(f"misnested closing tag </{tag}> while <{current}> is open")
            return
        if tag == "ul" and self.in_toc_depth == len(self.stack):
            self.in_toc_depth = None
        self.stack.pop()

    def finish(self):
        if self.stack:
            self.errors.append("unclosed tags: " + ", ".join(tag for tag, _ in self.stack[-10:]))


def attr(block, name):
    match = re.search(rf'\b{name}="([^"]+)"', block, re.I)
    return match.group(1) if match else ""


def basename(url):
    name = Path(urlparse(url).path).name
    return Path(name).stem.lower()


def canonical(fragment):
    return re.sub(r"\s+", " ", fragment).strip()


def validate_step_lists(html_text, errors):
    step_lists = re.findall(
        r'<ul\b[^>]*class="[^"]*\bstep-cont\b[^"]*"[^>]*>(.*?)</ul>',
        html_text,
        re.I | re.S,
    )
    for list_index, list_body in enumerate(step_lists, 1):
        items = re.findall(r"<li\b[^>]*>(.*?)</li>", list_body, re.I | re.S)
        if not items:
            errors.append(f"step-cont #{list_index} must contain at least one LI")
            continue
        expected_number = 1
        for item_index, item_body in enumerate(items, 1):
            paragraph = re.match(r"\s*<p>(.*?)</p>", item_body, re.I | re.S)
            if not paragraph:
                errors.append(
                    f"step-cont #{list_index} item #{item_index} must begin with a plain P"
                )
                continue
            step_line = paragraph.group(1)
            badge = re.fullmatch(
                r"\s*<span>\s*(?:步驟|步骤|step)\s*(\d+)\s*</span>\s*"
                r"<label>\s*(?:<strong>[^<]+</strong>)?([^<]+)\s*</label>\s*",
                step_line,
                re.I | re.S,
            )
            if not badge:
                errors.append(
                    f"step-cont #{list_index} item #{item_index} must be P > step SPAN + one LABEL; optional STRONG belongs inside LABEL"
                )
                continue
            number = int(badge.group(1))
            if number != expected_number:
                errors.append(
                    f"step-cont #{list_index} step numbers must be sequential from 1; got {number} at item #{item_index}"
                )
            expected_number += 1
            if not badge.group(2).strip():
                errors.append(
                    f"step-cont #{list_index} item #{item_index} has no step description"
                )
            after_paragraph = item_body[paragraph.end():]
            if re.search(r"<p\b", after_paragraph, re.I):
                errors.append(
                    f"step-cont #{list_index} item #{item_index} must not add another paragraph"
                )


def validate(html_text, assets_dir=None, profile="tw"):
    errors = []
    parser = StructureParser()
    try:
        parser.feed(html_text)
        parser.close()
        parser.finish()
    except Exception as exc:
        errors.append(f"HTML parser error: {exc}")

    errors.extend(parser.errors)
    if parser.h1:
        errors.append(f"H1 count must be 0, got {parser.h1}")
    if parser.h2 != len(parser.sections):
        errors.append(f"section/H2 mismatch: sections={len(parser.sections)}, h2={parser.h2}")
    section_openings = re.findall(r"<section\b[^>]*>(.*?)</section>", html_text, re.I | re.S)
    if len(section_openings) != len(parser.sections) or any(
        not re.match(r"\s*<h2\b", content, re.I) for content in section_openings
    ):
        errors.append("every section must begin with H2")
    if not parser.sections or any(not item for item in parser.sections):
        errors.append("every article section must have an id")
    if len(parser.sections) != len(set(parser.sections)):
        errors.append("duplicate section ids")
    if set(parser.sections) != set(parser.toc_hrefs) or len(parser.sections) != len(parser.toc_hrefs):
        errors.append("TOC href values must match section ids exactly")
    if section_openings:
        conclusion = section_openings[-1]
        homepage = (
            "https://tw.pogoskill.com/"
            if profile == "tw"
            else "https://www.pogoskill.com/"
        )
        homepage_link = None
        for match in re.finditer(r"<a\b[^>]*>.*?</a>", conclusion, re.I | re.S):
            if attr(match.group(0), "href") == homepage:
                homepage_link = match
                break
        if homepage_link is None:
            errors.append("final Conclusion section must link the correct site homepage")
        else:
            anchor_text = re.sub(r"<[^>]+>", "", homepage_link.group(0)).strip()
            if not anchor_text or "pogoskill" in anchor_text.lower():
                errors.append("Conclusion homepage anchor must be the source keyword phrase, not PoGoskill")
            after_link = conclusion[homepage_link.end():]
            if not re.search(r"\bPoGoskill\b", after_link):
                errors.append("Conclusion must keep PoGoskill as plain text after the keyword link")
    approved_h3 = {"h3-triangle"} if profile == "tw" else {
        "h3-triangle", "h3-orange-local", "h3-red-local", "h3-num"
    }
    for index, cls in enumerate(parser.h3_classes, 1):
        normal = bool(approved_h3.intersection(cls))
        faq = {"h3-faq", "faq1"}.issubset(cls)
        if not normal and not faq:
            errors.append(f"H3 #{index} lacks approved class")
    if re.search(r"</h3>\s*<h3\b", html_text, re.I):
        errors.append("consecutive H3 headings without content are forbidden")
    if re.search(r"<h3\b[^>]*>\s*(?:<[^>]+>)*\s*(?:步驟|步骤|step)\s*\d+", html_text, re.I):
        errors.append("individual operation steps must not use H3")
    if parser.bare_uls:
        errors.append(f"bare UL count must be 0, got {parser.bare_uls}")
    if not all(parser.table_parent_ok):
        errors.append("every table must be directly wrapped by .table-box.overflow-auto")
    if re.search(r"<style\b|article-toc", html_text, re.I):
        errors.append("custom style or article-toc is forbidden")
    if re.search(r'class="[^"]*(?:rare-forest-article|gible-article|auto-tool-card|table-cont|table-list)[^"]*"', html_text, re.I):
        errors.append("legacy article-specific classes are forbidden")
    if profile == "en":
        if re.search(r"[\u4e00-\u9fff]", html_text):
            errors.append("English profile must not contain Chinese text")
        if "tw.pogoskill.com" in html_text:
            errors.append("English profile must not contain Taiwan-site URLs")
        for forbidden_download in ("pogoskill_7925.exe", "pogoskill-mac_7926.dmg"):
            if forbidden_download in html_text:
                errors.append(f"English profile contains Taiwan download ID: {forbidden_download}")

    validate_step_lists(html_text, errors)

    tips_count = len(re.findall(r'class="tit-tips"', html_text, re.I))
    if profile == "tw" and tips_count != 2:
        errors.append(f"tit-tips count must be 2, got {tips_count}")

    buybox_count = len(re.findall(r'class="pro-content pro-board1"', html_text, re.I))
    if buybox_count != 1:
        errors.append(f"Buy Box count must be 1, got {buybox_count}")
    if assets_dir and buybox_count == 1:
        expected_buybox = (Path(assets_dir) / "buybox.html").read_text(encoding="utf-8")
        if canonical(expected_buybox) not in canonical(html_text):
            errors.append("Buy Box must be copied exactly from assets/buybox.html")

    before_buybox = html_text.split('<div class="pro-content pro-board1">', 1)[0]
    steps_title = "PoGoskill 操作步驟" if profile == "tw" else "How to Use PoGoskill"
    step_heading_match = None
    for heading_match in re.finditer(
        r"<h([34])\b([^>]*)>(.*?)</h\1>", before_buybox, re.I | re.S
    ):
        heading_text = re.sub(r"<[^>]+>", "", heading_match.group(3)).strip()
        is_steps_heading = (
            "PoGoskill 操作步驟" in heading_text
            if profile == "tw"
            else bool(re.search(r"\bhow to\b.*\bpogoskill\b", heading_text, re.I))
        )
        if is_steps_heading:
            step_heading_match = heading_match
            if profile == "en" and heading_match.group(1) == "4":
                heading_class = attr(f"<h4 {heading_match.group(2)}>", "class")
                if "h4-filled" not in heading_class.split():
                    errors.append("English How to PoGoskill H4 must use the approved h4-filled class")
            break
    has_steps = step_heading_match is not None
    expected_cta = None
    if assets_dir:
        expected_cta = (Path(assets_dir) / "download-cta.html").read_text(encoding="utf-8")
        cta_count = canonical(before_buybox).count(canonical(expected_cta))
    else:
        secure_btn_count = len(re.findall(r'class="secure-btn(?:\s|\")', before_buybox, re.I))
        cta_count = 1 if secure_btn_count == 2 else 0
    if cta_count > 2:
        errors.append(f"article CTA count must not exceed 2, got {cta_count}")

    faq_cta_count = 0
    if expected_cta:
        expected_cta_canonical = canonical(expected_cta)
        for section in section_openings:
            heading = re.search(r"<h2\b[^>]*>(.*?)</h2>", section, re.I | re.S)
            heading_text = re.sub(r"<[^>]+>", "", heading.group(1)).strip() if heading else ""
            if re.search(r"FAQ|常見問題|常见问题", heading_text, re.I):
                section_cta_count = canonical(section).count(expected_cta_canonical)
                faq_cta_count += section_cta_count
                faq_before_cta = canonical(section).split(expected_cta_canonical, 1)[0]
                if section_cta_count and "pogoskill" not in faq_before_cta.lower():
                    errors.append("FAQ CTA requires a PoGoskill recommendation in the same FAQ section")
        if cta_count > 1 and faq_cta_count != cta_count - 1:
            errors.append("an additional article CTA is allowed only inside a PoGoskill recommendation FAQ")

    desktop_groups = re.findall(
        r'<div\b[^>]*class="[^"]*\bdev-desktop\b[^"]*"[^>]*>\s*'
        r'<div\b[^>]*class="[^"]*\bbtn-groups\b[^"]*"([^>]*)>',
        before_buybox,
        re.I | re.S,
    )
    for index, attrs_text in enumerate(desktop_groups, 1):
        style = attr(f"<div {attrs_text}>", "style").replace(" ", "").lower()
        if "justify-content:center" not in style:
            errors.append(f"article CTA #{index} desktop button group must be centered")
    if has_steps:
        if cta_count < 1:
            errors.append(f"the main article CTA is required when PoGoskill steps exist, got {cta_count}")
        secure_btn_count = len(re.findall(r'class="secure-btn(?:\s|\")', before_buybox, re.I))
        secure_download_count = len(re.findall(r'class="secure-download"', before_buybox, re.I))
        expected_boxes = 2 * cta_count
        if secure_btn_count != expected_boxes or secure_download_count != expected_boxes:
            errors.append(
                f"download CTA copies must each keep two secure-btn and two secure-download boxes; "
                f"expected {expected_boxes} of each"
            )
        required_downloads = (
            ("pogoskill_7925.exe", "pogoskill-mac_7926.dmg")
            if profile == "tw"
            else ("pogoskill_7144.exe", "pogoskill-mac_7145.dmg")
        )
        for required in required_downloads:
            if required not in before_buybox:
                errors.append(f"download CTA missing {required}")
        advantage_text = "PoGoskill 優勢" if profile == "tw" else "Key Features of PoGoskill"
        advantage = before_buybox.find(advantage_text)
        steps_heading = step_heading_match.start() if step_heading_match else -1
        cta_search_start = 0 if profile == "tw" else (steps_heading if steps_heading >= 0 else 0)
        cta = before_buybox.find('<div class="dev-desktop">', cta_search_start)
        step_list = before_buybox.find('class="step-cont"', steps_heading if steps_heading >= 0 else 0)
        valid_order = (
            advantage < cta < steps_heading < step_list
            if profile == "tw"
            else advantage < steps_heading < cta < step_list
        )
        if min(advantage, cta, steps_heading, step_list) < 0 or not valid_order:
            if profile == "tw":
                errors.append("PoGoskill order must be advantages, exact CTA, H3 steps title, then step-cont")
            else:
                errors.append("English PoGoskill order must be features, How to Use heading, exact CTA, then step-cont")

    picture_blocks = re.findall(r"<picture\b[^>]*>(.*?)</picture>", html_text, re.I | re.S)
    for index, block in enumerate(picture_blocks, 1):
        source_match = re.search(r"<source\b[^>]*>", block, re.I | re.S)
        img_match = re.search(r"<img\b[^>]*>", block, re.I | re.S)
        if not source_match or not img_match:
            errors.append(f"picture #{index} must contain source and img")
            continue
        source = source_match.group(0)
        image = img_match.group(0)
        webp_url = attr(source, "data-srcset") or attr(source, "srcset")
        fallback_url = attr(image, "data-src") or attr(image, "src")
        combined_urls = f"{webp_url} {fallback_url}".lower()
        if "site.p.cms.afirstsoft.cn" in combined_urls or re.search(r"[?&]attachment=1(?:&|$)", combined_urls):
            errors.append(f"picture #{index} must not use a CMS backend/attachment URL")
        expected_image_prefix = (
            "https://tw.pogoskill.com/images/"
            if profile == "tw"
            else "https://images.pogoskill.com/"
        )
        if webp_url and not webp_url.startswith(expected_image_prefix):
            errors.append(f"picture #{index} WebP URL must use the {profile} public image host")
        if fallback_url and not fallback_url.startswith(expected_image_prefix):
            errors.append(f"picture #{index} fallback URL must use the {profile} public image host")
        if not re.search(r"\.webp(?:$|\?)", webp_url, re.I):
            errors.append(f"picture #{index} source is not WebP")
        if not re.search(r"\.(?:jpe?g|png)(?:$|\?)", fallback_url, re.I):
            errors.append(f"picture #{index} fallback is not JPG/PNG")
        if webp_url and fallback_url and basename(webp_url) != basename(fallback_url):
            errors.append(f"picture #{index} WebP/fallback basenames differ")
        if re.search(r"-[0-9a-f]{10}$", basename(fallback_url), re.I):
            errors.append(f"picture #{index} filename must not end with a checksum/hash")
        if not attr(image, "alt").strip():
            errors.append(f"picture #{index} ALT is empty")
        if profile == "en" and fallback_url:
            query = parse_qs(urlparse(html.unescape(fallback_url)).query)
            try:
                width = int(query.get("w", [0])[0])
                height = int(query.get("h", [0])[0])
            except (TypeError, ValueError):
                width = height = 0
            if height > width > 0:
                style = attr(image, "style").replace(" ", "").lower()
                if not re.search(r"max-height:\d+px", style) or "width:auto" not in style or "height:auto" not in style:
                    errors.append(f"English vertical picture #{index} must use max-height with width:auto and height:auto")
                if re.search(r"max-width:\d+px", style):
                    errors.append(f"English vertical picture #{index} must not use a fixed pixel max-width")

    pending_count = html_text.count("IMAGE_PENDING")
    if pending_count:
        errors.append(f"IMAGE_PENDING count must be 0 for a complete draft, got {pending_count}")

    return {
        "ok": not errors,
        "errors": errors,
        "counts": {
            "h1": parser.h1,
            "h2": parser.h2,
            "sections": len(parser.sections),
            "toc_links": len(parser.toc_hrefs),
            "tit_tips": tips_count,
            "h3": len(parser.h3_classes),
            "pictures": len(picture_blocks),
            "article_cta": cta_count,
            "buybox": buybox_count,
            "image_pending": pending_count,
        },
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("html")
    parser.add_argument("--assets-dir")
    parser.add_argument("--profile", choices=("tw", "en"), default="tw")
    parser.add_argument("--out")
    args = parser.parse_args()

    path = Path(args.html).resolve()
    assets_dir = Path(args.assets_dir).resolve() if args.assets_dir else (
        Path(__file__).resolve().parents[1] / "skills" / "pogoskill-cms-publisher" / "assets"
    )
    result = validate(path.read_text(encoding="utf-8"), assets_dir, args.profile)
    payload = json.dumps(result, ensure_ascii=False, indent=2)
    if args.out:
        Path(args.out).resolve().write_text(payload, encoding="utf-8")
    print(payload)
    sys.exit(0 if result["ok"] else 1)


if __name__ == "__main__":
    main()
