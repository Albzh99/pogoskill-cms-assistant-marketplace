# PoGoskill 页面验收约定

## 交稿输入验收

- DOCX 必须给出参考文章 URL、CMS 页面 ID 或现有 HTML中的至少一项，并能指出 Publisher 实际采用了哪一个参考来源。
- 需新上传的普通正文图必须嵌入 DOCX 的实际出现位置；核对 CMS 图片盒与其前后正文一致。
- Guide 图必须在对应段落或步骤标注 CMS `guides` 的准确文件名（含扩展名）。核对实际使用的 fallback/WebP 与该名称一致；发现语义猜图、相似图替换或重新上传 Guide 图时判定为 `FAIL`。

## 独立性

审查 Agent 默认只有读取权限。不要静默修复发布 Agent 的输出；把问题返回给发布 Agent 修改后重新审查。只有用户明确要求审查 Agent 直接修复时才可写入 CMS。

## 页面预览暂停

当前不执行 AI CMS 本地预览、浏览器截图或桌面／手机 DOM 视觉检测。审查不得为预览而要求登录 CMS，也不得把未做视觉预览视为失败。仍须通过 `/cms/page/info` 回读当前页面版本，并运行确定性的 HTML 与完整度检查。

## 图片验收

- 有真实素材时，按 `$pogoskill-cms-image-pipeline` 的 manifest 核对 fallback JPG/PNG 与同名 WebP、尺寸、URL、ALT、图片上传 request_id、图片 publish_id 和图片发布 request_id。
- CMS `/picture/list` 已上线且当前 API Key 已获授权。图片验收必须包含上传响应、列表回查、图片资源发布响应和前台 URL 检查。后台 `upload` URL 只用于验证上传；前台 `url/online` 在发布前返回 404 只是中间状态，不能作为完成证据。
- 对 `guides` 图片核对上传前图库检索与画面匹配证据；已有合适 Guide 图片却重复上传，判定为 `FAIL`。对用户提供的游戏正文图片，确认其被优先使用且仅做同名/完全重复检查，不得被图库相似图擅自替换。
- 主图必须为 850×460。横图应适合正文宽度；竖图保持比例且显示高度合理，不得占满长屏。
- 手机截图和其他竖图必须使用 `max-height` 限制，并保持 `width:auto;height:auto`。英文手机截图不得使用固定像素 `max-width` 作为主要展示限制。
- 核对目录：Pokémon GO 游戏图为 `pokemon-ios`，Pikmin Bloom 游戏图为 `pikmin`，PoGoskill 下载/安装/操作/产品界面为 `guides`。
- 核对文件名是简洁英文小写语义 slug，URL 与图片内容相关；拒绝顺序号、测试名、通用截图名或无意义随机串。
- 繁中正文的图片 URL 必须来自 `https://tw.pogoskill.com/images/`；CMS 后台域名、`attachment=1` 和结尾 SHA/随机哈希一律判定为 `FAIL`。`upload` URL 只允许存在于 manifest 证据中。
- 逐张比较正文上下文、图片真实画面和繁体 ALT；步骤 1/2/3 必须分别对应其实际界面功能，不能只因属于 PoGoskill 就插入。
- `IMAGE_PENDING` 必须保留在未有真实素材的位置，审查结果只能是 `PASS WITH IMAGE HOLD` 或 `FAIL`；图片全部补齐并通过 API 与机械检查后才可 `PASS`。
- 图片上传响应的 `publish_id` 必须传给 `/cms/pagepublish/publish`，且只用于发布图片资源。必须验证 `code === 0`、`data.failed = []`、`data.success[].id` 覆盖全部请求 ID，并确认前台双格式可读。页面 ID 或文章生成所得 ID 绝不能用于此步骤。

## 交付格式

简短列出页面与版本、元数据、HTML、图片状态、来源覆盖、阻断问题和最终判定。注明“AI 页面预览当前停用”，但不要把它列为阻断项。

## 结语首页链接

- 最后一个结语 section 必须链接正确站点首页。
- 锚文本必须是 DOCX 实际提供的自然关键词短语，而不是 `PoGoskill`；繁中通常为“最佳／最好……”工具词，英文通常为 `best ...` 工具词。
- `PoGoskill` 必须位于链接后并保持普通文字。缺少源文关键词、链接站点错误或 `<a>PoGoskill</a>` 均判定为 `FAIL`。

## 下载区位置与居中

- 主介绍模块使用对应站点的固定下载资产；繁中与英文 CTA 结构、下载 ID 和链接不得混用。
- 桌面 `.btn-groups` 必须保留 `display:flex;justify-content:center;`，无论前方使用哪一种已验证 H3/H4 标题样式，两个按钮都应整体居中。
- 英文主模块保留现有顺序：已验证的 `How to ... PoGoskill` 标题 → 英文 CTA → `step-cont` 步骤。标题可沿用参考文章的 `h3-triangle`、其他英文站已批准 H3，或 `h4-filled`；不得强制全部改成 H4，也不得为了按钮居中改写标题层级。繁中模块按繁中契约执行。
- FAQ 默认无 CTA。只有 DOCX 对应答案明确介绍或推荐 PoGoskill 时，才允许在答案后额外加入一组相同语言 CTA；没有源文依据、放错站点资产或全文超过两组均判定为 `FAIL`。

## 发布前强制清单

只有以下项目全部通过才可给出 `PASS`：无额外自定义框体；未改变模板、CSS 或模块结构；主图 850×460；新图有 fallback 与同名 WebP；文件名和 URL 语义正确；三个目录选择正确；Guide 已先查库并优先复用；用户提供的游戏正文图被优先上传；步骤图逐项匹配；图片与正文一致；竖图尺寸合理；ALT 准确且不重复；无同名冲突或完全重复上传；无 `IMAGE_PENDING`；HTML 与来源完整度机械校验通过。
