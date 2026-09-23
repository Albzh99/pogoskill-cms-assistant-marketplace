# English CMS live contract

Verified through production POST APIs on 2026-09-23. Re-query before each write because IDs and availability can change.

## Confirmed English site

- Site: `pogoskill`
- `site_id`: `286`
- Public URL: `https://www.pogoskill.com`
- Static root: `pogoskill`
- Image root: `pogoskill_images`
- Site status: enabled
- Article V2 template observed on current pages: `template_id = 9831`, `文章内容页面模板-v2-rnui-202408`
- Current article examples use `product_id = [4987, 4988]`; re-query and confirm these products before writing.
- Current example sidebar is `sidebar_module_id = 9445`; re-query it rather than assuming it is universal.
- Authors vary between pages; never copy an author ID from an example without a live author lookup.

## Confirmed access evidence

- `/cms/site/list`: `code = 0`, request `3edf7a03-da20-4bab-ba7d-67ca213a7838`
- `/cms/page/list` for site 286: `code = 0`, 856 pages, request `5be60556-5ba3-4ff9-8a0f-cab67a726286`
- `/cms/template/list` for site 286: `code = 0`, request `07d43a4d-4cf4-45e8-a781-f7d16b61a3b9`
- `/cms/picture/dirs` for site 286: `code = 0`, 33 root directories, request `83ec2465-7b08-4c87-bd76-2d18f07c6750`

These values prove access at the verification time; they do not replace live checks. Do not claim the English CMS is inaccessible without following the shared three-attempt evidence contract.

## Site separation

English and Traditional Chinese are different CMS sites:

| Concern | English | Traditional Chinese |
| --- | --- | --- |
| Site name | `pogoskill` | `pogoskilltw` |
| Site ID | `286` | `324` |
| Domain | `www.pogoskill.com` | `tw.pogoskill.com` |
| Image root | `pogoskill_images` | `pogoskilltw_images` |
| V2 template observed | `9831` | `9916` |
| Download IDs | `7144` / `7145` | `7925` / `7926` |

Never transfer IDs, URLs, content language or assets across these site profiles.

