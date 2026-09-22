---
name: pogoskill-cms-article-assistant
description: 将一篇 PoGoskill 台湾站 DOCX 完整处理为图片齐全、通过机械校验并经 CMS 回读审查的草稿。适用于端到端文章任务；默认禁止生成、发布、删除或修改无法确认归属的旧文章。
---

# PoGoskill CMS 完整文章助手

负责从 DOCX 到可审查 CMS 草稿的完整闭环。不要只生成局部 HTML、只上传图片，或在尚未获得 CMS 回读证据时结束。

开始时完整读取并依次使用：

1. `../pogoskill-cms-publisher/SKILL.md` 与其中要求的 HTML/CMS 契约；
2. `../pogoskill-cms-image-pipeline/SKILL.md` 与图片契约；
3. `../pogoskill-cms-reviewer/SKILL.md` 与审查契约；
4. [完成门槛](references/completion-gates.md)。

## API Key 首次设置

如果 Windows Credential Manager 中没有 CMS Key，只让使用者把完整 Key 复制到剪贴板并回复“已复制”。然后由 Agent 自己运行插件根目录：

```powershell
pwsh -NoProfile -File scripts/cms-save-api-key.ps1
```

脚本默认从剪贴板读取、保存到 Windows Credential Manager 并清空剪贴板。不要要求使用者把 Key 发到聊天、写进命令行、文件或环境日志；也不要让使用者手动输入长命令。只有明确要求键盘隐藏输入时才加 `-Prompt`。

## 强制执行闭环

1. 建立当前文章独立工作目录，保留源 DOCX、结构 JSON、HTML、图片 manifest、API payload/response 和检查结果。
2. 先用 `inspect-docx-structure.py` 读取全文、表格与图片关系，列出章节、FAQ、图片和 Guide 文件名；不得只阅读开头或摘要。
3. 实时查询站点、模板、分类、作者、产品、相关文章和 URL 冲突。
4. 按 Publisher 契约生成完整 HTML。下载区与 Buy Box 必须直接复制资产文件，不得手写简化。
5. 按 Image Pipeline 完成所有正文图；Guide 图只按 DOCX 给出的准确名称查库。图片未齐不得伪装完成。
6. 运行 `validate-article-html.py`。返回非零时继续修复，禁止上传不合格 HTML。
7. 用户已明确要求保存草稿时，只用 CMS POST API 调用 `page/add` 或已确认目标的 `page/update`。禁止用浏览器表单代替 API；禁止 `page/make` 和发布。
8. 写入后立即 `page/info` 回读，并运行 `compare-docx-to-cms-page.py`。缺少正文、表格、FAQ、图片、结语、下载区或 Buy Box 时修复草稿并再次回读。
9. 使用 Reviewer 通过 API 回读和本地机械检查复核当前草稿的字段、HTML、图片、来源覆盖与安全状态。当前暂不执行 AI 桌面／手机页面预览，也不得因此阻断草稿完成。

## 持续执行要求

- Commentary 只能报告已发生且可验证的进度，例如已生成的文件、API `request_id` 或页面 ID；禁止只说“正在处理”后停止。
- 任务仍有安全、已授权的下一步时继续调用工具，不把剩余步骤交还给使用者。
- 命令仍在运行时轮询同一会话；网络瞬时失败最多重试三次。写请求结果不确定时先按 URL/标题查询，确认没有已创建草稿后再重试，防止重复文章。
- 只有遇到缺少必要源文件、凭据不存在、三次相同失败、关键 CMS 字段无法唯一确认或需要新增授权时才停止，并给出具体阻断证据。

## 最终报告

只有完成门槛全部通过后才能报告 `Draft ready for review`，并同时提供页面 ID、URL、草稿状态、HTML 校验、图片数量、来源完整度和回读 `request_id`。否则明确报告 `Image hold` 或 `Blocked`，不得说已经完成、已经上传或稍后继续。AI 页面预览目前停用，不要求也不报告桌面／手机预览结论。
