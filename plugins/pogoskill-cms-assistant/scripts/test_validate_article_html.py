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
{buybox}'''


def sample_en_html():
    cta = (EN_PUBLISHER / "assets" / "download-cta.html").read_text(encoding="utf-8")
    buybox = (EN_PUBLISHER / "assets" / "buybox.html").read_text(encoding="utf-8")
    return f'''<p>Complete introduction.</p>
<ul class="list-filled-dot nav-list1">
  <li><a href="#part1">Part 1. Core Content</a></li>
  <li><a href="#part2">Part 2. PoGoskill</a></li>
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
{buybox}'''


class ValidatorTests(unittest.TestCase):
    def test_valid_contract_passes(self):
        self.assertTrue(VALIDATOR.validate(sample_html(), PUBLISHER / "assets")["ok"])

    def test_missing_download_box_is_blocked(self):
        broken = sample_html().replace('class="secure-download"', 'class="missing-download-box"', 1)
        self.assertFalse(VALIDATOR.validate(broken, PUBLISHER / "assets")["ok"])

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


if __name__ == "__main__":
    unittest.main()
