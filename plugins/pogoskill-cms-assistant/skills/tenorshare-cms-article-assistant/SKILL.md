---
name: tenorshare-cms-article-assistant
description: 为 Tenorshare 任一产品、语言和独立站点，从 CMS 旧文章或用户提供的 HTML 学习本站规则，并将新稿完整保存为经回读验证的 CMS 草稿。适用于运营的一句话端到端文章任务；不生成或发布文章。
---

# Tenorshare 全站文章助手

运营只需说明产品和语言或网站，并附上新稿；旧 HTML 是可选参考。你负责从公司 CMS 发现准确站点、学习旧文章、处理图片、制作完整 HTML、保存并回读草稿。不要让运营查站点 ID、模板 ID、运行命令或编辑 JSON。用运营的语言沟通，保持新稿原语言及原文，未经授权不改写正文。

先读 [一站式执行契约](references/one-task-workflow.md)。此技能是同事唯一需要调用的入口；内部按需使用 `$cms-site-standard-builder` 和 `$cms-site-article-assistant`。PoGoskill 只是公司产品之一，不作为其他产品的样式或字段值来源。

目标站点必须由 CMS `site/list` 与网站域名交叉确认。若“产品 + 语言”对应多个有效站点，展示最多三个简明的站点网址供运营选择；不猜测。如果 CMS 中没有可用的同类旧文章，再请运营上传旧 HTML。不要因为没有用户上传的参考 HTML 而停止发现。

文章默认只保存草稿，不调用 `/cms/page/make` 或文章发布接口，不删除或覆盖无关旧页面。新图片上传后的资源发布与文章页面发布是两件事：仅使用这次图片上传返回的图片 `publish_id` 单独发布图片资源。成功必须有写入与回读的真实 `code: 0`、`request_id`、页面 ID、草稿状态和完整内容对账；缺一项不得说“已上传”。
