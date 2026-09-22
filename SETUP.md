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

API Key 不包含在 Git 仓库或分享包内。使用者只需先复制完整 API Key，然后告诉 AI“已经复制”。由 AI 自动定位已安装的 Marketplace 并运行：

```powershell
$marketplaces = codex plugin marketplace list --json | ConvertFrom-Json
$root = ($marketplaces.marketplaces | Where-Object name -eq 'pogoskill-team').root
pwsh -NoProfile -File (Join-Path $root 'plugins\pogoskill-cms-assistant\scripts\cms-save-api-key.ps1')
```

脚本会直接从剪贴板读取密钥，写入 Windows Credential Manager，并自动清空剪贴板；不会写进文件或命令历史。

不要把 `cms-save-api-key` 替换成 API Key，也不要把 API Key 发到聊天中。若必须使用键盘隐藏输入，可由 AI 加上 `-Prompt`。

## 使用方式

在新任务中附上 DOCX，然后说明：

> 使用 `$pogoskill-cms-article-assistant` 把这篇文章按 PoGoskill 台湾站 V2 模板制作完整 HTML，处理所有图片并保存、回读和审查 CMS 草稿。禁止生成、禁止发布、禁止修改旧文章。没有页面 ID、回读结果和桌面／手机预览结论不得报告完成。

完整文章助手会强制串联 Publisher、Image Pipeline 和 Reviewer，并使用机械校验脚本阻止混乱或不完整 HTML 上传。CMS 生成与发布始终需要额外、明确授权。
