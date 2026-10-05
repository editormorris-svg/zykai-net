# ZYK public presence and launch operations

## Identity

Public name: **ZYK / ZhiAn YunKe / 智安云科**. Website: https://zykai.net. Contact: hello@zykai.net.
Positioning: institutional AI for education, with the existing China-focused design and development-stage language preserved.

Suggested profile display name: **ZYK | ZhiAn YunKe**.
Suggested handle: **zykai**; fallback **zhianyunke**. Neither is verified available or reserved.
Short biography: *Institutional AI for education. Connecting school knowledge, useful AI tools, governance and teacher capability. zykai.net*
Long biography: *ZhiAn YunKe (ZYK) is developing an education-first approach to institutional AI, connecting infrastructure, school knowledge, assessment, governance and teacher capability. It draws on its founder’s more than three decades in education across teaching, leadership, curriculum and international settings. Explore the developing approach and discuss practical needs at zykai.net or hello@zykai.net.*

## Separate history from destinations

Oxbridge College, William Morris Productions, earlier William Morris profiles and the existing personal/0604 YouTube identity remain historical material. Do not rename, merge, delete or publish ZYK content through them. Historical references do not establish ownership, current affiliation, endorsement or company age. The founder’s experience is not ZYK’s corporate trading history.

## Source of truth

`presence.json` contains the brand identity and verified ZYK destination allow-list. It intentionally starts empty. Browser authentication and Windsor connection are different checks; neither alone proves ZYK ownership. Never put passwords, API keys, cookies, recovery codes or private operational addresses in this repository.

Before adding a profile: establish a **new dedicated ZYK account/page**, confirm its exact stable platform ID and public URL, verify ZYK ownership, and record `platform`, `account_id`, `url`, `brand: "ZYK"`, `ownership_confirmed: true`, `verified_at` and a non-sensitive `verification_note`. The account ID is the platform destination ID, not a general Windsor connection ID. Reconnect that specific account to Windsor where supported; test permissions before considering any publisher. Historical IDs remain blocked.

## Prepared, not published

`social-launch.json` contains eight bilingual drafts for a proposed four-week introduction, with relative launch-day suggestions, not calendar appointments. There is **no automatic social publisher**, no reserved username, and no post scheduled by this repository. `publishing_enabled` must remain false until a separately reviewed publisher and verified destinations exist. Creating a profile does not automatically approve the draft queue. YouTube/TikTok require an actual approved video; Instagram requires suitable approved media rather than a text-only submission.

No invented customer counts, certifications, registrations, partnerships, addresses, case studies or product availability. Do not use student information or school deployment details as marketing evidence without appropriate permission.

## Website build and verification

Run `python3 -m unittest discover -s scripts -p 'test_*.py'`, then `python3 scripts/build_presence.py`. The script copies `public-site` to `site`, preserving authored pages, CSS and JavaScript. It adds EN/Simplified/Traditional official-channel pages, footer contact links, canonical/Open Graph/language metadata, Brand structured data, a public `channels.json`, and an updated sitemap. Operational configuration and drafts are not copied into the Pages artifact; this repository itself may be public.

`python3 scripts/build_presence.py --check-live` also reads the four live channel endpoints over HTTPS. The deployment workflow runs tests and the build before publishing. The separate daily presence check is read-only and never posts to social platforms. A green workflow is evidence of that run, not a guarantee of future execution or notification delivery.

## Pending manual boundary

Dedicated social account creation remains dependent on an authorised platform session and any platform-required verification. Avoid repeated browser captures and do not request passwords in chat. Continue website/content/validation work independently of that blocker. Once a single platform is genuinely available, finish that platform end to end before expanding.
