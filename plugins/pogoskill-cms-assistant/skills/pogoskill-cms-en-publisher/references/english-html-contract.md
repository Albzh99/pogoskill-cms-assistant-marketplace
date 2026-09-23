# English V2 HTML contract

This contract is derived from three supplied English production examples and normalized to remove malformed legacy nesting and one-line output. Copy the established component structure; do not imitate accidental markup defects.

## Non-negotiable rules

- Write natural English only. Do not insert Traditional Chinese labels, Taiwanese links or Taiwan product IDs.
- Do not output an H1; CMS renders it from `subject`.
- Do not add `<style>`, article-specific wrapper classes, custom cards, colored notice boxes or new visual components.
- Keep HTML readable with one logical tag per line and consistent indentation. Never compress the article into one line.
- Preserve the complete source article. Do not omit late sections, tables, FAQ, conclusion, images, download CTA or Buy Box.
- Every class must already exist in the supplied English examples or an English reference page selected through CMS.

## Canonical order

1. Two or more introductory paragraphs.
2. Main image in the standard `img-wrap > picture > source + img` structure.
3. One table of contents: `<ul class="list-filled-dot nav-list1">` containing the `<li>` items directly. Do not create a bare nested `<ul>`.
4. Main sections in source order. Each linked section uses `id="partN"`, begins with one H2, and has exactly one matching TOC link.
5. If the article recommends PoGoskill: complete product explanation, approved feature list, `How to Use PoGoskill` subheading, exact download CTA, then one `step-cont` list.
6. FAQ section using the established FAQ heading structure.
7. Conclusion section.
8. Exactly one complete Buy Box copied from `assets/buybox.html`, after the conclusion text.

Do not add a TOC entry for a section that does not have a matching ID. Do not leave duplicate IDs. The Conclusion may be assigned the next `partN` and included in the TOC; choose one consistent approach for both TOC and section.

## Heading hierarchy

- H2: major article parts, FAQ and Conclusion.
- H3: genuine subtopics only. Approved observed variants are `h3-triangle`, `h3-orange-local`, `h3-red-local`, `h3-num`, and `h3-faq faq1`.
- H4: only a real subsection nested beneath an H3/H2 when the selected English reference already uses `h4-filled` for the same content role.
- Never use headings merely to enlarge text. Never place consecutive headings without explanatory content.
- Individual operation steps are list items, not separate H3 headings.

## Lists, tables and links

- Use an observed `list-cont` variant such as `list-star`, `list-lamp`, `list-angle`, `list-flag`, `list-primary-dot` or `list-white-dot` only when its semantic role matches the reference.
- Every `<li>` must remain inside its owning `<ul>` or `<ol>`. Images belonging to a step stay inside that `<li>` after its paragraph; never place a `<div>` directly between list items.
- Wrap every table in the English site's verified responsive table container. Do not invent a table class.
- Internal links use `https://www.pogoskill.com/...`; external promotional links use the supplied `rel` and `target` attributes. Do not copy `tw.pogoskill.com` into English HTML.

## Images

Use the established structure:

```html
<div class="img-wrap text-center">
  <picture>
    <source class="lozad img-fluid"
            srcset="https://images.pogoskill.com/loading.svg"
            data-srcset="https://images.pogoskill.com/<folder>/<semantic-name>.webp?w=<width>&amp;h=<height>"
            type="image/webp">
    <img class="lozad img-fluid"
         src="https://images.pogoskill.com/loading.svg"
         data-src="https://images.pogoskill.com/<folder>/<semantic-name>.jpg?w=<width>&amp;h=<height>"
         alt="accurate English description">
  </picture>
</div>
```

The WebP and JPG/PNG basenames must match. ALT describes the actual image. Keep the main image at 850×460 and do not invent URLs or claim upload success without API evidence.

Use `/cms/picture/upload` response `data.list[].url` as the public article URL; if it is absent, verify `/cms/picture/list` field `online`. The CMS `upload` URL is evidence only. Never claim that the API cannot provide a frontend URL before checking those fields, and never place `site.p.cms.afirstsoft.cn`, `attachment=1`, or another CMS backend URL in article HTML. Public English image URLs must use `https://images.pogoskill.com/`; filenames must remain readable semantic names without a trailing checksum/hash.

- User-supplied article images are the primary source. Convert each JPG/PNG to a same-basename WebP and keep both formats.
- Upload against English `site_id = 286` and choose the English image directory by article topic, such as `change-location`, `pokemon-ios`, `pikmin-bloom` or another live-confirmed folder.
- Guide/product screenshots are different: when the source supplies an exact Guide filename, search the English `guides` library and reuse that exact image pair. Do not guess a visually similar screenshot.
- Never upload an English image into `pogoskilltw_images`, and never silently reuse a Taiwan-site media URL as proof of an English CMS upload.

## PoGoskill recommendation block

- The first mention of PoGoskill in its recommendation section links to `https://www.pogoskill.com/`.
- Explain what PoGoskill does and why it solves the article's problem before showing download buttons.
- Use the reference site's existing feature heading/list. Do not create a custom feature card.
- Insert `assets/download-cta.html` exactly once in the recommendation block.
- The download CTA must retain both desktop secure-download boxes and the mobile Buy Now links. Do not remove wrappers, SVG references or button classes.
- Place a clear existing-style heading such as `<h4 class="h4-filled">How to Use PoGoskill</h4>` before the CTA/steps grouping according to the selected English reference. Do not translate it or turn every step into a heading.
- Each step uses this stable structure:

```html
<ul class="step-cont">
  <li>
    <p>
      <span>Step 1</span>
      <label><strong>Connect your device:</strong> Complete instruction.</label>
    </p>
    <!-- matching image box, when supplied -->
  </li>
</ul>
```

Keep the label around both bold lead text and the normal description so the layout cannot split into narrow columns.

## FAQ

- FAQ is a major H2 section.
- Each question uses the existing `h3-faq faq1` component, including its complete approved icon markup copied from a verified English page.
- Put one or more answer paragraphs immediately after each question.
- Do not insert a download CTA inside FAQ unless the source explicitly contains a PoGoskill recommendation there; even then, never duplicate the article CTA.

## Download CTA and Buy Box

- `assets/download-cta.html` is the only permitted English inline download CTA. It uses English download IDs `7144` and `7145` and `www.pogoskill.com` purchase links.
- `assets/buybox.html` is the only permitted English Buy Box. It includes desktop and mobile platform variants, product buttons, badges and counts.
- Copy both assets exactly. Do not hand-retype, shorten, translate, reorder, restyle or partially copy them.
- A valid article contains at most one inline download CTA and exactly one Buy Box.
- The `dev-desktop` / `dev-mobile` inside the Buy Box do not count as a second inline CTA.

## Defects seen in source examples that must be corrected

- Bare `<ul>` nested directly inside the TOC `<ul>`.
- Images or `<div>` elements placed between `<li>` siblings instead of inside the correct `<li>`.
- Entire sections compressed onto one line.
- Missing spaces around inline `<b>` elements.
- Broken words caused by adjacent text, such as `Psystrikeprovides`.
- Heading choices based only on visual size rather than document hierarchy.

The supplied articles are references for components and visual language, not permission to repeat these defects.
