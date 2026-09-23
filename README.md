# PoGoskill CMS 文章助手

这是 PoGoskill 团队使用的 Codex 插件 Marketplace，繁中站与英文站规则彼此独立，包含：

- 台湾站 V2 文章 HTML 转换、机械校验与 CMS 草稿回读
- 英文站 V2 文章 HTML 转换、固定英文下载区与 Buy Box、CMS 草稿回读
- JPG/PNG 与 WebP 图片处理、上传及回填
- CMS 草稿字段、HTML、来源覆盖和图片审查（AI 页面预览暂时停用）

默认安全规则：文章只创建或更新草稿，不生成、不发布、不删除，也不修改无法确认归属的旧文章。新上传图片会使用其图片上传 `publish_id` 单独发布到云端，确保前台 URL 可用；图片发布绝不等于文章发布。

## 让 AI 自动安装

把本仓库地址交给组员的 Codex AI，并发送下面这句话：

> 请从 Git 仓库安装 PoGoskill CMS 文章助手：`https://github.com/Albzh99/pogoskill-cms-assistant-marketplace.git`。按照仓库根目录 `SETUP.md` 完成 Marketplace 和插件安装。需要 CMS API Key 时，先替我启动保存命令并让终端停在等待提示；然后让我复制 Key，回到终端只按 Enter。不要让我把 Key 粘贴进终端或发到聊天里。安装完成后请让我新建一个任务再使用插件。

组员的电脑必须已经：

1. 安装 Codex 桌面版或 Codex CLI；
2. 安装 Git；
3. 能正常访问 GitHub。

API Key 不在仓库中，也不得提交到 Git。

不熟悉电脑操作的同事可直接下载 [PoGoskill CMS 文章助手同事试用指南](docs/PoGoskill%20CMS%20文章助手同事试用指南.docx)。手册逐步说明如何向管理员申请 API Key、让 AI 安装插件、安全保存 Key，以及分别试用繁中站和英文站文章。

## 安装后怎样使用

每篇文章请新建一个 Codex 任务，只附上一种语言的一篇 DOCX。不要在同一任务中同时处理繁中站和英文站文章。

### 繁中站文章

适用范围：繁体中文稿件，目标站点为 `pogoskilltw` / `https://tw.pogoskill.com`。必须调用完整流程技能 `$pogoskill-cms-article-assistant`，它会串联繁中 Publisher、图片 Pipeline 和 Reviewer。

附上 DOCX 后，把下面整段复制给 AI：

> 使用 `$pogoskill-cms-article-assistant` 完整处理这篇繁中 DOCX。严格使用台湾站 V2 模板和繁体中文；完整保留正文、表格、FAQ、图片、下载区与 Buy Box。DOCX 中指定名称的 Guide 图片从 CMS 图片库精确查找；其他随稿图片保留 JPG/PNG 并生成同名 WebP，成对上传后使用图片上传响应的 `publish_id` 单独发布图片资源，确认两个前台 URL 均可访问后再回填 HTML。通过 CMS POST API 保存为草稿并回读核对。禁止调用 `/cms/page/make`，禁止发布文章页面，禁止删除或修改其他文章。没有页面 ID、草稿状态、写入 request_id 和回读 request_id 时，不得声称完成。

### 英文站文章

适用范围：英文稿件，目标站点为 `pogoskill` / `https://www.pogoskill.com`。必须调用 `$pogoskill-cms-en-publisher`；不得调用繁中 Publisher，也不得混用繁中站链接、产品 ID、下载区或 Buy Box。

附上英文 DOCX 后，把下面整段复制给 AI：

> Use `$pogoskill-cms-en-publisher` to process this complete English DOCX for `www.pogoskill.com`. Preserve every paragraph, table, FAQ, image, download CTA, and Buy Box, and follow the fixed English V2 HTML contract. Resolve Guide images only by the exact filenames supplied in the DOCX. For other supplied JPG/PNG images, keep the original, create a same-basename WebP, upload both to the correct English CMS folder, publish only the image resources with the `publish_id` returned by `/cms/picture/upload`, and verify that both public URLs are readable before inserting them into HTML. Save and read back a CMS draft through POST APIs. Never call `/cms/page/make`, never publish the article page, and never delete or modify another article. Do not claim completion without the page ID, draft status, write request_id, and readback request_id.

### 只处理图片

如果不需要创建或修改文章草稿，只需处理当前文章的图片，可附上图片或 DOCX 后输入：

> 使用 `$pogoskill-cms-image-pipeline` 处理这些当前文章的真实图片。保留 JPG/PNG，生成同名 WebP，检查目标目录与重复文件，成对上传，并使用本次图片上传响应中的 `publish_id` 单独发布图片资源。确认两个前台 URL 均可访问后返回 manifest 和 request_id。禁止生成或发布文章页面。

重要区别：`/cms/pagepublish/publish` 在这里仅用于发布图片上传记录。允许传入的唯一 ID 是 `/cms/picture/upload` 本次返回且有上传 `request_id` 佐证的图片 `publish_id`；页面 ID 和 `/cms/page/make` 产生的文章发布 ID 一律禁止。

## 如何判断 AI 真的完成了

成功回复至少应包含：页面 ID、URL、`status = 5`、`sync_status = 1`、写入 `request_id`、回读 `request_id`、HTML 校验结果、图片数量，以及“图片资源已发布，文章未生成、未发布”。如果只说“正在处理”“已准备 payload”或没有这些证据，就不算完成。

两个站点共享安全的 API 调用与执行证据框架，但不会共享语言、站点 ID、模板 ID、下载链接或 Buy Box 文案。
