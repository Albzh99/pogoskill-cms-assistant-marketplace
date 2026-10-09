# Tenorshare CMS 文章助手安装和跨平台执行

这是给 AI 执行的技术说明。运营同事只看 [START-HERE.md](START-HERE.md)，不用手工输入这里的命令。仓库和插件的技术 ID 暂保留 `pogoskill-cms-assistant`，但产品范围是 Tenorshare 全公司，而不是只处理 PoGoskill。

## 推荐：让 AI 从 Git 仓库自动安装

AI 在 Windows PowerShell 或 macOS Terminal 中运行相同的 Codex CLI 命令，安装前先确认 `codex` 可用：

```text
codex plugin marketplace add "https://github.com/Albzh99/tenorshare-cms-assistant-marketplace.git" --ref main
codex plugin add pogoskill-cms-assistant@pogoskill-team
```

`codex plugin marketplace add` 会自行获取公开 Git 仓库，不需要使用者手动下载或解压。

若电脑已经安装过旧版，必须先让 AI 更新 Marketplace 的 Git 仓库，再重新执行 `codex plugin add pogoskill-cms-assistant@pogoskill-team`。后续命令必须从当前 Marketplace 根目录动态定位插件；禁止复制旧消息中带 `1.0.0+codex...` 的缓存路径。

```powershell
codex plugin marketplace upgrade pogoskill-team
codex plugin add pogoskill-cms-assistant@pogoskill-team
```

安装完成后，新建一个 Codex 任务，让新任务加载插件。

## 本地文件安装（备用）

将整个 `tenorshare-cms-assistant-marketplace` 文件夹复制到本机后，由 AI 在当前系统的终端运行：

```text
codex plugin marketplace add "此文件夹的完整路径"
codex plugin add pogoskill-cms-assistant@pogoskill-team
```

安装完成后新建一个 Codex 任务，让新任务加载插件。

## 保存 CMS API Key

AI 先检查，不要每次重新索取。Windows 从当前插件根目录运行 `scripts/cms-check-api-key.ps1`；macOS 运行 `python3 scripts/cms-macos.py check-key`（可使用 Codex 配置的 bundled Python）。检查通过就继续 CMS 任务，禁止再次要求 Key。检查失败后才打开用户可见的保存会话，不能把 Key 当命令参数或消息文本传递。

保存 Key 后，AI 必须用本机可用 Python 3 运行插件 `scripts/verify-workstation.py`。它实际以现有凭据向 `/cms/site/list` 发只读 POST，只回报站点数量、`request_id` 和 WebP 编码能力，不显示 Key。Windows 找不到 PowerShell 时，AI 从当前 Codex 依赖中找 `pwsh.exe` 并传给 `--powershell`；macOS 不传此参数。预检失败时按其客观错误修复，不能说“安装完成”。预检通过只证明本机可读取 CMS，不证明任一新站点的草稿写入或图片发布已通过实测。

### Windows

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
4. 脚本读取剪贴板，将 Key 写入 Windows DPAPI 加密、仅当前 Windows 用户可读的稳定存储；Windows Credential Manager 可用时也会同时写入，随后自动清空剪贴板。

Key 不会以明文出现在终端、文件或命令历史。加密副本位于 `%LOCALAPPDATA%\PoGoskillCMS\OpenAPI.v1.dat`，不在 Git 仓库或插件缓存中，因此插件升级后仍可使用。如果使用者已经提前复制完成，并由 AI 在非交互终端执行，可以在命令末尾加入 `-FromClipboard`，让脚本立即读取剪贴板。

如果 Windows 显示错误 `1312（指定的登录会话不存在）`，新版脚本会自动使用受保护的本地存储，不应再次要求输入 Key。只有脚本明确报告两个存储位置都没有凭据时才需要重新保存。

AI 在每个新任务中应先运行 `scripts/cms-check-api-key.ps1`。它只返回“凭据可用／不存在”，不会显示 Key；检查通过后必须继续执行，不得再次询问。

### AI 必须怎样打开终端

这一步不应交给同事手工打开 PowerShell。AI 必须：

1. 从当前 Marketplace 根目录定位最新版脚本，不能使用旧对话里带版本号的缓存路径；
2. 用可持续跟踪的终端会话运行不带 `-Prompt`、不带 `-FromClipboard` 的 `cms-save-api-key.ps1`；
3. 等脚本显示“请现在复制完整的 CMS API Key”后，把同一个运行会话真正打开到 Codex 的可见终端面板；
4. 只有终端打开工具返回成功后，才能告诉使用者“终端已打开”；看不到终端时不得假装已经打开，也不得改让使用者手工输入长路径；
5. 使用者复制 Key 并在终端按 Enter 后，AI 必须继续等待同一进程退出；
6. 随后立即从同一个插件根目录运行 `cms-check-api-key.ps1`。只有它报告可用，才算保存成功。

如果使用者已经明确说“Key 已复制到剪贴板”，AI 可以直接从当前插件根目录运行 `cms-save-api-key.ps1 -FromClipboard`，不需要终端交互；执行后仍必须立即运行检查脚本。默认禁止使用 `-Prompt`，因为它要求粘贴而不是“复制后按 Enter”。

不要把 `cms-save-api-key` 替换成 API Key，不要把 Key 粘贴进终端，也不要把 API Key 发到聊天中。只有使用者明确要求键盘隐藏输入时，AI 才可加上 `-Prompt`。

### macOS

AI 从**当前安装的插件根目录**找到 `scripts/cms-macos.py`，确认可用的 Python 3，然后在可跟踪、用户可见的终端运行 `python3 scripts/cms-macos.py save-key`。脚本先等待；运营复制完整 Key，回到同一终端只按 Enter。脚本通过 `pbpaste` 读取剪贴板，用 macOS Keychain 保存，清空剪贴板，并在同一进程中验证。AI 再独立运行 `python3 scripts/cms-macos.py check-key`。Key 不写入脚本参数、聊天、仓库或明文文件。macOS 可能弹出系统钥匙串授权窗口；仅让用户完成系统原生授权，不要求在聊天里提供 Key。若 `python3` 或 Keychain 不可用，AI 应先定位 Codex bundled Python 或按机器实际情况处理依赖，不能声称已保存。

macOS JSON POST 使用 `python3 scripts/cms-macos.py request --path /cms/site/list --body <请求文件> --output <响应文件>`；页面写入额外加 `--execute`。图片可用 `upload-image --site-id ... --cms-path ... --file ... --output ... --execute`，再用该次响应文件执行 `publish-image --upload-response ... --output ... --execute`。`cms-macos.py` 会阻止页面生成、删除和把普通文章发布请求当成图片发布。图片原图加 WebP 的站点可用跨平台 `prepare-image-pair.py`（要求该 Python 运行时有 Pillow/WebP 编码）；DOCX 图片可用 `extract-docx-media.py` 提取。AI 自行运行这些命令，不让运营填写参数。

## PoGoskill 专用交稿要求

每篇 DOCX 都必须给出参考样式，可提供参考文章 URL、CMS 页面 ID 或现有 HTML，至少一项。需要上传的新正文图片必须直接嵌入 DOCX 的实际出现位置；不要只给文件夹或本地路径。Guide 图片不需要重新上传，请在对应位置写出 CMS `guides` 图片库的准确文件名（含扩展名），AI 只按名称精确复用，不猜图、不换相似图。

```text
参考样式：
参考文章 URL / CMS 页面 ID / 现有 HTML：

新上传正文图片：
已直接嵌入 DOCX 对应位置。

Guide 图片：
在对应位置填写 CMS 准确文件名，例如：guide-change-location-step-1.jpg
```

## 其他公司网站的一站式使用方式

首次学习旧文章必须走只读入口：Windows `scripts/cms-learning-request.ps1`，macOS `python3 scripts/cms-macos.py learn`。这两个入口在发出 CMS POST 前按查询路由白名单拦截写入；不得因为 CMS 全部使用 POST 就把上传、编辑或发布当成查询。学习阶段只写本机 profile，不对 CMS 做任何修改。日常已有 `ready` 规范后的草稿上传才使用正常写入工具，并仍需用户明确要求。

首次为某站点／语言／文章类型开通时，同事说明网站和语言，调用 `$tenorshare-cms-article-assistant`；助手通过 CMS `site/list`、`page/list`、`page/info` 建立独立规范，展示本站样本并等待运营确认，**首次建规范任务不写草稿**。以后上传新稿时直接读取本机已确认的 `ready` 规范，不每篇重新学习。旧 HTML 可选；只有 CMS 找不到同类参考时才向运营索要。站点不唯一时只问网址。各站共用 CMS POST API、作者／URL／关键词等字段名，以及新图片上传后用图片 `publish_id` 单独发布资源的流程；字段取值、站点链接、图片格式和全部 HTML 样式按本站规范确定。运营说明见 [START-HERE.md](START-HERE.md)。

## 使用方式：繁中站

新建一个 Codex 任务，附上一篇繁中 DOCX，然后完整发送：

> 使用 `$pogoskill-cms-article-assistant` 完整处理这篇繁中 DOCX。严格使用台湾站 V2 模板和繁体中文；完整保留正文、表格、FAQ、图片、下载区与 Buy Box。Guide／操作步骤只允许改变 HTML 包装；源文已有短标题可以原样加粗，后面的说明文字必须逐字、原序保留，禁止改写、润色、缩写、补写或重排。结语最后一个首页链接必须使用 DOCX 实际提供的“最佳／最好……”工具关键词作为锚文本，后面的 `PoGoskill` 保持普通文字，禁止链接品牌名本身。DOCX 中指定名称的 Guide 图片从 CMS 图片库精确查找；其他随稿图片保留 JPG/PNG 并生成同名 WebP，成对上传后使用图片上传响应的 `publish_id` 单独发布图片资源，确认两个前台 URL 均可访问后再回填 HTML。写入前及 CMS 回读后必须对账源 DOCX 图片出现次数、manifest 项数与 HTML 回填数，三个数量完全一致才算通过，少一张禁止保存或声称完成。通过 CMS POST API 保存为草稿并回读核对。禁止调用 `/cms/page/make`，禁止发布文章页面，禁止删除或修改其他文章。没有页面 ID、草稿状态、写入 request_id 和回读 request_id 时，不得声称完成。

完整文章助手会强制串联 Publisher、Image Pipeline 和 Reviewer，并使用机械校验脚本阻止混乱或不完整 HTML 上传。图片上传后会单独发布图片资源；文章生成与文章发布始终禁止，除非使用者提出一个新的、明确的文章发布任务。

## 使用方式：英文站

另开一个 Codex 任务，附上一篇英文 DOCX，然后完整发送：

> 使用 `$pogoskill-cms-en-publisher` 完整处理这篇英文 DOCX，目标站点是 `www.pogoskill.com`。请用中文汇报执行进度、异常和最终结果，但文章正文与 HTML 文案必须保持自然英文。完整保留每个段落、表格、FAQ、图片、英文下载区和英文 Buy Box，并严格遵守英文 V2 HTML 契约。Guide／operation steps 只允许改变 HTML 包装；源文已有 lead phrase 可以原样加粗，后面的说明必须逐字、原序保留，禁止 paraphrase、polish、shorten、expand 或 reorder。结语中把 DOCX 实际提供的 `best ...` 工具关键词链接到英文站首页，后面的 `PoGoskill` 品牌名保持普通文字。Guide 图片只按 DOCX 指定的准确文件名查找；其他随稿 JPG/PNG 保留原图并生成同名 WebP，上传到正确的英文站目录，使用 `/cms/picture/upload` 返回的 `publish_id` 单独发布图片资源，确认两个前台 URL 可访问后再回填 HTML。英文手机截图必须使用 `max-height` 和自动宽高，不能使用固定像素 `max-width`。通过 POST API 保存并回读 CMS 草稿。禁止调用 `/cms/page/make`，禁止发布文章页面，禁止删除或修改其他文章。没有页面 ID、草稿状态、写入 request_id 和回读 request_id 时，不得声称完成。

不要让同一个任务同时处理繁中站和英文站文章。两个站点的模板、产品、下载链接、图片域名与内容资产不同。

## 只处理图片

如果不需要创建或更新文章，只处理当前文章图片，可发送：

> 使用 `$pogoskill-cms-image-pipeline` 处理这些当前文章的真实图片。保留 JPG/PNG，生成同名 WebP，检查目标目录与重复文件，成对上传，并使用本次图片上传响应中的 `publish_id` 单独发布图片资源。确认两个前台 URL 均可访问后返回 manifest 和 request_id。禁止生成或发布文章页面。

图片发布和文章发布不是同一件事。图片上传后的 `publish_id` 必须用于图片资源上云；页面 ID 或 `/cms/page/make` 返回的文章发布 ID 不得用于这个步骤。
