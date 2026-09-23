# PoGoskill V2 图片约定

核验日期：2026-09-20。实时 API 响应优先于本文。

## CMS 对象与接口

- 台湾站：`site_id = 324`，`img_root = pogoskilltw_images`
- 目录：`POST /cms/picture/dirs`
- 文件列表：`POST /cms/picture/list` 已上线且当前 API Key 已获授权；可返回 `uri`、MIME、size、w、h、upload 与 online
- 上传：`POST /cms/picture/upload`，`multipart/form-data`
- 单文件上限 30 MB；单次最多 100 个；支持 jpg/jpeg/png/webp
- 文件名只允许小写 ASCII `[a-z0-9-_.]`，长度 4–255
- 上传成功返回 `publish_id`、文件名、MIME、size、w、h、url 与 upload；必须用该图片上传记录的 `publish_id` 调用 `/cms/pagepublish/publish`，将图片同步到云端

## 素材与命名

- PoGoskill 下载、安装、操作步骤和产品界面图必须先用 `/cms/picture/list` 搜索 `guides`。搜索维度包括平台、Guide、PoGoskill、步骤动作和界面功能；文件名不同不代表图片不同，必须打开候选 URL 核对画面。
- 用户为 Pokémon GO 或 Pikmin Bloom 正文配好的图片优先上传为新素材，不用 CMS 中主题相似的图片替换；上传前仍检查同名冲突与完全相同文件。
- DOCX 只提取 `word/document.xml` 中 `a:blip r:embed` 实际引用的媒体。
- JPG/PNG 原字节保留为 fallback；`.jpeg` 文件名规范为 `.jpg`，PNG 不改成 JPG。
- basename 必须是简洁、英文、小写、连字符分隔且描述图片真实内容的语义名称，例如 `coral-decor-pikmin-guide` 或 `pogoskill-pikmin-location-step-1`。禁止 `image1`、`123`、`test`、`screenshot1`、无意义随机串或结尾 SHA/哈希；源文件 SHA-256 只保留在 manifest，绝不写入公开文件名。
- fallback 与 WebP 必须同目录、同 basename。若语义名称已存在，先判断是否可直接复用；不可复用时使用有意义的主题、年份或步骤后缀，不得覆盖。
- 目标目录必须由 `/cms/picture/dirs` 确认存在，不从文章 URL 猜测，也不自动新建。

## 目录与语义匹配

- Pokémon GO 游戏内容图：`pokemon-ios`
- Pikmin Bloom 游戏内容图：`pikmin`
- PoGoskill 下载、安装、操作步骤、产品界面和 Guide 截图：`guides`
- 目录按图片内容决定，不只按文章主题决定。游戏文章中的 PoGoskill 操作截图仍使用 `guides`。
- 下载步骤图必须逐项核对界面功能：连接设备、搜索位置/坐标、开始修改定位等动作不能错配或随机插入。
- 每张图必须能解释其所在段落；正文讲 A、图片展示 B 时不得回填。

## 转换与验证

- JPG：`cwebp -q 90 -m 6 -metadata none`
- PNG：`cwebp -lossless -z 9 -metadata none`
- 文章主图必须在成对转换前准备为 850×460，且不得拉伸变形；无合适素材时停止并报告。正文图保持原始比例，横图按正文展示需求控制，手机截图等竖图限制 `max_width` 和最终展示高度。
- WebP 转换本身不 resize、不 crop；fallback 与 WebP 像素宽高必须完全一致。
- 上传前验证：可解码、非零、≤30 MB、扩展名与 MIME 合理、SHA-256 已记录。
- 上传后验证：`code=0`、`data.total=2`、`err_name_files=[]`、返回名称/尺寸/目录匹配，并对两个后台 `upload` URL 做可读性检查。
- 上传后必须再用 `/picture/list` 回查 `uri/w/h/upload/online`；两种格式都存在且尺寸一致后才能交给文章回填。
- 若 `/picture/list` 已确认同名、同尺寸 fallback/WebP 对存在，应直接复用；禁止为了取得不同 URL 再次上传同一图片。
- 图片未发布时，前台 `url/online` 返回 HTTP 404 是正常的待发布状态，不触发重复上传；应继续使用原上传响应中的图片 `publish_id` 发布资源。图片发布并确认前台可读后，才把 URL 回填到草稿。

## 前台公开 URL

- CMS 响应的 `upload` URL（例如 `https://site.p.cms.afirstsoft.cn/...?...attachment=1`）只用于上传验证，不是文章地址，严禁写入 `src`、`srcset`、`data-src` 或 `data-srcset`。
- `/cms/picture/upload` 成功响应中的 `data.list[].url` 是前台正式地址，必须优先直接采用；`/cms/picture/list` 的 `online` 是缺失时的核对兜底。不得忽略已有 `url` 字段后声称前台地址无法取得。
- 繁中站 `site_id = 324`：`https://tw.pogoskill.com/images/<folder>/<semantic-name>.<ext>?w=<width>&h=<height>`。
- 英文站 `site_id = 286`：`https://images.pogoskill.com/<folder>/<semantic-name>.<ext>?w=<width>&h=<height>`。
- 只在 API 返回的公开 URL 尚无尺寸参数时追加 `w` 与 `h`；不得自行替换 API 返回的 host、目录或文件名。
- 图片上传存在与图片已上云是两个状态：`picture/list` 确认双格式存在后，仍须完成图片资源发布。前台 fallback/WebP 均返回 200/206 后，才能判定 `image_published` 并回填文章。

## 图片资源发布

- 唯一允许传给 `/cms/pagepublish/publish` 的 ID，是当前图片 `/cms/picture/upload` 响应中的 `data.publish_id`。必须同时保留该上传 `request_id` 作为来源证据。
- 请求使用 `{ "ids": [图片发布记录ID], "description": "...image resources..." }`。成功必须同时满足 `code === 0`、`data.failed = []`，且 `data.success[].id` 完整覆盖请求 IDs。
- 图片发布与文章发布必须严格区分：禁止传入页面 ID；禁止传入 `/cms/page/make` 产生的文章发布 ID；仍禁止调用 `/cms/page/make`。
- 发布接口成功后可能异步同步 OSS/S3。最多轮询前台 URL 约 30 秒；尚未可读时保留 `image_publish_submitted` 和发布 `request_id`，之后只重试 URL 验证，不重复发布同一 ID。
- 已存在且前台可读的图片对直接标记 `image_published`，不重复上传、不重复发布。已存在但 404 的图片对必须从原始 manifest/上传响应恢复 `publish_id`；`picture/list` 本身不能证明发布 ID，禁止拿图片名、页面 ID 或猜测数字代替。
- fallback 与 WebP 使用同目录、同 basename、同尺寸参数，仅扩展名不同。查询参数写入 HTML 时必须编码为 `&amp;`。

## V2 HTML

CMS 新上传资源的已发布范例使用：

```html
<div class="img-wrap text-center">
  <picture>
    <source class="lozad img-fluid"
            srcset="PUBLIC_LOADING_SVG"
            data-srcset="PUBLIC_WEBP_URL"
            type="image/webp">
    <img class="lozad img-fluid"
         src="PUBLIC_LOADING_SVG"
         data-src="PUBLIC_FALLBACK_URL"
         alt="自然、准确的繁体中文 ALT"
         style="max-width:850px;width:100%;height:auto;">
  </picture>
</div>
```

- `<source>` 必须在 `<img>` 前；ALT 只放在 fallback `<img>`。
- `src/srcset` 使用对应站点的公开 `loading.svg`；`data-src/data-srcset` 使用上述前台公开图片 URL。后台 `upload` URL 只能留在 manifest 作证据。
- `max-width` 不超过原图宽度；主图固定 850×460，步骤图与竖图按实际可读性缩小，窄素材按真实宽度。竖图不得占满一个长屏。
- ALT 必须描述图片实际画面，以自然繁体中文表达，可包含适当关键词；不得直接复制 H1，也不得让多张图使用相同 ALT。
- 不改用 `loading="lazy"`，保留站点的 `lozad img-fluid` 机制。

## Manifest 必填项

每项至少包含：`image_key`、`source_entry`、`source_sha256`、`fallback_path`、`webp_path`、`width`、`height`、`alt`、`max_width`。新上传项追加 `site_id`、`upload_request_id`、图片 `publish_id`；复用现有项记录 `site_id`、`list_request_id`。两种情况都保存后台验证 URL、前台 URL 与检查结果。图片发布后追加 `image_publish_request_id`、`image_publish_submitted_at`、`image_public_verified_at`，最终状态必须为 `image_published` 才能回填 HTML。
