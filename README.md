# PoGoskill CMS 文章助手

这是 PoGoskill 团队使用的 Codex 插件 Marketplace，繁中站与英文站规则彼此独立，包含：

- 台湾站 V2 文章 HTML 转换、机械校验与 CMS 草稿回读
- 英文站 V2 文章 HTML 转换、固定英文下载区与 Buy Box、CMS 草稿回读
- JPG/PNG 与 WebP 图片处理、上传及回填
- CMS 草稿字段、HTML、来源覆盖和图片审查（AI 页面预览暂时停用）

默认安全规则：只创建草稿；不生成、不发布、不删除文章，也不修改旧文章。任何生成或发布操作都需要使用者另行明确授权。

## 让 AI 自动安装

把本仓库地址交给组员的 Codex AI，并发送下面这句话：

> 请从 Git 仓库安装 PoGoskill CMS 文章助手：`https://github.com/Albzh99/pogoskill-cms-assistant-marketplace.git`。按照仓库根目录 `SETUP.md` 完成 Marketplace 和插件安装。需要 CMS API Key 时，先替我启动保存命令并让终端停在等待提示；然后让我复制 Key，回到终端只按 Enter。不要让我把 Key 粘贴进终端或发到聊天里。安装完成后请让我新建一个任务再使用插件。

组员的电脑必须已经：

1. 安装 Codex 桌面版或 Codex CLI；
2. 安装 Git；
3. 能正常访问 GitHub。

API Key 不在仓库中，也不得提交到 Git。

## 站点必须分开使用

- 繁中站：使用 `$pogoskill-cms-article-assistant`，目标为 `pogoskilltw` / `tw.pogoskill.com`。
- 英文站：使用 `$pogoskill-cms-en-publisher`，目标为 `pogoskill` / `www.pogoskill.com`。

两个技能共享安全的 API 调用与执行证据框架，但不会共享语言、站点 ID、模板 ID、下载链接或 Buy Box 文案。
