import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLISHER = ROOT / "skills" / "pogoskill-cms-publisher"
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
</section>
<section id="part2">
  <h2>二、PoGoskill</h2>
  <p>完整介紹、適用情境、操作思路與作用。</p>
  <p class="section-label"><strong>PoGoskill 優勢</strong></p>
  <ul class="list-cont list-dark-dot"><li>優勢。</li></ul>
  {cta}
  <h3 class="h3-triangle">PoGoskill 操作步驟</h3>
  <ul class="step-cont"><li><p><span>步驟 1</span>操作。</p></li></ul>
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


if __name__ == "__main__":
    unittest.main()
