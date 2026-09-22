# Luna HTML 固定执行契约

本文件专门约束 Luna 或其他只负责执行的 Agent。生成 PoGoskill 台湾站 V2 文章正文时，必须从这里复制现有组件结构，不得根据自己的审美发明 HTML、class 或 CSS。

## 1. 先决定文章层级

在写 HTML 前，先把 DOCX 内容整理成以下层级：

- 导语：2～4 个普通 `<p>`，不设标题。
- 主图：导语后放一个图片盒。
- 文章目录：只列主要章节。
- 主要章节：每个目录项对应一个 `<section id="partN">` 和一个 `<h2>`。
- 子章节：只有真正需要展开说明的独立主题才用 `<h3>`。
- FAQ：一个 H2 章节，问题使用 FAQ 专用 H3。
- 结语：最后一个 section。
- Buy Box：结语 section 结束后，正文最末尾放一个。

禁止把每个短段落、每个表格行、每个步骤或每个并列对象都做成 H3。两个相邻 H3 之间通常至少应有一段完整正文；只是标签或引导语时使用普通 `<p>` 或 `<p class="section-label"><strong>…</strong></p>`。

## 2. 整篇文章固定骨架

```html
<div>

<p>導語第一段。</p>

<p>導語第二段。</p>

<!-- 主圖圖片盒 -->

<ul class="list-filled-dot nav-list1">
  <li><a href="#part1">一、第一個主要章節</a></li>
  <li><a href="#part2">二、核心解法章節 <img class="tit-tips" src="https://images.pogoskill.com/hot-tips.png?w=100&amp;h=38" width="50" alt="熱門"></a></li>
  <li><a href="#part3">三、PoGoskill 介紹章節 <img class="tit-tips" src="https://images.pogoskill.com/hot-tips.png?w=100&amp;h=38" width="50" alt="熱門"></a></li>
  <li><a href="#part4">四、常見問題</a></li>
  <li><a href="#part5">結語</a></li>
</ul>

<section id="part1">
  <h2>一、第一個主要章節</h2>
  <p>正文。</p>
</section>

<section id="part2">
  <h2>二、核心解法章節</h2>
  <p>正文。</p>
</section>

<section id="part3">
  <h2>三、PoGoskill 介紹章節</h2>
  <p>正文。</p>
</section>

<section id="part4">
  <h2>四、常見問題</h2>
  <!-- FAQ 模組 -->
</section>

<section id="part5">
  <h2>結語</h2>
  <p>結語內容。</p>
</section>

<!-- 原樣貼入 assets/buybox.html；該資產最後一個 </div> 會關閉本文最外層 <div> -->
```

规则：

- 正文禁止 `<h1>`，CMS 用 `subject` 渲染 H1。
- 最外层只用普通 `<div>`，不得创建 `xxx-article` 等自定义 class。
- section ID 从 `part1` 连续编号，不得跳号或重复。
- 每个 section 的第一个内容必须是一个 H2。
- 目录 href 集合必须与 section ID 集合完全一致。
- 不使用 `<nav class="article-toc">`、嵌套目录 `<ul>` 或自行设计目录容器。

## 3. H2 与 H3

### H2：只表示目录中的主要章节

```html
<section id="part2">
  <h2>二、主要章節名稱</h2>
  <p>本章導入內容。</p>
</section>
```

### 普通 H3：必须使用站点现有三角标题

```html
<h3 class="h3-triangle">1. 真正的子章節標題</h3>

<p>該子章節的完整說明。</p>
```

同一 H2 下只有一个主题时不使用 H3。并列名称、角色、奖励和简短提示优先用列表或表格，不得连续堆叠多个裸 H3。

禁止：

```html
<h3>普通裸標題</h3>
<h3 style="...">自訂樣式標題</h3>
<h2 class="new-class">自創 H2 class</h2>
```

### PoGoskill 模块内的小标签

“PoGoskill 優勢”等辅助标签不消耗 H3 层级；但“PoGoskill 操作步驟”是下载按钮后正式进入步骤模块的标题，必须使用 H3，不能归入小标签：

```html
<p class="section-label"><strong>PoGoskill 優勢</strong></p>

<ul class="list-cont list-dark-dot">
  <li>一鍵修改 GPS 定位。</li>
  <li>依照文章內容描述對應功能。</li>
</ul>
```

## 4. 文章目录

固定使用：

```html
<ul class="list-filled-dot nav-list1">
  <li><a href="#part1">一、章節標題</a></li>
  <li><a href="#part2">二、核心解法 <img class="tit-tips" src="https://images.pogoskill.com/hot-tips.png?w=100&amp;h=38" width="50" alt="熱門"></a></li>
  <li><a href="#part3">三、PoGoskill 解法 <img class="tit-tips" src="https://images.pogoskill.com/hot-tips.png?w=100&amp;h=38" width="50" alt="熱門"></a></li>
</ul>
```

- 先理解文章，再选择“核心解决方案章节”和“PoGoskill 介绍章节”，不能固定套用 part4/part5。
- 每篇只给这两个有价值的目录项加 `.tit-tips`；不是所有项都加。
- 确属新功能或新内容时，可把图片换成 `new-tips.png`，alt 改为“最新”。
- 图标必须位于对应 `<a>` 内、标题文字之后。

## 5. 普通段落、强调与链接

```html
<p>普通正文內容。</p>

<p><strong>需要自然強調的短句。</strong></p>

<p>首次實際介紹 <a href="https://tw.pogoskill.com/">PoGoskill</a> 時加入官網連結。</p>
```

- 不用 `<br>` 模拟段落。
- 不用 `<div>` 包每一段文字。
- 不自行创建提示框、彩色框、引用框、卡片或背景。
- 第一次实际介绍 PoGoskill 和结语最后一次提到 PoGoskill 时链接官网；其他地方不机械重复。

## 6. 普通列表

无序重点列表固定使用：

```html
<ul class="list-cont list-dark-dot">
  <li>第一個重點。</li>
  <li>第二個重點。</li>
  <li>第三個重點。</li>
</ul>
```

不要输出裸 `<ul><li>…</li></ul>`。普通数字顺序若不是带图步骤，可用普通 `<ol>`，但只有原参考文章存在同类用法时才使用；产品操作步骤统一用 `step-cont`。

## 7. 表格

```html
<div class="table-box overflow-auto">
  <table>
    <thead>
      <tr>
        <th>欄位一</th>
        <th>欄位二</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>內容一</td>
        <td>內容二</td>
      </tr>
    </tbody>
  </table>
</div>
```

- 所有正文表格必须放在 `.table-box.overflow-auto` 内。
- 不给 `<table>`、`<th>` 或 `<td>` 添加自定义 style/class。
- 并列对象超过三个、属性适合横向比较时优先使用表格，避免制造大量 H3。

## 8. 图片盒

### 新上传的正文图片

```html
<div class="img-wrap text-center">
  <picture>
    <source class="lozad img-fluid"
            srcset="WEBP_UPLOAD_URL"
            data-srcset="WEBP_UPLOAD_URL"
            type="image/webp">
    <img class="lozad img-fluid"
         src="FALLBACK_UPLOAD_URL"
         data-src="FALLBACK_UPLOAD_URL"
         alt="描述圖片真實內容的繁體中文 ALT"
         style="max-width:850px;width:100%;height:auto;">
  </picture>
</div>
```

### CMS guides 中复用的现有图片

```html
<div class="img-wrap text-center">
  <picture>
    <source class="lozad img-fluid"
            srcset="https://tw.pogoskill.com/images/loading.svg"
            data-srcset="GUIDE_WEBP_URL"
            type="image/webp">
    <img class="lozad img-fluid"
         src="https://tw.pogoskill.com/images/loading.svg"
         data-src="GUIDE_FALLBACK_URL"
         alt="描述該步驟畫面的繁體中文 ALT"
         style="max-width:760px;width:100%;height:auto;">
  </picture>
</div>
```

竖向手机截图改用：

```html
style="max-height:520px;max-width:100%;width:auto;height:auto;"
```

- 主图必须实际为 850×460。
- `<source>` 使用 WebP，`<img>` 使用同 basename 的 JPG/PNG。
- 不能只写 `<img>`，不能缺少 `data-src/data-srcset`，不能伪造 URL。
- 新图使用上传接口返回的 URL；Guide 图只用 DOCX 指定名称在 CMS 查到的准确 URL。

## 9. PoGoskill 介绍、下载与操作步骤顺序

PoGoskill 模块必须遵循固定阅读顺序：先把 PoGoskill 的介绍、适用情境、操作思路、作用与优势文字完整写完；再放唯一一组正文下载 CTA；下载按钮之后才用站点现有较大 H3 标题“PoGoskill 操作步驟”开启步骤模块。

禁止在介绍段落刚结束时立即插入下载按钮。下载 CTA 必须位于整段说明文字和优势列表之后、操作步骤 H3 之前。也禁止把“PoGoskill 操作步驟”做成普通 `section-label` 小字标题。

固定结构：

```html
<p>首次实际介绍 <a href="https://tw.pogoskill.com/">PoGoskill</a> 的说明。</p>

<p>继续说明适用情境、操作思路与 PoGoskill 的实际作用。</p>

<p class="section-label"><strong>PoGoskill 優勢</strong></p>
<ul class="list-cont list-dark-dot">
  <li>優勢說明。</li>
</ul>

<!-- 上述介绍和优势文字全部结束后，再放唯一正文 CTA -->
<div class="dev-desktop">
  ...标准下载 CTA...
</div>

<h3 class="h3-triangle">PoGoskill 操作步驟</h3>

<ul class="step-cont" id="pogoskill-guide-step">
  ...步驟與圖片...
</ul>
```

“PoGoskill 操作步驟”必须使用 `h3-triangle`（或同分类已验证、语义等价的现有 H3 class），视觉层级要明显高于 `section-label`；不得使用裸 H3、H4 或自创 class。可以根据文章内容补充标题语义，但必须明确表示这是 PoGoskill 操作步骤。

正文下载 CTA 只放一次，位置必须是 PoGoskill 的完整介绍与优势内容之后、操作步骤 H3 之前。必须原样复制 `assets/download-cta.html`，不得手写简化版。下列结构中的 `secure-btn` 和 `secure-download` 就是下载按钮及其安全下载框，任何一层缺失都会导致页面样式不完整：

```html
<div class="dev-desktop">
  <div class="btn-groups" style="display:flex;justify-content:center;">
    <div class="secure-btn me-md-4 mb-md-0 mb-3">
      <a class="btn btn-primary btn-xl d-flex align-items-center"
         href="https://download.pogoskill.com/go/pogoskill_7925.exe">
        <svg class="me-2" width="24" height="24">
          <use xlink:href="#win-path"></use>
        </svg>
        免費試用
      </a>
      <div class="secure-download">
        <img src="https://images.pogoskill.com/v2/article/protect.svg" alt="安全下載">
        <span>安全下載</span>
      </div>
    </div>
    <div class="secure-btn">
      <a class="btn btn-primary btn-xl d-flex align-items-center"
         href="https://download.pogoskill.com/go/pogoskill-mac_7926.dmg">
        <svg class="me-2" width="24" height="24">
          <use xlink:href="#mac-path"></use>
        </svg>
        免費試用
      </a>
      <div class="secure-download">
        <img src="https://images.pogoskill.com/v2/article/protect.svg" alt="安全下載">
        <span>安全下載</span>
      </div>
    </div>
  </div>
</div>
```

- 指南步骤前后不再重复 CTA。
- FAQ 默认不放 CTA。
- Buy Box 内按钮不是正文 CTA，不计入“一次”的数量。
- 不改按钮 class、下载 PID、层级或文案。
- 两个 `.secure-btn` 和两个 `.secure-download` 必须全部保留；只有按钮、没有安全下载框的 CTA 判定为失败。

## 10. PoGoskill 操作步骤

```html
<h3 class="h3-triangle">PoGoskill 操作步驟</h3>

<ul class="step-cont" id="pogoskill-guide-step">
  <li>
    <p><span>步驟 1</span><label><strong>連接手機：</strong>開啟 PoGoskill 後，把 iPhone 或 Android 連接到電腦。</label></p>
    <!-- 与步骤 1 名称完全匹配的 Guide 图片盒 -->
  </li>
  <li>
    <p><span>步驟 2</span><label><strong>搜尋位置：</strong>第二步的實際操作說明。</label></p>
    <!-- 与步骤 2 名称完全匹配的 Guide 图片盒 -->
  </li>
  <li>
    <p><span>步驟 3</span><label><strong>修改定位：</strong>第三步的實際操作說明。</label></p>
    <!-- 与步骤 3 名称完全匹配的 Guide 图片盒 -->
  </li>
</ul>
```

- 每个 `<li>` 只能对应一个步骤。
- 步骤文字与 DOCX 指定的 Guide 图片必须一一对应。
- “PoGoskill 操作步驟”模块标题必须是 H3；但每个单独步骤不能再写成 H3，`step-cont` 已负责步骤内部的视觉层级。
- 每个 `<li>` 的第一个元素必须是一个无 class 的 `<p>`。其直接子元素固定为两个：先放 `<span>步驟 N</span>` 徽标，再放一个无 class 的 `<label>`，由 `label` 包住该步骤的全部标题和说明。
- 需要加粗时，只允许在 `label` 开头使用一个 `<strong>短標題：</strong>`，其后直接接普通文字。禁止把 `strong`、正文文字或其他标签直接放在 `p` 下，也禁止在 `label` 内加入第二个 `span`、`br`、链接或其他布局元素。
- `.step-cont p` 在站点中采用横向 flex；固定的 `span + label` 只形成“步骤徽标 + 完整内容”两列。若写成 `span + strong + 文字`，则会形成三列，使短标题逐字换行和正文挤压。
- Guide 图片盒是 `<p>` 后面的同级元素，仍位于同一 `<li>` 内；禁止把 `<div class="img-wrap">` 或 `<picture>` 放进步骤文字 `<p>`。

禁止以下会挤压的结构：

```html
<li>
  <p><span>步驟 1</span><strong>連接手機：</strong>開啟 PoGoskill 後連接裝置。</p>
</li>
```

必须改为：

```html
<li>
  <p><span>步驟 1</span><label><strong>連接手機：</strong>開啟 PoGoskill 後連接裝置。</label></p>
  <div class="img-wrap text-center">
    <!-- 對應步驟 1 的 picture -->
  </div>
</li>
```

## 11. FAQ

```html
<section id="part6">
  <h2>六、主題常見問題</h2>

  <h3 class="h3-faq faq1">1. 第一個問題？</h3>
  <p>第一個答案。</p>

  <h3 class="h3-faq faq1">2. 第二個問題？</h3>
  <p>第二個答案。</p>
</section>
```

- FAQ 问题不能用普通裸 H3 或 `h3-triangle`。
- 每个问题后必须紧跟答案段落。
- FAQ 不是 PoGoskill 推广区，不自动插入 CTA。

## 12. 视频

只有 DOCX 明确需要视频，且同类已上线文章存在对应模块时才使用：

```html
<div class="video-cont">
  <iframe class="lozad w-100"
          src="https://images.pogoskill.com/loading.svg"
          data-src="YOUTUBE_EMBED_URL"
          title="描述影片內容的標題"
          frameborder="0"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen></iframe>
</div>
```

禁止直接贴普通 `<iframe>` 或自己新增响应式 CSS。

## 13. 结语与 Buy Box

```html
<section id="partN">
  <h2>結語</h2>
  <p>总结全文；最后一次提到 <a href="https://tw.pogoskill.com/">PoGoskill</a> 时链接官网。</p>
</section>
```

结语之后原样复制 `assets/buybox.html`，不得删减、重排或重写。整篇必须恰好一个 `class="pro-content pro-board1"`。

## 14. 面包屑、相关文章、作者与侧边栏

这些不属于正文 `content`，不要在 HTML 中手写：

- 面包屑与 `.content-navlinks`：由 V2 模板根据分类和页面字段渲染。
- 相关文章：写入 CMS `related_id`。
- 作者：写入 `author_id` 和模板 `author_cont` 字段。
- 分类：写入 `classify_id` 与 `classify_page_id`。
- 产品：写入 CMS 产品主键 `6333`、`6332`。
- 侧边栏：写入正确的 `sidebar_module_id`。

正文中禁止复制 `.content-navlinks`、相关文章卡片、作者卡片或侧边栏 HTML，否则容易重复、挤压和遮挡。

## 15. Luna 禁止输出

以下任一项出现即视为 HTML 不合格，禁止上传 CMS：

```text
<h1>
<nav class="article-toc">
没有 class 的 <h3>
正文中的裸 <ul>
不在 table-box 中的 <table>
<style> 或自定义 CSS
自创 xxx-card、xxx-box、xxx-note、xxx-article class
手写面包屑、相关文章、作者或侧边栏
重复正文 CTA
缺少 WebP/fallback 任一格式的图片盒
目录 href 与 section id 不一致
未闭合或不平衡的 div/section/table
```

## 16. 上传前机械校验

Luna 必须输出校验结果后才能调用 `/cms/page/add` 或 `/cms/page/update`：

1. H1 数量为 0。
2. `<section>` 数量等于 H2 数量。
3. TOC href 与 section ID 一一对应。
4. 非 FAQ 的 H3 全部为 `class="h3-triangle"`。
5. FAQ H3 全部为 `class="h3-faq faq1"`。
6. 不存在 `article-toc`、`<style>`、自创 class 或裸列表。
7. 所有表格位于 `table-box overflow-auto`。
8. 所有完成图片盒含同 basename 的 fallback 与 WebP。
9. 主图为 850×460；竖图使用高度限制。
10. `.tit-tips` 恰好用于两个经过语义判断的目录项。
11. 正文 `.btn-groups` 恰好一组。
12. PoGoskill 模块的完整介绍、适用情境、操作思路、作用与优势都位于 CTA 之前；CTA 之后紧接 `h3.h3-triangle` 的“PoGoskill 操作步驟”，再紧接 `ul.step-cont`。不得出现“介绍一段 → CTA → 继续介绍／优势”的错误顺序。
13. Buy Box 恰好一个且与资产完全一致。
14. `IMAGE_PENDING` 为 0 才能判定图片完成。
15. 所有标签平衡，HTML 按逻辑块换行缩进。
16. 每个 `step-cont > li` 必须以固定的 `p > span + label` 开头；`label` 可用一个开头 `strong` 加粗短标题，并包含其余普通正文。图片盒只能作为该 `<p>` 后面的同级元素。
17. 上传前必须运行 `scripts/validate-article-html.py`，返回码必须为 0；不得用人工口头检查代替。
18. DOCX 的所有正文段落、表格、FAQ、结语和图片占位都必须进入 HTML。写入后用 `compare-docx-to-cms-page.py` 列出缺失区块；存在未解释缺失时不得报告完成。

任何一项失败：停止上传，回到 HTML 修正；不得依赖 CMS 或浏览器自动修复结构。
  
