---
name: pogoskill-cms-en-publisher
description: Convert English PoGoskill SEO drafts into the English site's fixed V2 article HTML and, when explicitly authorized, save a verified CMS draft. Use only for site `pogoskill` / www.pogoskill.com; do not use for Traditional Chinese content or publishing.
---

# PoGoskill English CMS Publisher

Use this skill only for English articles on `https://www.pogoskill.com`. Traditional Chinese articles must use `pogoskill-cms-publisher`; never mix the two sites' wording, IDs, product links, image roots, or component assets.

默认用中文向团队成员汇报进度、异常和最终结果；只有文章正文、HTML 文案与英文站固定组件保持英文。除非用户明确要求英文回复，否则不要因为源稿是英文就改用英文沟通。

Before any CMS request, read the shared [execution evidence contract](../pogoskill-cms-article-assistant/references/execution-contract.md). Before writing HTML, read:

1. [English V2 HTML contract](references/english-html-contract.md);
2. [English CMS live contract](references/cms-en-live-contract.md);
3. `assets/download-cta.html` and `assets/buybox.html` in full.

## Fixed boundary

- Read-only discovery and local HTML conversion are allowed by default.
- Create or update a draft only when the user explicitly asks to save that English article in CMS.
- Use CMS POST API only; never use browser forms.
- Never call `/cms/page/make`, publish an article page, call delete endpoints, or modify an unrelated page. The image pipeline must call `/cms/pagepublish/publish` only with a `publish_id` returned by the current `/cms/picture/upload` response, solely to publish image resources.
- Never claim upload success without `page/add` or confirmed `page/update` evidence followed by successful `page/info` readback.

## Required workflow

1. Read the complete English source, including every paragraph, table, FAQ and image marker.
2. Query the English site, V2 template, fields, author, classification, products, sidebar, related pages and exact URL in real time.
3. Build readable, indented V2 HTML using only approved structures from the English contract.
4. For supplied JPG/PNG article images, create the same-basename WebP and upload both with the image pipeline using `-SiteId 286`. Article HTML must use `https://images.pogoskill.com/<folder>/<semantic-name>.<ext>` public URLs, never the CMS `upload` host. For Guide images named in the source, search the English `guides` library by that exact name; do not guess substitutes.
   If the exact fallback/WebP pair already exists in `/cms/picture/list`, reuse it instead of uploading again. If its public URL returns 404, recover the original image-upload `publish_id`, publish that image resource, and wait until both public URLs are readable before updating the draft. Never substitute a page ID or guess a publish ID.
5. Copy the English download CTA and Buy Box byte-for-byte from this skill's assets. Do not translate, shorten, restyle or reconstruct them.
   In the final Conclusion paragraph, link the natural homepage keyword phrase supplied by the source, such as `best Pikmin planting assistant` or `best Pokémon GO location changer`, and keep the following brand name `PoGoskill` outside the link. Never use `PoGoskill` itself as the Conclusion homepage anchor, and never invent a keyword absent from the source.
   Treat English phone screenshots as height-limited vertical media: use `max-height` with `width:auto;height:auto`, not a fixed pixel `max-width` that enlarges the screenshot across the article body.
6. Run the shared validator with the English profile:

```powershell
python scripts/validate-article-html.py <html-path> --profile en --assets-dir skills/pogoskill-cms-en-publisher/assets
```

7. Fix every validator error before any CMS write.
8. On authorization, save only a draft, then immediately call `/cms/page/info` and compare the complete readback with the final local HTML and metadata.

## Completion

`Draft ready for review` requires the page ID, write `request_id`, readback `request_id`, `status = 5`, `sync_status = 1`, complete HTML comparison, exact English CTA, exactly one English Buy Box, published and publicly readable image resources, and confirmation that no page make or article publication occurred.
