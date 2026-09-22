# PoGoskill 页面验收约定

## 独立性

审查 Agent 默认只有读取与预览权限。不要静默修复发布 Agent 的输出；把问题返回给发布 Agent 修改后重新审查。只有用户明确要求审查 Agent 直接修复时才可写入 CMS。

## CMS 本地预览

CMS 已确认提供本地预览选项。优先使用该选项查看当前草稿的真实模板、CSS、模块和响应式效果。

预览前记录 `/cms/page/info` 的页面 ID、version、update_time 和正文摘要；预览后再次核对版本，避免审查期间页面被其他人更新。

如果本地预览需要 UI 登录、一次性授权或人工操作，清楚说明所需步骤。不要为获得预览而擅自执行正式发布。

## 自动与人工视觉信号

在浏览器能力允许时，结合截图与 DOM 数据检查：

- `document.documentElement.scrollWidth > clientWidth` 的横向溢出
- 可见文本元素与 fixed/sticky 浮层的矩形重叠
- `display:none`、`visibility:hidden`、`opacity:0` 或零尺寸的关键内容
- 图片 `complete` 但 `naturalWidth === 0`
- iframe、表格和 Buy Box 超出正文容器
- 锚点目标不存在、CTA href 为空或仍为 `#`

自动信号不能代替截图观察；桌面和手机都要查看。

## 图片验收

- 有真实素材时，按 `$pogoskill-cms-image-pipeline` 的 manifest 核对 fallback JPG/PNG 与同名 WebP、尺寸、URL、ALT、upload request_id 和待发布 publish_id。
- CMS `/picture/list` 已上线且当前 API Key 已获授权。图片验收必须同时包含上传响应、列表回查、URL 可读性和真实草稿预览。
- 对 `guides` 图片核对上传前图库检索与画面匹配证据；已有合适 Guide 图片却重复上传，判定为 `FAIL`。对用户提供的游戏正文图片，确认其被优先使用且仅做同名/完全重复检查，不得被图库相似图擅自替换。
- 主图必须为 850×460。横图应适合正文宽度；竖图保持比例且显示高度合理，不得占满长屏。
- 核对目录：Pokémon GO 游戏图为 `pokemon-ios`，Pikmin Bloom 游戏图为 `pikmin`，PoGoskill 下载/安装/操作/产品界面为 `guides`。
- 核对文件名是简洁英文小写语义 slug，URL 与图片内容相关；拒绝顺序号、测试名、通用截图名或无意义随机串。
- 逐张比较正文上下文、图片真实画面和繁体 ALT；步骤 1/2/3 必须分别对应其实际界面功能，不能只因属于 PoGoskill 就插入。
- `IMAGE_PENDING` 必须保留在未有真实素材的位置，审查结果只能是 `PASS WITH IMAGE HOLD` 或 `FAIL`；图片全部补齐并通过桌面/手机预览后才可 `PASS`。
- 图片上传的 `publish_id` 不得传给发布接口，除非用户日后另行明确要求发布。

## 交付格式

简短列出页面与版本、元数据、HTML、桌面/手机预览、图片状态、截图证据、阻断问题和最终判定。

## 发布前强制清单

只有以下项目全部通过才可给出 `PASS`：无额外自定义框体；未改变模板、CSS 或模块结构；主图 850×460；新图有 fallback 与同名 WebP；文件名和 URL 语义正确；三个目录选择正确；Guide 已先查库并优先复用；用户提供的游戏正文图被优先上传；步骤图逐项匹配；图片与正文一致；竖图尺寸合理；ALT 准确且不重复；无同名冲突或完全重复上传；无 `IMAGE_PENDING`；桌面与手机真实预览无挤压、遮挡或溢出。
