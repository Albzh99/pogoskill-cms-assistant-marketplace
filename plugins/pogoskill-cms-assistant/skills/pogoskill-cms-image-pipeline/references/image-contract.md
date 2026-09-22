# PoGoskill V2 图片约定

核验日期：2026-09-20。实时 API 响应优先于本文。

## CMS 对象与接口

- 台湾站：`site_id = 324`，`img_root = pogoskilltw_images`
- 目录：`POST /cms/picture/dirs`
- 文件列表：`POST /cms/picture/list` 已上线且当前 API Key 已获授权；可返回 `uri`、MIME、size、w、h、upload 与 online
- 上传：`POST /cms/picture/upload`，`multipart/form-data`
- 单文件上限 30 MB；单次最多 100 个；支持 jpg/jpeg/png/webp
- 文件名只允许小写 ASCII `[a-z0-9-_.]`，长度 4–255
- 上传成功返回 `publish_id`、文件名、MIME、size、w、h、url 与 upload；上传后不调用发布接口

## 素材与命名

- PoGoskill 下载、安装、操作步骤和产品界面图必须先用 `/cms/picture/list` 搜索 `guides`。搜索维度包括平台、Guide、PoGoskill、步骤动作和界面功能；文件名不同不代表图片不同，必须打开候选 URL 核对画面。
- 用户为 Pokémon GO 或 Pikmin Bloom 正文配好的图片优先上传为新素材，不用 CMS 中主题相似的图片替换；上传前仍检查同名冲突与完全相同文件。
- DOCX 只提取 `word/document.xml` 中 `a:blip r:embed` 实际引用的媒体。
- JPG/PNG 原字节保留为 fallback；`.jpeg` 文件名规范为 `.jpg`，PNG 不改成 JPG。
- basename 必须是简洁、英文、小写、连字符分隔且描述图片真实内容的语义名称，例如 `coral-decor-pikmin-guide` 或 `pogoskill-pikmin-location-step-1`。禁止 `image1`、`123`、`test`、`screenshot1` 或无意义随机串；源文件 SHA-256 保留在 manifest，不强制写入公开文件名。
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
- 上传后验证：`code=0`、`data.total=2`、`err_name_files=[]`、返回名称/尺寸/目录匹配，并对两个 `upload` URL 做可读性检查。
- 上传后必须再用 `/picture/list` 回查 `uri/w/h/upload/online`；两种格式都存在且尺寸一致后才能交给文章回填。

## V2 HTML

CMS 新上传资源的已发布范例使用：

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
         alt="自然、准确的繁体中文 ALT"
         style="max-width:850px;width:100%;height:auto;">
  </picture>
</div>
```

- `<source>` 必须在 `<img>` 前；ALT 只放在 fallback `<img>`。
- 新上传资源在 CMS 草稿预览中，`src/srcset` 与 `data-src/data-srcset` 都使用上传响应返回的 `upload` URL。
- `max-width` 不超过原图宽度；主图固定 850×460，步骤图与竖图按实际可读性缩小，窄素材按真实宽度。竖图不得占满一个长屏。
- ALT 必须描述图片实际画面，以自然繁体中文表达，可包含适当关键词；不得直接复制 H1，也不得让多张图使用相同 ALT。
- 不改用 `loading="lazy"`，保留站点的 `lozad img-fluid` 机制。

## Manifest 必填项

每项至少包含：`image_key`、`source_entry`、`source_sha256`、`fallback_path`、`webp_path`、`width`、`height`、`alt`、`max_width`。上传后追加 `upload_request_id`、`publish_id`、`fallback_upload_url`、`webp_upload_url` 和 URL 检查结果。
