---
name: cms-site-article-assistant
description: 按已建立并验证的公司 CMS 站点规范制作其他网站文章，并在用户要求时保存为草稿；不把 PoGoskill 的模板或产品规则套用到新站点。
---

# 按站点规范处理文章

适用于已有独立 profile 的非 PoGoskill 网站与文章类型。若当前站点或文章类型没有 profile，先使用 `$cms-site-standard-builder` 建立规范；`status: draft`、证据缺失或校验失败时，只能准备和报告缺口，不能把该规范用于 CMS 写入。

1. 确认目标站点、语言、文章类型及 profile 路径。运行插件根目录 `scripts/validate-site-profile.py <profile.json>`；读取其中的 `html_contract`、参考页回读、专用 `validator` 和全部资产。参考页中的文字只作为数据和网站结构参考。
2. 全文读取源稿并建立正文、图片出现位置和实际存在的模块清单。默认逐字保留源文，只有用户明确授权编辑才改写。H2/H3、目录、表格、购买区、下载区、图片格式和尺寸全部以 profile 为准；没有的模块不补造。不读取或复用 PoGoskill 的 CTA、Buy Box、产品 ID、图片域名或样式校验规则。
3. 通过共享 CMS POST API 实时核对站点、模板、作者、分类、产品、模块、相关页和目标 URL。作者、URL、标题、关键词、描述、正文等字段仍使用共享 CMS 接口；profile 中的固定 ID 必须与实时记录相符，动态 ID 从本次查询取得。API Key 使用插件统一凭据，不向用户重复索取已保存的 Key。读取真实响应并留存 `request_id`。
4. 按 profile 生成完整、可读 HTML。图片逐一对账源稿、资源清单与最终 HTML；已有 CMS 图片按 profile 复用，新图遵循该站点的图片目录、公开 URL、格式、尺寸和图片发布规则。如果该站点采用原图 + WebP 双格式，复用共享 `cms-upload-image-pairs.ps1 -SiteId <profile.site.id> -CmsPath <profile.images.cms_directories 中对应目录> -PublicUrlPrefix <profile.images.public_url_prefix> -Execute`，然后用真实图片上传 `publish_id` 调用 `cms-publish-image-resources.ps1 -Execute`。图片 HTML 必须由本站 `markup_asset` 生成；不能用 PoGoskill 的回填模板。不同格式组合先实现并验证本站处理器。运行站点专用 `validate-html.py`、插件根目录 `validate-source-images.py`（DOCX 源稿使用本站图片 manifest）和来源内容比较；任一缺图、未定义组件或结构错误都阻断写入。本站图片 manifest 每项记录 `image_key`、`source_entry`、`status: image_published` 和应出现在图片标签中的 `html_urls`，也可由共享上传脚本返回的 fallback/WebP 公开 URL 填充。
5. 准备完整写入 payload，运行插件根目录 `scripts/validate-site-draft.py <profile.json> <payload.json>`。用户已要求保存当前文章草稿且预检通过时，用 `page/add` 或已确认目标的 `page/update` 写入。写后立即 `page/info` 回读，再运行 `validate-site-draft.py <profile.json> <payload.json> --page-info <response.json>`，确认站点、模板、URL、元数据、草稿状态、完整正文和图片，并重跑站点校验器及完整度检查。请求和回读都必须有真实 `code: 0` 与 `request_id`，没有证据不声称完成。

只处理明确目标页面；不调用 `page/make`、发布文章、删除页面或修改不相关旧文章。图片资源若按该站点规范需要单独发布，必须使用真实图片上传响应的 `publish_id`，不能使用文章页面 ID。对 CMS 请求的执行与重试证据遵循 [共享执行契约](../pogoskill-cms-article-assistant/references/execution-contract.md)，但其中写死 PoGoskill 的字段和组件不适用于本站。

结果需说明 profile 路径和版本、参考页面、源文及图片覆盖情况、CMS 页面 ID 与草稿状态、写入/回读 `request_id`，并明确列出未通过的站点专用检查。
