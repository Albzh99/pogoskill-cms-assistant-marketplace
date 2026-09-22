---
name: pogoskill-cms-reviewer
description: 独立审查 PoGoskill 台湾站 CMS 草稿，核对元数据、图片双格式和 CMS 本地桌面/手机预览；默认只读，不修改或发布。
---

# PoGoskill CMS Reviewer

独立于发布 Agent 验收草稿。先回读 `/cms/page/info`，确认站点 `324`、模板 `9916`、页面版本和正文，再打开 CMS 本地预览。

## 数据与 HTML

- 核对 subject、SEO 字段、URL、作者、分类、相关文章、产品和自定义字段。
- 按 Publisher 的 [Luna HTML 固定执行契约](../pogoskill-cms-publisher/references/luna-html-contract.md) 审查正文骨架：目录必须使用 `nav-list1`，不得出现 `article-toc`；section/H2/目录锚点一一对应；普通 H3 必须使用 `h3-triangle`，FAQ 必须使用 `h3-faq faq1`；拒绝裸列表和未包入 `table-box overflow-auto` 的表格。
- 正文不得有 H1；目录锚点与 section ID 一一对应；标准 Buy Box 必须恰好一个。
- PoGoskill 模块必须先完整写完介绍、适用情境、操作思路、作用与优势，再原样放入 Publisher 的 `assets/download-cta.html`；下载区必须有两个 `secure-btn` 和两个 `secure-download` 安全下载框。按钮下方必须紧接较大的现有 H3“PoGoskill 操作步驟”，随后才进入 `step-cont`。若下载区被简化、按钮过早出现，或“PoGoskill 操作步驟”只有 `section-label` 小标签而没有 H3，判定为结构不合格。
- 将同分类正常上线文章作为结构基准；拒绝基准中不存在的新文本框、提示框、卡片、彩色背景框、引用框、CSS class、局部 CSS、标题样式或下载框架。
- 每个已完成图片盒必须是 `img-wrap text-center > picture > source[type=image/webp] + img`，两者同 basename、同尺寸，fallback 为 JPG/PNG，ALT 为自然繁体中文。
- 对每对图片核对 manifest、上传 request_id、publish_id、CMS 返回 URL、尺寸和文件名；不得把图片上传记录发布。
- 任一 `IMAGE_PENDING`、本地路径、假 URL、坏图、单格式图片、尺寸不一致或标签未闭合均为发布阻断。
- 审查前先运行 Publisher 要求的 `validate-article-html.py`，并读取 DOCX/CMS 完整度比较结果；脚本失败或存在未解释缺失区块时直接判定 `FAIL`。

## 真实预览

- CMS 本地预览必须是当前草稿版本，不得用线上旧页替代。
- 检查约 1440px 桌面与 390px 手机，并滚动到底触发懒加载。
- 检查图片加载、比例、拉伸、溢出、异常留白，以及文字是否被导航、浮层、CTA、侧栏或 Buy Box 遮挡。
- 确认主图实际尺寸为 850×460；竖图不占满长屏；图片与上下文语义一致，步骤图与对应产品操作一一匹配。
- 检查表格、FAQ、目录、视频、平台切换和 Buy Box 交互。
- 保存必要截图。无法操作真实预览时明确标注“真实视觉检查未完成”，不得给 PASS。

## 判定

- `PASS`：数据、HTML、所有图片和桌面/手机真实预览全部通过。
- `PASS WITH IMAGE HOLD`：只有已知图片占位未补；仍禁止 make/publish。
- `FAIL`：存在字段、HTML、图片、遮挡、溢出或交互问题，或真实预览未完成。
