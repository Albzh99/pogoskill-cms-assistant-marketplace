# 新站点规范契约

## 输入和证据

- 用户至少给出目标网站或 CMS 站点，以及一种文章类型的正常文章 URL、CMS 页面 ID 或 HTML。优先通过 `site/list` 与 `page/info` 取得可核对的站点 ID、模板 ID、实际 HTML 和 `request_id`；若参考材料来自网站 HTML 而 CMS 无对应页面，记录来源并保持 profile 为 `draft`，直到 CMS 字段可核对。
- 参考文章应与目标文章类型相同；多个风格差异较大的文章类型分别建规范。先确认文章 URL、站点、语言、作者、分类、产品、模板字段和相关文章的实际取值，不从 PoGoskill 规则推断。
- 读取目标站点已使用的图片路径与 HTML 图片盒、原图/WebP 关系、主图尺寸、竖图展示、图片发布方式、Guide 图片复用方式。若某站点不用某模块，明确写“无”，不要硬塞 PoGoskill CTA 或 Buy Box。

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
  "references": [{"page_id": 789, "page_info_json": "evidence/reference-page-info.json"}],
  "html_contract": "html-contract.md",
  "validator": "validate-html.py",
  "assets": []
}
```

`product_ids` 为空只能表示该站点文章确实不关联产品；不确定时保持 `draft`。`required_fields` 是当前模板实际需要的 CMS 字段；文章的作者、分类、模块、相关页等动态 ID 每次写入前重新查，不把参考文章的动态 ID 当成固定值。资产是需要原样复用的 HTML 片段；没有固定组件时数组可为空。

`html-contract.md` 至少记录：适用范围、证据 URL/页面 ID、模板与字段、模块顺序、标题层级、目录锚点、图片/表格/CTA/FAQ/结语结构、语言和链接规则、禁止改动的文字区域、图片目录与公开域名、草稿状态、需要人工判断的例外。每条重要规则标明依据的参考页面或用户明确要求；冲突时把差异写清楚，不能混合为新样式。

`validate-html.py` 接收最终 HTML 文件路径；通过时退出 0，缺少必要模块、结构失衡、图片未回填或站点错误资源时退出非 0。它验证本规范的关键结构，不调用 PoGoskill 专用 `validate-article-html.py`。在采用新规范前用真实样本和一个故意删掉必要模块的样本验证校验器确实能拦截。

`validate-site-profile.py` 只检查 profile 的格式、文件存在和 CMS 参考页证据匹配；它不证明设计规则正确，也不替代站点专用 HTML 校验器。`status: ready` 还必须以人工复核参考样本和站点专用校验结果为前提。

## 后续使用

文章任务先通过 `validate-site-profile.py`，再执行 `$cms-site-article-assistant`。写草稿前重新实时核对 CMS 字段，按 profile 渲染全文，运行站点校验器和来源/图片完整度检查；写后回读同样检查。图片上传脚本目前只支持 PoGoskill 的两个站点 ID 和域名；新站点首次启用图片时，必须先针对新站点扩展或提供经测试的图片处理器，不能把 PoGoskill 参数强套进去。
