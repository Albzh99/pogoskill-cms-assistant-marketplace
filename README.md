# PoGoskill CMS 文章助手

这是团队使用的 Codex CMS 插件 Marketplace。PoGoskill 繁中站与英文站规则彼此独立；其他网站先建立自己的文章规范，再使用通用文章流程。包含：

- 台湾站 V2 文章 HTML 转换、机械校验与 CMS 草稿回读
- 英文站 V2 文章 HTML 转换、固定英文下载区与 Buy Box、CMS 草稿回读
- JPG/PNG 与 WebP 图片处理、上传及回填
- CMS 草稿字段、HTML、来源覆盖和图片审查（AI 页面预览暂时停用）
- 为新网站和新文章类型建立独立的 profile、HTML 契约、固定组件与站点校验器

默认安全规则：文章只创建或更新草稿，不生成、不发布、不删除，也不修改无法确认归属的旧文章。新上传图片会使用其图片上传 `publish_id` 单独发布到云端，确保前台 URL 可用；图片发布绝不等于文章发布。

## 让 AI 自动安装

把本仓库地址交给组员的 Codex AI，并发送下面这句话：

> 请从 Git 仓库安装或更新到最新版 PoGoskill CMS 文章助手：`https://github.com/Albzh99/pogoskill-cms-assistant-marketplace.git`。按照仓库根目录 `SETUP.md` 完成 Marketplace 和插件安装，不要复用旧消息中的版本号或缓存路径。需要 CMS API Key 时，先替我启动不带 `-Prompt` 的保存命令，并把该运行会话真正打开到 Codex 可见终端；确认我能看到“请现在复制完整的 CMS API Key”后，再让我复制 Key并回到终端只按 Enter。保存进程退出后，立即用同一插件根目录运行 `cms-check-api-key.ps1`；检查通过才算完成。不要让我把 Key 粘贴进终端或发到聊天里。安装完成后请让我新建一个任务再使用插件。

组员的电脑必须已经：

1. 安装 Codex 桌面版或 Codex CLI；
2. 安装 Git；
3. 能正常访问 GitHub。

API Key 不在仓库中，也不得提交到 Git。首次保存后会写入 Windows DPAPI 加密、仅当前用户可读且独立于插件版本的本地存储；Credential Manager 可用时也会保存一份。遇到 Windows `1312` 时自动使用本地副本，不应在每个新任务中重新索取。

如果 AI 给出的脚本路径包含旧版本号，或声称“终端已打开”但界面没有终端面板，说明它没有完成新版交互流程。应先更新插件，再由 AI 创建终端运行会话并把该会话显示到 Codex 底部面板；不能让同事手工寻找缓存目录。

已经安装过的同事可让 AI 执行 `codex plugin marketplace upgrade pogoskill-team`，再执行 `codex plugin add pogoskill-cms-assistant@pogoskill-team`，然后新建任务加载新版。

不熟悉电脑操作的同事可直接下载 [PoGoskill CMS 文章助手同事试用指南](docs/PoGoskill%20CMS%20文章助手同事试用指南.docx)。手册逐步说明如何向管理员申请 API Key、让 AI 安装插件、安全保存 Key，以及分别试用繁中站和英文站文章。

## 安装后怎样使用

每篇文章请新建一个 Codex 任务，只附上一种语言的一篇 DOCX。不要在同一任务中同时处理繁中站和英文站文章。

### 其他公司网站：先建规范

首次处理一个新网站或不同文章类型时，给 AI 目标网站、文章类型和至少一篇同类型的正常参考文章 URL／CMS 页面 ID，然后说：

> 使用 `$cms-site-standard-builder` 为这个网站和文章类型建立独立规范。通过 CMS API 读取真实参考文章、模板字段、图片目录和现有组件，生成 `site-profiles/<站点>/<文章类型>/` 的 profile、HTML 契约、组件样本和校验器。规范通过验证后告诉我如何复用；这一步不要上传文章。

以后处理该站点文章时，附上稿件并说：

> 使用 `$cms-site-article-assistant` 和对应站点 profile 完整处理这篇文章。先验证 profile，保留全部正文和图片，按该站点的模板与组件生成 HTML，运行站点校验器；我要求保存草稿时，使用 CMS POST API 保存并回读。不要调用文章生成或发布接口。

规范按“网站 + 语言 + 文章类型”隔离。新站点不会自动沿用 PoGoskill 的产品 ID、下载框、Buy Box、图片域名和尺寸。当前 PoGoskill 图片上传脚本只支持其两个站点；新站点第一次处理图片时需在建规范阶段补齐并验证该站点的图片处理器，不能直接套用旧脚本。

### 交稿前必须写进 DOCX 的内容

每篇稿件都要在文档开头或备注区提供参考样式，至少填写一种可核验来源：参考文章 URL、CMS 页面 ID 或可复制的现有 HTML。AI 必须先读取参考样式，再复用其中已存在的标题、目录、图片、表格、下载区、步骤与 Buy Box 结构。

- 需要新上传的正文图片：直接嵌入 DOCX 的实际出现位置，不要只写本地路径或另发一包无位置说明的图片。AI 会按文档位置提取，保留 JPG/PNG，生成同名 WebP 后成对上传。
- Guide 图片：不要重新嵌入或让 AI 猜图；在对应正文或步骤位置写 CMS `guides` 图片库中的准确文件名（含扩展名），例如 `guide-change-location-step-1.jpg`。AI 只能按该文件名精确检索并复用同名 fallback/WebP，不能换相似图或重新上传 Guide 图。
- 并排双图：如果 DOCX 或参考文章明确把两张图放在同一个区域并排展示，请保留两张图的左右顺序和各自下方的说明文字。AI 使用插件固定的响应式双图结构；桌面端每张图显示宽度不超过 400px，手机端自动改为上下排列，禁止把两张图强行挤在一行。
- 表格：普通表格按内容使用合理宽度并居中，不强制铺满正文，也不默认横向滚动。只有实际文字过长、在正文宽度内确实会挤压时，才切换为可横向滚动的宽表格；不能仅因列数多或横向排列就滚动。

可直接写入 DOCX：

```text
参考样式：
参考文章 URL / CMS 页面 ID / 现有 HTML：

新上传正文图片：
已直接嵌入 DOCX 对应位置。

Guide 图片：
在对应位置填写 CMS 准确文件名，例如：guide-change-location-step-1.jpg
```

### 繁中站文章

适用范围：繁体中文稿件，目标站点为 `pogoskilltw` / `https://tw.pogoskill.com`。必须调用完整流程技能 `$pogoskill-cms-article-assistant`，它会串联繁中 Publisher、图片 Pipeline 和 Reviewer。

附上 DOCX 后，把下面整段复制给 AI：

> 使用 `$pogoskill-cms-article-assistant` 完整处理这篇繁中 DOCX。严格使用台湾站 V2 模板和繁体中文；完整保留正文、表格、FAQ、图片、下载区与 Buy Box。Guide／操作步骤只允许改变 HTML 包装；源文已有短标题可以原样加粗，后面的说明文字必须逐字、原序保留，禁止改写、润色、缩写、补写或重排。结语最后一个首页链接必须使用 DOCX 实际提供的“最佳／最好……”工具关键词作为锚文本，后面的 `PoGoskill` 保持普通文字，禁止链接品牌名本身。DOCX 中指定名称的 Guide 图片从 CMS 图片库精确查找；其他随稿图片保留 JPG/PNG 并生成同名 WebP，成对上传后使用图片上传响应的 `publish_id` 单独发布图片资源，确认两个前台 URL 均可访问后再回填 HTML。写入前及 CMS 回读后必须对账源 DOCX 图片出现次数、manifest 项数与 HTML 回填数，三个数量完全一致才算通过，少一张禁止保存或声称完成。通过 CMS POST API 保存为草稿并回读核对。禁止调用 `/cms/page/make`，禁止发布文章页面，禁止删除或修改其他文章。没有页面 ID、草稿状态、写入 request_id 和回读 request_id 时，不得声称完成。

### 英文站文章

适用范围：英文稿件，目标站点为 `pogoskill` / `https://www.pogoskill.com`。必须调用 `$pogoskill-cms-en-publisher`；不得调用繁中 Publisher，也不得混用繁中站链接、产品 ID、下载区或 Buy Box。

附上英文 DOCX 后，把下面整段复制给 AI：

> 使用 `$pogoskill-cms-en-publisher` 完整处理这篇英文 DOCX，目标站点是 `www.pogoskill.com`。请用中文汇报执行进度、异常和最终结果，但文章正文与 HTML 文案必须保持自然英文。完整保留每个段落、表格、FAQ、图片、英文下载区和英文 Buy Box，并严格遵守英文 V2 HTML 契约。Guide／operation steps 只允许改变 HTML 包装；源文已有 lead phrase 可以原样加粗，后面的说明必须逐字、原序保留，禁止 paraphrase、polish、shorten、expand 或 reorder。结语中把 DOCX 实际提供的 `best ...` 工具关键词链接到英文站首页，后面的 `PoGoskill` 品牌名保持普通文字。Guide 图片只按 DOCX 指定的准确文件名查找；其他随稿 JPG/PNG 保留原图并生成同名 WebP，上传到正确的英文站目录，使用 `/cms/picture/upload` 返回的 `publish_id` 单独发布图片资源，确认两个前台 URL 可访问后再回填 HTML。英文手机截图必须使用 `max-height` 和自动宽高，不能使用固定像素 `max-width`。通过 POST API 保存并回读 CMS 草稿。禁止调用 `/cms/page/make`，禁止发布文章页面，禁止删除或修改其他文章。没有页面 ID、草稿状态、写入 request_id 和回读 request_id 时，不得声称完成。

### 只处理图片

如果不需要创建或修改文章草稿，只需处理当前文章的图片，可附上图片或 DOCX 后输入：

> 使用 `$pogoskill-cms-image-pipeline` 处理这些当前文章的真实图片。保留 JPG/PNG，生成同名 WebP，检查目标目录与重复文件，成对上传，并使用本次图片上传响应中的 `publish_id` 单独发布图片资源。确认两个前台 URL 均可访问后返回 manifest 和 request_id。禁止生成或发布文章页面。

重要区别：`/cms/pagepublish/publish` 在这里仅用于发布图片上传记录。允许传入的唯一 ID 是 `/cms/picture/upload` 本次返回且有上传 `request_id` 佐证的图片 `publish_id`；页面 ID 和 `/cms/page/make` 产生的文章发布 ID 一律禁止。

## 如何判断 AI 真的完成了

成功回复至少应包含：页面 ID、URL、`status = 5`、`sync_status = 1`、写入 `request_id`、回读 `request_id`、HTML 校验结果、源 DOCX 图片数、manifest 图片数、CMS 回读 HTML 图片数，以及“图片资源已发布，文章未生成、未发布”。三个图片数必须完全一致；少一张就会在写入前被机械阻断，不能保存草稿或声称完成。HTML 校验也会拦截 `` `n ``、字面 `\n` 等可见换行污染，并区分普通表格与真正需要滚动的宽表格。如果只说“正在处理”“已准备 payload”或没有这些证据，就不算完成。

两个站点共享安全的 API 调用与执行证据框架，但不会共享语言、站点 ID、模板 ID、下载链接或 Buy Box 文案。
