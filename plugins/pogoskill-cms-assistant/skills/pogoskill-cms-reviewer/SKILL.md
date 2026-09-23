---
name: pogoskill-cms-reviewer
description: 独立审查 PoGoskill 台湾站 CMS 草稿的元数据、HTML、来源覆盖和图片双格式；当前不执行 AI 页面预览，默认只读，不修改或发布。
---

# PoGoskill CMS Reviewer

独立于发布 Agent 验收草稿。先回读 `/cms/page/info`，确认站点 `324`、模板 `9916`、页面版本和正文，再执行 HTML、图片与来源覆盖的机械审查。

## 数据与 HTML

- 核对 subject、SEO 字段、URL、作者、分类、相关文章、产品和自定义字段。
- 按 Publisher 的 [Luna HTML 固定执行契约](../pogoskill-cms-publisher/references/luna-html-contract.md) 审查正文骨架：目录必须使用 `nav-list1`，不得出现 `article-toc`；section/H2/目录锚点一一对应；普通 H3 必须使用 `h3-triangle`，FAQ 必须使用 `h3-faq faq1`；拒绝裸列表和未包入 `table-box overflow-auto` 的表格。
- 正文不得有 H1；目录锚点与 section ID 一一对应；标准 Buy Box 必须恰好一个。
- PoGoskill 模块必须先完整写完介绍、适用情境、操作思路、作用与优势，再原样放入 Publisher 的 `assets/download-cta.html`；下载区必须有两个 `secure-btn` 和两个 `secure-download` 安全下载框。按钮下方必须紧接较大的现有 H3“PoGoskill 操作步驟”，随后才进入 `step-cont`。若下载区被简化、按钮过早出现，或“PoGoskill 操作步驟”只有 `section-label` 小标签而没有 H3，判定为结构不合格。
- 每个 `step-cont > li` 必须以 `<p><span>步驟 N</span><label><strong>短標題：</strong>普通正文。</label></p>` 开头。`p` 只能直接包含步骤徽标和一个无 class 的 `label`；加粗标题只能位于 `label` 开头。图片盒必须是该 `<p>` 后面的同级元素。把 `strong` 或正文直接放在 `p` 下时，判定为会产生多列挤压的结构错误。
- 将同分类正常上线文章作为结构基准；拒绝基准中不存在的新文本框、提示框、卡片、彩色背景框、引用框、CSS class、局部 CSS、标题样式或下载框架。
- 每个已完成图片盒必须是 `img-wrap text-center > picture > source[type=image/webp] + img`，两者同 basename、同尺寸，fallback 为 JPG/PNG，ALT 为自然繁体中文。
- 图片 `data-src/data-srcset` 必须使用 `https://tw.pogoskill.com/images/` 前台地址；出现 `site.p.cms.afirstsoft.cn`、`attachment=1`、错误站点域名或哈希结尾文件名时直接判定 `FAIL`。
- 对每对图片核对 manifest、上传 request_id、publish_id、CMS 返回 URL、尺寸和文件名；不得把图片上传记录发布。
- 任一 `IMAGE_PENDING`、本地路径、假 URL、坏图、单格式图片、尺寸不一致或标签未闭合均为发布阻断。
- 审查前先运行 Publisher 要求的 `validate-article-html.py`，并读取 DOCX/CMS 完整度比较结果；脚本失败或存在未解释缺失区块时直接判定 `FAIL`。

## 页面预览状态

当前暂不执行 AI 桌面／手机页面预览，也不要求截图或 DOM 视觉检测。不得为了预览而打开浏览器、登录 CMS、生成页面或发布。只根据 CMS API 回读、确定性 HTML 校验、图片 manifest 与来源覆盖结果作出审查结论。

## 判定

- `PASS`：数据、HTML、来源覆盖和所有图片检查全部通过。
- `PASS WITH IMAGE HOLD`：只有已知图片占位未补；仍禁止 make/publish。
- `FAIL`：存在字段、HTML、来源覆盖或图片问题。
