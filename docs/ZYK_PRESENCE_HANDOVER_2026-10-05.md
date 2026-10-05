# ZYK presence and automation handover — 5 October 2026

## Outcome

The website/channel-register release is deployed. Social profile copy and introductory posts are prepared, not published. No dedicated ZYK social account was created, renamed or verified in this pass. No post was submitted and no social publishing scheduler was installed.

Public identity: ZYK / ZhiAn YunKe / 智安云科. Website: https://zykai.net. Contact: hello@zykai.net.

Oxbridge College, William Morris Productions and earlier William Morris identities remain founder history, not ZYK destinations. They were not renamed, merged, deleted or used for ZYK posting. Founder experience is not ZYK corporate age, registration, ownership of earlier organisations or evidence of current affiliation. Existing China-focused development-stage language is preserved. NASJX, 0604.ai and local infrastructure were not changed.

## Released website

PR: https://github.com/editormorris-svg/zykai-net/pull/4
Release commit: `013ff802f545f46965120b70d1812fde32f1a60c`.

The build preserves authored public-site pages/styles/scripts and adds:

- https://zykai.net/en/channels.html
- https://zykai.net/zh-cn/channels.html
- https://zykai.net/zh-hk/channels.html
- https://zykai.net/channels.json

The channel pages show the website and public email, state that dedicated social channels are being established, and explicitly distinguish founder history from official ZYK accounts. Existing localised pages gain footer contact/channel links, canonical/Open Graph/language-alternate metadata and Brand structured data. The sitemap is regenerated. No unverified profile is added to sameAs. The public register exposes only brand identity and verified public profile links; its current profile list is empty.

Operational configuration and drafts are excluded from the deployed Pages artifact, although this GitHub repository itself is public. Never store passwords, API keys, cookies or private session material here.

## Prepared assets

`brand/presence.json`: canonical identity, proposed handles, target platforms, ownership-verification fields and historical-identity boundary. Preferred handle candidate: `zykai`; fallback: `zhianyunke`. Neither is verified available or reserved.

`brand/social-launch.json`: eight English/Simplified Chinese drafts covering introduction, education-first founder history, bounded pilots, school knowledge, teacher capability, human accountability, durable institutional foundations and contact. The suggested days 1, 4, 8, 11, 15, 18, 22 and 25 are relative planning offsets, not actual scheduled posts.

`brand/platform-copy.md`: draft biographies and opening copy for Facebook, LinkedIn, Instagram, Threads, X, TikTok and YouTube, plus the first-video voiceover and production brief. A script is not a completed video; suitable media has not been supplied for Instagram/video publishing.

`brand/README.md`: identity, content and account-verification procedures.

## Account audit and login boundary

Windsor returned Facebook: Oxbridge College; LinkedIn: William Morris Productions; TikTok: William Morris; and the existing email-linked YouTube connection. None is promoted to a dedicated ZYK destination. A listed connector does not itself prove current publishing permissions or ownership of a new ZYK account.

The stored ZYK browser profile listed no signed-in sites at inspection. Its name is not authentication evidence. Persistent Facebook/LinkedIn login remains unresolved. No new capture or password request was initiated.

The previous 26 September verification message to hello@zykai.net was found in the connected inbox. This confirms earlier inbound delivery, not a new outbound send-as/SMTP test.

## Verified implementation and automation

`scripts/build_presence.py` uses only the Python standard library. Its registry validation rejects known historical account IDs, missing ZYK ownership/evidence, lookalike platform domains, duplicate posts and attempts to enable publishing in this preparation-only release. `publishing_enabled` remains false.

Production run https://github.com/editormorris-svg/zykai-net/actions/runs/37286443411 completed successfully, including build and GitHub Pages deployment.

Automatic post-deployment run https://github.com/editormorris-svg/zykai-net/actions/runs/37286485159 completed successfully. Job `111686496745` reported:

- Nine safeguard tests passed.
- 59 HTML pages built and local links checked.
- Eight social drafts; zero verified social destinations; publishing disabled.
- LIVE PASS for all three channel pages and channels.json.

`.github/workflows/presence-check.yml` runs read-only validation for relevant pull requests, after successful main-site deployments and daily at 02:23 UTC / 09:23 Asia/Bangkok. GitHub scheduling is best effort. Notification delivery was not verified. This is website validation, not autonomous social posting or assistant work between conversations.

## Browser acceptance and limitations

Browser run `7f92b1b3-360e-49b6-986d-427c1a2dd265` completed. The browser agent reported eight passed checks: page rendering, ZYK identification, displayed website, mailto contact, honest pending-social status, historical separation, all three language links, and English About navigation with return to Channels. No console/resource errors were observed by that agent.

A 390px mobile viewport and mobile-menu operation were not directly verified because the session's tools did not support that viewport operation. Desktop rendering is not proof of mobile correctness. A desktop screenshot was reported captured, but no reusable screenshot reference was returned; no independent screenshot review is claimed.

## Next practical action

Resolve one legitimate persistent platform administrator session, then create a dedicated ZYK company Page/profile/channel through the platform's supported flow. Retain the authentic personal administrator identity where required; do not rename it or a historical organisation into ZYK.

Confirm the exact stable destination ID, public URL and ZYK ownership. Record platform, account_id, url, brand, ownership_confirmed, verified_at and a non-sensitive verification note in the register. Connect that specific new destination to Windsor where supported and verify permissions. Review/adapt prepared copy and supply appropriate media before installing and testing a separate publisher with duplicate prevention and publication receipts. Never fall back to a historical account.

Do not invent company registrations, certifications, customers, school endorsements, addresses, affiliations, deployment results or product availability. Do not expose student data or use identifiable school material without appropriate permission.

Resume from this handover and current main. Do not rebuild already completed work or repeat failed login captures without a new reason. Keep account setup, website validation, draft preparation and actual publishing as distinct states.
