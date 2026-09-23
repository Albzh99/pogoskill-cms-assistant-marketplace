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

## 使用方式

繁中站在新任务中附上 DOCX，然后说明：

> 使用 `$pogoskill-cms-article-assistant` 把这篇文章按 PoGoskill 台湾站 V2 模板制作完整 HTML，处理所有图片并保存、回读和审查 CMS 草稿。禁止 AI 页面预览、禁止生成、禁止发布、禁止修改旧文章。没有页面 ID 和回读结果不得报告完成。

完整文章助手会强制串联 Publisher、Image Pipeline 和 Reviewer，并使用机械校验脚本阻止混乱或不完整 HTML 上传。CMS 生成与发布始终需要额外、明确授权。

英文站附上英文稿件或 HTML，然后说明：

> 使用 `$pogoskill-cms-en-publisher` 按 www.pogoskill.com 的英文 V2 契约制作完整 HTML；下载区和 Buy Box 必须复制英文固定资产，保存后回读 CMS 草稿。禁止生成、禁止发布、禁止修改旧文章。

不要让同一个任务同时处理繁中站和英文站文章。两个站点的模板、产品、下载链接与内容资产不同。
