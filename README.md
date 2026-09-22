# PoGoskill CMS 文章助手

这是 PoGoskill 团队使用的 Codex 私有插件 Marketplace，包含：

- 台湾站 V2 文章 HTML 转换、机械校验与 CMS 草稿回读
- JPG/PNG 与 WebP 图片处理、上传及回填
- CMS 草稿字段、HTML、来源覆盖和图片审查（AI 页面预览暂时停用）

默认安全规则：只创建草稿；不生成、不发布、不删除文章，也不修改旧文章。任何生成或发布操作都需要使用者另行明确授权。

## 让 AI 自动安装

把本仓库地址交给组员的 Codex AI，并发送下面这句话：

> 请从 Git 仓库安装 PoGoskill CMS 文章助手：`https://github.com/Albzh99/pogoskill-cms-assistant-marketplace.git`。按照仓库根目录 `SETUP.md` 完成 Marketplace 和插件安装。需要 CMS API Key 时，只提示我复制 Key 到剪贴板，之后由你运行保存脚本；不要让我输入长命令，也不要要求我把 Key 发到聊天里。安装完成后请让我新建一个任务再使用插件。

组员的电脑必须已经：

1. 安装 Codex 桌面版或 Codex CLI；
2. 安装 Git；
3. 能正常访问 GitHub。

API Key 不在仓库中，也不得提交到 Git。
