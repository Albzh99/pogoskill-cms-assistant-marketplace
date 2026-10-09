# 新站点规范契约

## 输入和证据

- 同事优先只提供几份正常旧 HTML 和一篇待处理新稿。助手用 `inspect-reference-html.py` 自动提取 canonical/domain、标题类、表格、购买区、图片尺寸等，再完整阅读原 HTML。能识别网站时自行查询 CMS；只有无法判定目标网站时才要求一个网站 URL，不要让同事找页面 ID、填 JSON 或操作终端。
- 通过 `site/list`、`template/list` 和 `template/fields` 取得可核对的站点 ID、模板 ID、字段和 `request_id`。若旧 HTML 的 canonical/URL 能在 CMS 中命中，额外保存 `page/info`；旧 HTML 没有 CMS 页面 ID 也可以作为样式证据，但 CMS 映射证据仍必须齐全才能把 profile 标成 `ready`。
- 参考文章应与目标文章类型相同；多个风格差异较大的文章类型分别建规范。作者、URL、标题、关键词、描述和正文等 CMS 字段名及 POST 调用方式共用，但它们的取值、生成规则、链接目标和关联 ID 必须逐站确认；不从 PoGoskill 规则推断。
- 读取目标站点已使用的图片路径与 HTML 图片盒、格式组合、主图尺寸、竖图展示和已有图片复用方式。图片经 `/cms/picture/upload` 上传，再使用该次返回的图片 `publish_id` 发布资源，是共用的 CMS 调用流程；各站图片规格与 HTML 仍以本站实例和 CMS 结果为准。若某站点不用某模块，明确写“无”，不要硬塞 PoGoskill CTA 或 Buy Box。

## 文件格式

目录例：`site-profiles/example-com/how-to/`。`profile.json` 需要以下字段；数值与网址必须来自当前站点的查询结果，不使用示例值：

```json
{
  "schema_version": 1,
  "profile_id": "example-com-how-to",
  "status": "draft",
  "site": {"id": 123, "name": "Example", "language": "en", "base_url": "https://www.example.com"},
  "article_type": "how-to",
  "cms": {
    "template_id": 456,
    "draft_status": 5,
    "draft_sync_status": 1,
    "product_ids": [],
    "required_fields": ["title", "subject", "url", "content"]
  },
  "references": [{"kind": "html", "html_file": "evidence/old-article.html", "sha256": "<该文件实际 SHA256>"}],
  "cms_discovery": {
    "site_list_json": "evidence/site-list.json",
    "template_list_json": "evidence/template-list.json",
    "template_fields_json": "evidence/template-fields.json"
  },
  "images": {
    "enabled": true,
    "formats": ["jpg", "webp"],
    "cms_directories": {"article": "article-images"},
    "public_url_prefix": "https://images.example.com/article-images/",
    "publish_mode": "picture-upload-publish-id",
    "markup_asset": "assets/image-box.html"
  },
  "html_contract": "html-contract.md",
  "validator": "validate-html.py",
  "assets": []
}
```

`draft_status` 和 `draft_sync_status` 的数字须由该 CMS 站点的真实草稿/接口规则确认；示例数值不直接套用。`product_ids` 为空只能表示该站点文章确实不关联产品；不确定时保持 `draft`。`required_fields` 是当前模板实际需要的 CMS 字段；文章的作者、分类、模块、相关页等动态 ID 每次写入前重新查，不把参考文章的动态 ID 当成固定值。作者、URL、标题、关键词、描述和正文仍使用共享 CMS API 字段。资产是需要原样复用的 HTML 片段；没有固定组件时数组可为空。若参考页来自 CMS，可改用 `{"kind":"cms","page_id":789,"page_info_json":"evidence/reference-page-info.json"}`；纯 HTML 参考则必须同时提供三份 CMS 发现响应。

`images` 把 CMS 通用上传与图片资源发布流程同站点变量分开。新图上传后必须使用该次 `/cms/picture/upload` 响应中的图片 `publish_id` 单独发布资源，绝不能用文章页面 ID，也不因此生成或发布文章。目录、前台 URL 前缀、HTML 图片盒和所需格式从本站旧 HTML 与 CMS 图片库确定；如果该文章类型没有图片，写 `{"enabled": false}`。主图、正文横图、竖图、手机截图的尺寸规则写入 `html-contract.md`，不能照搬示例数值。

`html-contract.md` 至少记录：适用范围、旧 HTML 与 CMS 证据、模板与字段、模块顺序、标题层级、目录锚点、图片/表格/购买区/下载区/FAQ/结语结构、语言和链接规则、禁止改动的文字区域、图片目录、图片格式与尺寸、公开域名、草稿状态、需要人工判断的例外。不存在的模块标记为“无”。每条重要规则标明依据的参考文件或用户明确要求；不同旧 HTML 互相冲突时判断是否应拆成不同文章类型，不能混合为新样式。

`validate-html.py` 接收最终 HTML 文件路径；通过时退出 0，缺少必要模块、结构失衡、图片未回填或站点错误资源时退出非 0。它验证本规范的关键结构，不调用 PoGoskill 专用 `validate-article-html.py`。在采用新规范前用真实样本和一个故意删掉必要模块的样本验证校验器确实能拦截。

`validate-site-profile.py` 只检查 profile 的格式、文件存在和 CMS 参考页证据匹配；它不证明设计规则正确，也不替代站点专用 HTML 校验器。`status: ready` 还必须以人工复核参考样本和站点专用校验结果为前提。

## 后续使用

文章任务先通过 `validate-site-profile.py`，再执行 `$cms-site-article-assistant`。写草稿前重新实时核对 CMS 字段及本站取值，按 profile 渲染全文，运行站点校验器和来源/图片完整度检查；写后回读同样检查。新站点按本站规则建立图片 manifest：每个 DOCX 图片出现位置对应一项，`html_urls` 列出该站点要求的格式 URL；用 `validate-source-images.py` 对账。若本站也采用原图 + WebP 成对上传，可复用现有 `cms-upload-image-pairs.ps1`，显式传入 profile 的 `site.id`、目标 `cms_directories` 和 `public_url_prefix`；上传后用 `cms-publish-image-resources.ps1` 和真实图片 `publish_id` 单独发布资源。HTML 回填仍使用本站 `markup_asset`，不套用 PoGoskill 图片盒。若本站采用不同格式组合，则先实现并验证对应格式的上传处理器，再走同一图片资源发布流程。
