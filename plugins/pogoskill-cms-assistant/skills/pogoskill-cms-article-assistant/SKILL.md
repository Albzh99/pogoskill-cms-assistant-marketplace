---
name: pogoskill-cms-article-assistant
description: 将一篇 PoGoskill 台湾站 DOCX 完整处理为图片已单独发布、通过机械校验并经 CMS 回读审查的草稿。适用于端到端文章任务；禁止生成或发布文章、删除或修改无法确认归属的旧文章。
---

# PoGoskill CMS 完整文章助手

负责从 DOCX 到可审查 CMS 草稿的完整闭环。不要只生成局部 HTML、只上传图片，或在尚未获得 CMS 回读证据时结束。

开始时完整读取并依次使用：

1. [CMS 真实执行与证据契约](references/execution-contract.md)；
2. `../pogoskill-cms-publisher/SKILL.md` 与其中要求的 HTML/CMS 契约；
3. `../pogoskill-cms-image-pipeline/SKILL.md` 与图片契约；
4. `../pogoskill-cms-reviewer/SKILL.md` 与审查契约；
5. [完成门槛](references/completion-gates.md)。

执行证据契约优先于口头进度：没有真实工具调用、API 响应和写后回读时，不得声称 CMS 无法访问、正在执行或已经上传。

## API Key 首次设置

如果 Windows Credential Manager 中没有 CMS Key，优先采用“先启动命令、后复制”的交互流程。由 Agent 先在可见终端运行插件根目录：

```powershell
pwsh -NoProfile -File scripts/cms-save-api-key.ps1
```

脚本会先停在“请现在复制完整的 CMS API Key”提示。此时让使用者复制 Key，回到终端直接按 Enter；脚本随后才读取剪贴板、保存到 Windows Credential Manager 并清空剪贴板。不要让使用者把 Key 粘贴进终端、发到聊天、写进命令行、文件或环境日志。

如果 Agent 已经确认使用者提前复制完 Key，并且要通过非交互终端自动执行，则使用：

```powershell
pwsh -NoProfile -File scripts/cms-save-api-key.ps1 -FromClipboard
```

`-FromClipboard` 会立即读取剪贴板，不等待 Enter。只有使用者明确要求键盘隐藏输入时才使用 `-Prompt`。

## 强制执行闭环

1. 建立当前文章独立工作目录，保留源 DOCX、结构 JSON、HTML、图片 manifest、API payload/response 和检查结果。先从 DOCX 提取参考文章 URL、CMS 页面 ID 或现有 HTML；至少有一种参考样式。缺失时不得自行设计页面，应明确报告输入缺少参考样式。
2. 先用 `inspect-docx-structure.py` 读取全文、表格与图片关系，列出章节、FAQ、图片和 Guide 文件名；不得只阅读开头或摘要。
3. 实时查询站点、模板、分类、作者、产品、相关文章和 URL 冲突。
4. 按 Publisher 契约生成完整 HTML。下载区与 Buy Box 必须直接复制资产文件，不得手写简化。
5. 按 Image Pipeline 完成所有正文图。新上传正文图必须真实嵌入 DOCX 的目标位置；按该位置提取、转换和回填。Guide 图不要求嵌入，只读取 DOCX 对应位置写明的 CMS 准确文件名（含扩展名），并按名称精确查库；不进行语义猜图、相似图替换或 Guide 重传。新上传图片必须使用上传响应的图片 `publish_id` 单独发布并确认前台双格式可读；图片未齐不得伪装完成。
6. 运行 `validate-article-html.py`。返回非零时继续修复，禁止上传不合格 HTML。
7. 用户已明确要求保存草稿时，只用 CMS POST API 调用 `page/add` 或已确认目标的 `page/update`。禁止用浏览器表单代替 API；禁止 `page/make` 和发布文章页面。图片资源发布是前一步的必要流程，不属于文章发布。
8. 写入后立即 `page/info` 回读，并运行 `compare-docx-to-cms-page.py`。缺少正文、表格、FAQ、图片、结语、下载区或 Buy Box 时修复草稿并再次回读。
9. 使用 Reviewer 通过 API 回读和本地机械检查复核当前草稿的字段、HTML、图片、来源覆盖与安全状态。当前暂不执行 AI 桌面／手机页面预览，也不得因此阻断草稿完成。

## 持续执行要求

- Commentary 只能报告已发生且可验证的进度，例如已生成的文件、API `request_id` 或页面 ID；任何“正在处理”之后必须立即执行真实工具调用，禁止只说不做。
- 任务仍有安全、已授权的下一步时继续调用工具，不把剩余步骤交还给使用者。
- 命令仍在运行时轮询同一会话；未经真实 POST 和执行证据契约规定的重试，不得报告网络、权限或接口故障。写请求结果不确定时先按 URL/标题查询，确认没有已创建草稿后再重试，防止重复文章。
- 只有遇到缺少必要源文件、凭据不存在、三次相同失败、关键 CMS 字段无法唯一确认或需要新增授权时才停止，并给出具体阻断证据。

## 最终报告

只有完成门槛全部通过后才能报告 `Draft ready for review`，并同时提供页面 ID、URL、草稿状态、HTML 校验、图片数量、来源完整度和回读 `request_id`。否则明确报告 `Image hold` 或 `Blocked`，不得说已经完成、已经上传或稍后继续。AI 页面预览目前停用，不要求也不报告桌面／手机预览结论。
