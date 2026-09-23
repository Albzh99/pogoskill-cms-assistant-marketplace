# PoGoskill CMS 文章助手安装

## 推荐：让 AI 从 Git 仓库自动安装

把仓库地址交给 Codex AI，并要求它在终端执行：

```powershell
codex plugin marketplace add "https://github.com/Albzh99/pogoskill-cms-assistant-marketplace.git" --ref main
codex plugin add pogoskill-cms-assistant@pogoskill-team
```

`codex plugin marketplace add` 会自行获取公开 Git 仓库，不需要使用者手动下载或解压。

安装完成后，新建一个 Codex 任务，让新任务加载插件。

## 本地文件安装（备用）

将整个 `pogoskill-cms-assistant-marketplace` 文件夹复制到本机后，在 PowerShell 中运行：

```powershell
codex plugin marketplace add "此文件夹的完整路径"
codex plugin add pogoskill-cms-assistant@pogoskill-team
```

安装完成后新建一个 Codex 任务，让新任务加载插件。

## 保存 CMS API Key

API Key 不包含在 Git 仓库或分享包内。为避免终端无法粘贴，必须先运行命令，再复制 Key：

```powershell
$marketplaces = codex plugin marketplace list --json | ConvertFrom-Json
$root = ($marketplaces.marketplaces | Where-Object name -eq 'pogoskill-team').root
pwsh -NoProfile -File (Join-Path $root 'plugins\pogoskill-cms-assistant\scripts\cms-save-api-key.ps1')
```

命令启动后按以下顺序操作：

1. 等终端显示“请现在复制完整的 CMS API Key”；
2. 复制完整 API Key 到剪贴板；
3. 回到终端，不要粘贴，只按一次 Enter；
4. 脚本读取剪贴板，将 Key 写入 Windows Credential Manager，然后自动清空剪贴板。

Key 不会出现在终端、文件或命令历史。如果使用者已经提前复制完成，并由 AI 在非交互终端执行，可以在命令末尾加入 `-FromClipboard`，让脚本立即读取剪贴板。

不要把 `cms-save-api-key` 替换成 API Key，不要把 Key 粘贴进终端，也不要把 API Key 发到聊天中。若必须使用键盘隐藏输入，可由 AI 加上 `-Prompt`。

## 使用方式：繁中站

新建一个 Codex 任务，附上一篇繁中 DOCX，然后完整发送：

> 使用 `$pogoskill-cms-article-assistant` 完整处理这篇繁中 DOCX。严格使用台湾站 V2 模板和繁体中文；完整保留正文、表格、FAQ、图片、下载区与 Buy Box。DOCX 中指定名称的 Guide 图片从 CMS 图片库精确查找；其他随稿图片保留 JPG/PNG 并生成同名 WebP，成对上传后使用图片上传响应的 `publish_id` 单独发布图片资源，确认两个前台 URL 均可访问后再回填 HTML。通过 CMS POST API 保存为草稿并回读核对。禁止调用 `/cms/page/make`，禁止发布文章页面，禁止删除或修改其他文章。没有页面 ID、草稿状态、写入 request_id 和回读 request_id 时，不得声称完成。

完整文章助手会强制串联 Publisher、Image Pipeline 和 Reviewer，并使用机械校验脚本阻止混乱或不完整 HTML 上传。图片上传后会单独发布图片资源；文章生成与文章发布始终禁止，除非使用者提出一个新的、明确的文章发布任务。

## 使用方式：英文站

另开一个 Codex 任务，附上一篇英文 DOCX，然后完整发送：

> Use `$pogoskill-cms-en-publisher` to process this complete English DOCX for `www.pogoskill.com`. Preserve every paragraph, table, FAQ, image, download CTA, and Buy Box, and follow the fixed English V2 HTML contract. Resolve Guide images only by the exact filenames supplied in the DOCX. For other supplied JPG/PNG images, keep the original, create a same-basename WebP, upload both to the correct English CMS folder, publish only the image resources with the `publish_id` returned by `/cms/picture/upload`, and verify that both public URLs are readable before inserting them into HTML. Save and read back a CMS draft through POST APIs. Never call `/cms/page/make`, never publish the article page, and never delete or modify another article. Do not claim completion without the page ID, draft status, write request_id, and readback request_id.

不要让同一个任务同时处理繁中站和英文站文章。两个站点的模板、产品、下载链接、图片域名与内容资产不同。

## 只处理图片

如果不需要创建或更新文章，只处理当前文章图片，可发送：

> 使用 `$pogoskill-cms-image-pipeline` 处理这些当前文章的真实图片。保留 JPG/PNG，生成同名 WebP，检查目标目录与重复文件，成对上传，并使用本次图片上传响应中的 `publish_id` 单独发布图片资源。确认两个前台 URL 均可访问后返回 manifest 和 request_id。禁止生成或发布文章页面。

图片发布和文章发布不是同一件事。图片上传后的 `publish_id` 必须用于图片资源上云；页面 ID 或 `/cms/page/make` 返回的文章发布 ID 不得用于这个步骤。
