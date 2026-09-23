# CMS 草稿完成门槛

以下项目全部有证据才算完成：

| 阶段 | 必须证据 |
| --- | --- |
| 源文完整读取 | `inspect-docx-structure.py` 产出的结构 JSON，含全部段落、表格和图片关系 |
| 参考样式 | DOCX 提供参考文章 URL、CMS 页面 ID 或现有 HTML中的至少一项；已读取并记录实际采用的参考来源 |
| CMS 字段确认 | 实时 API 返回的站点、模板、分类、作者、产品、相关文章与 URL 查重结果 |
| HTML 完整 | `validate-article-html.py` 返回 `ok: true` |
| 结语链接 | 最后一个结语 section 使用源文提供的关键词短语链接正确站点首页；`PoGoskill` 位于链接后且不是锚文本 |
| 下载区完整 | 主介绍 CTA 位于完整介绍之后及步骤标题附近，桌面按钮组固定居中；每组均有两个 `secure-btn`、两个 `secure-download`。只有源文 FAQ 明确推荐 PoGoskill 时才允许第二组对应语言 CTA，全文最多两组 |
| 图片完整 | 需新上传的正文图已嵌入 DOCX 实际位置并全部完成 fallback/WebP；Guide 图在对应位置提供含扩展名的 CMS 准确文件名并唯一命中；未猜图、换相似图或重传 Guide 图；新图具备上传 request_id、图片 publish_id、图片发布 request_id；图片资源发布成功且前台双格式可读；英文手机截图使用 `max-height` 和自动宽高；`IMAGE_PENDING = 0`；繁中/英文分别使用正确前台公开图片域名，正文无 CMS 后台 URL、`attachment=1` 或文件名哈希 |
| CMS 写入 | `page/add` 或已确认目标的 `page/update` 返回 `code: 0`、页面 ID 与 `request_id` |
| CMS 回读 | `page/info` 返回相同页面 ID、完整正文和草稿状态 |
| 来源覆盖 | `compare-docx-to-cms-page.py` 报告无未解释缺失区块；有编辑性改写时逐条记录对应关系 |
| 安全状态 | 未调用 `page/make`、未发布文章页面；`pagepublish/publish` 仅接收有当前图片上传 request_id 佐证的图片 publish_id；未删除或修改无关旧文章 |

任一项缺失都不得输出 `Draft ready for review`。

当前暂不把 AI 桌面／手机页面预览列为完成门槛；仍须完成 HTML 机械校验、CMS 回读和来源覆盖检查。
