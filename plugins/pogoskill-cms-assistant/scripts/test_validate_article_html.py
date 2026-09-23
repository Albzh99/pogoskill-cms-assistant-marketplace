import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = ROOT / "skills" / "pogoskill-cms-publisher"
EN_PUBLISHER = ROOT / "skills" / "pogoskill-cms-en-publisher"
SPEC = importlib.util.spec_from_file_location(
    "article_validator", ROOT / "scripts" / "validate-article-html.py"
)
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


def sample_html():
    cta = (PUBLISHER / "assets" / "download-cta.html").read_text(encoding="utf-8")
    buybox = (PUBLISHER / "assets" / "buybox.html").read_text(encoding="utf-8")
    return f'''<div>
<p>完整導語。</p>
<ul class="list-filled-dot nav-list1">
  <li><a href="#part1">一、核心內容 <img class="tit-tips" src="https://images.pogoskill.com/hot-tips.png?w=100&amp;h=38" width="50" alt="熱門"></a></li>
  <li><a href="#part2">二、PoGoskill <img class="tit-tips" src="https://images.pogoskill.com/hot-tips.png?w=100&amp;h=38" width="50" alt="熱門"></a></li>
  <li><a href="#part3">結語</a></li>
</ul>
<section id="part1">
  <h2>一、核心內容</h2>
  <p>完整內容。</p>
  <div class="img-wrap text-center"><picture><source class="lozad img-fluid" srcset="https://tw.pogoskill.com/images/loading.svg" data-srcset="https://tw.pogoskill.com/images/pikmin/rare-pikmin-guide.webp?w=850&amp;h=460" type="image/webp"><img class="lozad img-fluid" src="https://tw.pogoskill.com/images/loading.svg" data-src="https://tw.pogoskill.com/images/pikmin/rare-pikmin-guide.png?w=850&amp;h=460" alt="稀有飾品皮克敏指南"></picture></div>
</section>
<section id="part2">
  <h2>二、PoGoskill</h2>
  <p>完整介紹、適用情境、操作思路與作用。</p>
  <p class="section-label"><strong>PoGoskill 優勢</strong></p>
  <ul class="list-cont list-dark-dot"><li>優勢。</li></ul>
  {cta}
  <h3 class="h3-triangle">PoGoskill 操作步驟</h3>
  <ul class="step-cont"><li><p><span>步驟 1</span><label><strong>連接手機：</strong>操作。</label></p></li></ul>
</section>
<section id="part3">
  <h2>結語</h2>
  <p><a href="https://tw.pogoskill.com/">最佳皮克敏飛人工具</a> PoGoskill 可協助完成上述需求。</p>
</section>
{buybox}'''


def sample_html_with_faq_cta():
    cta = (PUBLISHER / "assets" / "download-cta.html").read_text(encoding="utf-8")
    html = sample_html().replace(
        '<li><a href="#part3">結語</a></li>',
        '<li><a href="#part3">常見問題</a></li>\n  <li><a href="#part4">結語</a></li>',
    )
    return html.replace(
        '<section id="part3">\n  <h2>結語</h2>',
        f'''<section id="part3">
  <h2>常見問題</h2>
  <h3 class="h3-faq faq1">1. PoGoskill 可以協助這個操作嗎？</h3>
  <p>可以，本題明確推薦 PoGoskill 協助完成上述定位操作。</p>
  {cta}
</section>
<section id="part4">
  <h2>結語</h2>''',
    )


def sample_en_html():
    cta = (EN_PUBLISHER / "assets" / "download-cta.html").read_text(encoding="utf-8")
    buybox = (EN_PUBLISHER / "assets" / "buybox.html").read_text(encoding="utf-8")
    return f'''<p>Complete introduction.</p>
<ul class="list-filled-dot nav-list1">
  <li><a href="#part1">Part 1. Core Content</a></li>
  <li><a href="#part2">Part 2. PoGoskill</a></li>
  <li><a href="#part3">Conclusion</a></li>
</ul>
<section id="part1">
  <h2>Part 1. Core Content</h2>
  <h3 class="h3-orange-local">Verified Method</h3>
  <p>Complete content.</p>
  <div class="img-wrap text-center"><picture><source class="lozad img-fluid" srcset="https://images.pogoskill.com/loading.svg" data-srcset="https://images.pogoskill.com/pikmin-bloom/rare-pikmin-guide.webp?w=850&amp;h=460" type="image/webp"><img class="lozad img-fluid" src="https://images.pogoskill.com/loading.svg" data-src="https://images.pogoskill.com/pikmin-bloom/rare-pikmin-guide.jpg?w=850&amp;h=460" alt="Rare Decor Pikmin guide"></picture></div>
</section>
<section id="part2">
  <h2>Part 2. PoGoskill</h2>
  <p>Complete product explanation and use case.</p>
  <h4 class="h4-filled">Key Features of PoGoskill</h4>
  <ul class="list-cont list-flag"><li>Stable feature.</li></ul>
  <h4 class="h4-filled">How to Use PoGoskill</h4>
  {cta}
  <ul class="step-cont"><li><p><span>Step 1</span><label><strong>Connect your device:</strong> Complete instruction.</label></p></li></ul>
</section>
<section id="part3">
  <h2>Conclusion</h2>
  <p>The <a href="https://www.pogoskill.com/">best Pikmin planting assistant</a> PoGoskill supports the workflow above.</p>
</section>
{buybox}'''


def sample_en_html_with_faq_cta():
    cta = (EN_PUBLISHER / "assets" / "download-cta.html").read_text(encoding="utf-8")
    html = sample_en_html().replace(
        '<li><a href="#part3">Conclusion</a></li>',
        '<li><a href="#part3">FAQ</a></li>\n  <li><a href="#part4">Conclusion</a></li>',
    )
    return html.replace(
        '<section id="part3">\n  <h2>Conclusion</h2>',
        f'''<section id="part3">
  <h2>FAQ</h2>
  <h3 class="h3-faq faq1">Can PoGoskill help with this task?</h3>
  <p>Yes. PoGoskill is recommended here because it supports the location workflow described above.</p>
  {cta}
</section>
<section id="part4">
  <h2>Conclusion</h2>''',
    )


class ValidatorTests(unittest.TestCase):
    def test_valid_contract_passes(self):
        self.assertTrue(VALIDATOR.validate(sample_html(), PUBLISHER / "assets")["ok"])

    def test_missing_download_box_is_blocked(self):
        broken = sample_html().replace('class="secure-download"', 'class="missing-download-box"', 1)
        self.assertFalse(VALIDATOR.validate(broken, PUBLISHER / "assets")["ok"])

    def test_taiwan_faq_recommendation_allows_second_cta(self):
        result = VALIDATOR.validate(sample_html_with_faq_cta(), PUBLISHER / "assets")
        self.assertTrue(result["ok"], result["errors"])

    def test_truncated_html_is_blocked(self):
        self.assertFalse(VALIDATOR.validate(sample_html()[:-20], PUBLISHER / "assets")["ok"])

    def test_inline_markup_after_step_badge_is_blocked(self):
        broken = sample_html().replace(
            '<span>步驟 1</span><label><strong>連接手機：</strong>操作。</label>',
            '<span>步驟 1</span><strong>連接手機：</strong>操作。',
        )
        result = VALIDATOR.validate(broken, PUBLISHER / "assets")
        self.assertFalse(result["ok"])
        self.assertTrue(any("step SPAN + one LABEL" in item for item in result["errors"]))

    def test_step_numbers_must_be_sequential(self):
        broken = sample_html().replace('<span>步驟 1</span>', '<span>步驟 2</span>')
        result = VALIDATOR.validate(broken, PUBLISHER / "assets")
        self.assertFalse(result["ok"])
        self.assertTrue(any("sequential from 1" in item for item in result["errors"]))

    def test_valid_english_contract_passes(self):
        self.assertTrue(
            VALIDATOR.validate(sample_en_html(), EN_PUBLISHER / "assets", "en")["ok"]
        )

    def test_english_download_buttons_must_be_centered(self):
        broken = sample_en_html().replace(
            ' style="display:flex;justify-content:center;"', "", 1
        )
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("must be centered" in item for item in result["errors"]))

    def test_english_faq_recommendation_allows_second_cta(self):
        result = VALIDATOR.validate(
            sample_en_html_with_faq_cta(), EN_PUBLISHER / "assets", "en"
        )
        self.assertTrue(result["ok"], result["errors"])

    def test_english_faq_cta_requires_pogoskill_recommendation(self):
        broken = sample_en_html_with_faq_cta().replace(
            "PoGoskill is recommended here", "This option is recommended here", 1
        ).replace(
            "Can PoGoskill help with this task?", "Can this method help with the task?", 1
        )
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("FAQ CTA requires" in item for item in result["errors"]))

    def test_english_contract_rejects_taiwan_download_ids(self):
        broken = sample_en_html().replace("pogoskill_7144.exe", "pogoskill_7925.exe")
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])

    def test_english_contract_rejects_modified_buybox(self):
        broken = sample_en_html().replace(
            "The Best GPS Location Spoofer", "A GPS Location Spoofer", 1
        )
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("Buy Box must be copied exactly" in item for item in result["errors"]))

    def test_english_contract_rejects_taiwan_site_links(self):
        broken = sample_en_html().replace("www.pogoskill.com", "tw.pogoskill.com", 1)
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("Taiwan-site URLs" in item for item in result["errors"]))

    def test_taiwan_contract_rejects_cms_backend_image_url(self):
        broken = sample_html().replace(
            "https://tw.pogoskill.com/images/pikmin/rare-pikmin-guide.png?w=850&amp;h=460",
            "https://site.p.cms.afirstsoft.cn/pogoskilltw_images/pikmin/rare-pikmin-guide.png?attachment=1&amp;123",
        )
        result = VALIDATOR.validate(broken, PUBLISHER / "assets")
        self.assertFalse(result["ok"])
        self.assertTrue(any("CMS backend/attachment URL" in item for item in result["errors"]))

    def test_taiwan_contract_rejects_hash_suffix(self):
        broken = sample_html().replace("rare-pikmin-guide", "rare-pikmin-guide-394dd20f66")
        result = VALIDATOR.validate(broken, PUBLISHER / "assets")
        self.assertFalse(result["ok"])
        self.assertTrue(any("checksum/hash" in item for item in result["errors"]))

    def test_english_contract_rejects_cms_backend_image_url(self):
        broken = sample_en_html().replace(
            "https://images.pogoskill.com/pikmin-bloom/rare-pikmin-guide.jpg?w=850&amp;h=460",
            "https://site.p.cms.afirstsoft.cn/pogoskill_images/pikmin-bloom/rare-pikmin-guide.jpg?attachment=1",
        )
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("CMS backend/attachment URL" in item for item in result["errors"]))

    def test_taiwan_conclusion_rejects_pogoskill_as_anchor(self):
        broken = sample_html().replace(
            '<a href="https://tw.pogoskill.com/">最佳皮克敏飛人工具</a> PoGoskill',
            '<a href="https://tw.pogoskill.com/">PoGoskill</a>',
        )
        result = VALIDATOR.validate(broken, PUBLISHER / "assets")
        self.assertFalse(result["ok"])
        self.assertTrue(any("source keyword phrase" in item for item in result["errors"]))

    def test_english_conclusion_rejects_pogoskill_as_anchor(self):
        broken = sample_en_html().replace(
            '<a href="https://www.pogoskill.com/">best Pikmin planting assistant</a> PoGoskill',
            '<a href="https://www.pogoskill.com/">PoGoskill</a>',
        )
        result = VALIDATOR.validate(broken, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("source keyword phrase" in item for item in result["errors"]))

    def test_english_vertical_screenshot_requires_max_height(self):
        vertical = sample_en_html().replace(
            'rare-pikmin-guide.webp?w=850&amp;h=460',
            'phone-location-step.webp?w=390&amp;h=844',
        ).replace(
            'rare-pikmin-guide.jpg?w=850&amp;h=460" alt="Rare Decor Pikmin guide"',
            'phone-location-step.jpg?w=390&amp;h=844" alt="PoGoskill phone screenshot" style="max-width:390px;width:100%;height:auto;"',
        )
        result = VALIDATOR.validate(vertical, EN_PUBLISHER / "assets", "en")
        self.assertFalse(result["ok"])
        self.assertTrue(any("must use max-height" in item for item in result["errors"]))

    def test_english_vertical_screenshot_accepts_max_height(self):
        vertical = sample_en_html().replace(
            'rare-pikmin-guide.webp?w=850&amp;h=460',
            'phone-location-step.webp?w=390&amp;h=844',
        ).replace(
            'rare-pikmin-guide.jpg?w=850&amp;h=460" alt="Rare Decor Pikmin guide"',
            'phone-location-step.jpg?w=390&amp;h=844" alt="PoGoskill phone screenshot" style="max-height:520px;max-width:100%;width:auto;height:auto;"',
        )
        result = VALIDATOR.validate(vertical, EN_PUBLISHER / "assets", "en")
        self.assertTrue(result["ok"], result["errors"])


if __name__ == "__main__":
    unittest.main()
