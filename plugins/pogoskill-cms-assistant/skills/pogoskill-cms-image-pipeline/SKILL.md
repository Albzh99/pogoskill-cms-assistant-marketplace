---
name: pogoskill-cms-image-pipeline
description: 为 PoGoskill 台湾站文章提取真实 JPG/PNG 素材、生成同名 WebP、成对上传 CMS 并安全回填 V2 图片盒。适用于文章图片处理；不用于生成虚构图片、覆盖既有资源、生成页面或发布。
---

# PoGoskill CMS Image Pipeline

把用户提供且确实属于当前文章的图片处理成 CMS V2 可预览的双格式图片盒。

开始前读取 [references/image-contract.md](references/image-contract.md)。在当前项目的文章工作目录运行本技能 `scripts/` 下的确定性脚本；API Key 只由插件根目录 `scripts/CmsCredential.ps1` 从 Windows 凭据管理器读取。

## 权限边界

- 读取、提取、转换和本地验证默认允许。
- 只有用户已明确要求把当前文章及其图片写入 CMS 时，才可用 `cms-upload-image-pairs.ps1 -Execute` 上传。
- 上传只产生待发布记录；记录 `publish_id`，绝不调用 `/cms/pagepublish/publish`、`/cms/page/make` 或删除接口。
- 不上传测试图、占位图、AI 猜测图或 DOCX 中未被正文引用的媒体。
- 不覆盖无法证明归属的已有文件。上传前后使用 `/cms/picture/list` 查重与回读，并继续用源文件 SHA-256 前缀命名，避免误覆盖。

## 工作流

1. 对 PoGoskill 下载、安装、操作步骤和产品界面图，只读取 DOCX 在对应位置写明的准确图片名称，再用该名称查询 `/cms/picture/list` 的 `guides`。必须唯一找到 fallback 原图与同名 WebP 后原位复用；缺失、重名或无法唯一确认时停止，不自行按语义猜图、换相似图或新上传 Guide 图。用户为游戏正文配好的图片则优先新上传，只查同名冲突和完全重复文件，不用相似图库图片替换。
2. 用 `extract-docx-images.ps1` 按 `document.xml` 的图片关系顺序提取正文实际引用的 JPG/PNG，不盲目复制 `word/media`。
3. 为每张图确定用途、所在段落和目标目录：Pokémon GO 游戏图用 `pokemon-ios`，Pikmin Bloom 游戏图用 `pikmin`，PoGoskill 下载/安装/步骤/产品界面用 `guides`。
4. 人工或语义映射补齐每张图的 `image_key`、繁体中文 `alt`、语义化 basename 和 `max_width`。不得把 DOCX 的 `descr` 自动当作最终 ALT。
5. 主图先处理为 850×460；其他图片保持比例，横图不超过正文需求，竖图限制展示宽高。随后用 `convert-image-pairs.ps1` 保留 JPG/PNG 并生成同 basename WebP。
6. 上传前用 `/cms/picture/list` 检查目标文件名与完全重复项，确认目标目录真实存在后上传 fallback 与 WebP。必须验证 `code === 0`、`total === 2`、`err_name_files` 为空、两者尺寸一致，并回查列表。
7. 用上传响应返回的 `upload` URL 生成草稿图片盒；不要自己拼接 host、query string 或 CDN URL。
8. 用 `apply-image-manifest.ps1` 按唯一 `image-key` 回填，不按“第几个图片盒”猜测。回填后交给 Reviewer 做桌面 1440px 与手机 390px 真实预览。

## 停止条件

- 没有真实图片：保留 `IMAGE_PENDING`，报告 Image hold。
- 转换器不可用、尺寸不一致、文件超过 30 MB、命名不合法、目录不存在或上传仅成功一个格式：停止，不改 CMS 正文。
- 占位数量、`image-key`、原区块哈希或上下文不匹配：停止，不进行模糊替换。
- 图片 URL 无法读取或实际解码失败：停止，不报告图片完成。
- 主图不是 850×460、文件名不具语义、目标目录错误、步骤图与 DOCX 指定名称不对应、竖图过高、Guide 名称无法唯一命中，或任何图片存在同名/完全重复冲突：停止，不写入 CMS。
