# CMS 草稿完成门槛

以下项目全部有证据才算完成：

| 阶段 | 必须证据 |
| --- | --- |
| 源文完整读取 | `inspect-docx-structure.py` 产出的结构 JSON，含全部段落、表格和图片关系 |
| CMS 字段确认 | 实时 API 返回的站点、模板、分类、作者、产品、相关文章与 URL 查重结果 |
| HTML 完整 | `validate-article-html.py` 返回 `ok: true` |
| 下载区完整 | 唯一正文 CTA；两个 `secure-btn`、两个 `secure-download`，并位于完整介绍之后、步骤 H3 之前 |
| 图片完整 | DOCX 正文图全部完成 fallback/WebP；Guide 图按指定名称唯一命中；`IMAGE_PENDING = 0` |
| CMS 写入 | `page/add` 或已确认目标的 `page/update` 返回 `code: 0`、页面 ID 与 `request_id` |
| CMS 回读 | `page/info` 返回相同页面 ID、完整正文和草稿状态 |
| 来源覆盖 | `compare-docx-to-cms-page.py` 报告无未解释缺失区块；有编辑性改写时逐条记录对应关系 |
| 视觉审查 | 当前草稿的 1440px 桌面与 390px 手机预览均无遮挡、溢出或模块缺失 |
| 安全状态 | 未调用 `page/make` 或 `pagepublish/publish`，未删除或修改无关旧文章 |

任一项缺失都不得输出 `Draft ready for review`。

