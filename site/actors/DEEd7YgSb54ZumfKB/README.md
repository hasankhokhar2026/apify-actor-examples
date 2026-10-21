# TikTok Verified Mention Tracker

See who is talking about a TikTok brand or creator account. Give the tracker one or more handles and it collects public TikTok posts that **tag** the account or type its **@handle** in the caption. Every row says *why* it matched, so a real clickable tag never gets confused with a caption that just happens to contain the name.

Use it for brand monitoring, sponsorship and campaign proof, influencer discovery and competitor watch. No TikTok login, no cookies and no setup are needed.

## What this actor does

- **Real mentions, with the reason.** `mentionType` labels every row `tagged`, `captionText` or `searchResult`. Tagged rows carry the exact tag and its position in the caption, so a clickable tag is never confused with a typed `@handle` or a related post.
- **Proof tied to the account.** Each row carries the tracked account's TikTok ID, display name, verified badge and follower count, so a renamed or look-alike handle can't slip in. The account's own posts are skipped (`isOwnPost`).
- **Controls for real monitoring.** Date windows from 24 hours to 6 months or an exact cut-off, relevance/most-liked/newest order, minimum views, about 50 country views, and a deep multi-search mode (handle, name, display name, #handle, most-liked pass, photo posts) that merges results without duplicates. Give deep runs 2048 MB of memory.
- **Full post and profile detail.** Caption, hashtags, every tagged account, post date, views/likes/comments/shares/saves/reposts, author profile, sound, video or slideshow media, location and ad, paid-partnership and AI labels. Optional permanent video files and related-video discovery.
- **Empty fields are omitted.** Fields TikTok doesn't provide for a post are left out instead of filled with placeholders.

## Output per post

One row per post, per tracked account. Fields TikTok doesn't provide for a post are left out of that row rather than filled with placeholders.

| Field | Meaning |
|---|---|
| `targetUsername` | The tracked account this post was found for |
| `mentionType` | `tagged`, `captionText` or `searchResult` |
| `isMentionConfirmed` | `true` when `mentionType` is `tagged` |
| `mentionEntry` | The matching tag: `username`, `userId`, `secUid`, `displayText`, `start`/`end` position in the caption |
| `captionMentionsHandle` | The caption contains `@handle` as text |
| `isOwnPost` | Published by the tracked account itself |
| `targetUserId`, `targetSecUid`, `targetDisplayName`, `targetVerified`, `targetFollowerCount` | The tracked account's profile |
| `postId`, `postUrl`, `postType` | Post ID, link and `video` or `slideshow` |
| `caption`, `textLanguage`, `hashtags`, `mentions` | Caption text, language, hashtags and every tagged account |
| `createTime`, `createdAt` | Post time (Unix seconds and ISO 8601 UTC) |
| `playCount`, `likeCount`, `commentCount`, `shareCount`, `collectCount`, `repostCount` | Engagement at collection time |
| `author` | Creator: ID, username, display name, bio, verified, private flag, avatar, followers, following, likes, videos |
| `music` | Sound: ID, title, artist, album, original flag, duration, cover, streaming links |
| `video` | Size, duration, quality, format, cover images and TikTok's video links |
| `images` | Slideshow photos in order, with sizes and links |
| `poi` | Location tag, when the creator added one |
| `locationCreated` | Country the post was made in, e.g. `US` (when `addPostCountry` is on) |
| `isPaidPartnership` | TikTok shows the "Paid partnership" label (sponsored creator content) |
| `isAigc`, `aiContentLabel` | TikTok shows an AI label: `creatorLabeled` ("Creator labeled as AI-generated") or `aiGeneratedMedia` ("Contains AI-generated media") |
| `isAd`, `adLabelVersion` | Ad markers |
| `downloadedVideoUrl` | Permanent video file link (when `downloadVideos` is on) |
| `rank` | Order in which the post was found for this account |
| `foundVia`, `relatedToPostId` | `search` or `relatedVideos`, and for the latter the post it was related to |
| `searchQuery`, `searchUrl` | The TikTok search that found the post, and a link to repeat it |
| `searchCountry` | Country the search ran from (when `searchCountry` is set) |
| `scrapedAt`, `mediaUrlExpiresAt` | Collection time and when TikTok's media links expire |

### Sample row (shortened)

```json
{
  "targetUsername": "billieeilish",
  "mentionType": "tagged",
  "isMentionConfirmed": true,
  "mentionEntry": {"username": "billieeilish", "userId": "6879693940111901701", "displayText": "@BILLIE EILISH", "start": 144, "end": 158},
  "captionMentionsHandle": false,
  "isOwnPost": false,
  "targetUserId": "6879693940111901701",
  "targetDisplayName": "BILLIE EILISH",
  "targetVerified": true,
  "targetFollowerCount": 74678836,
  "postId": "7673892883543493910",
  "postType": "video",
  "postUrl": "https://www.tiktok.com/@fkedits62/video/7673892883543493910",
  "createdAt": "2026-08-14T14:23:49Z",
  "playCount": 1400000,
  "likeCount": 44400,
  "commentCount": 559,
  "author": {"username": "fkedits62", "followerCount": 26500, "verified": false},
  "searchQuery": "@billieeilish",
  "scrapedAt": "2026-10-19T09:28:51Z"
}
```

A per-account run summary (account found or not, posts checked, rows saved by mention type, and why the search stopped) is saved in the run's key-value store as `TARGET_SUMMARY`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `usernames` | array | – | **Required.** Accounts to track: `nike`, `@nike` or `https://www.tiktok.com/@nike` |
| `mentionFilter` | select | `taggedOrCaption` | `taggedOrCaption` (real mentions), `tagged` (clickable tag only) or `all` (every search result, labelled) |
| `excludeOwnPosts` | boolean | `true` | Skip posts published by the tracked account |
| `datePosted` | select | `anyTime` | `anyTime`, `past24Hours`, `pastWeek`, `pastMonth`, `past3Months`, `past6Months` |
| `postedAfter` | string | – | Exact cut-off: a date such as `2026-10-01` or an age such as `3 days` |
| `sortBy` | select | `relevance` | `relevance`, `mostLiked` or `newest` |
| `minPlayCount` | integer | – | Skip posts with fewer views |
| `searchDepth` | select | `standard` | `standard` (fast) or `deep` (more mentions, slower; use 2048 MB memory) |
| `searchCountry` | select | `any` | Search as seen from one country (`JP`, `DE`, `BR`, …, about 50 markets) or `any` |
| `followRelatedVideos` | boolean | `false` | Also collect tagged posts from the related videos of each tagged post (needs 4096 MB memory) |
| `maxResultsPerProfile` | integer | `50` | Max saved posts per account (1-500) |
| `maxItems` | integer | – | Max saved posts across all accounts |
| `downloadVideos` | boolean | `false` | Save video files and add `downloadedVideoUrl` |
| `addPostCountry` | boolean | `false` | Add the country each post was made in (`locationCreated`) |

Older inputs keep working: the previous `confirmedMentionsOnly` switch is still honoured when it is sent, and profile links work in `usernames`.

### Example: brand mentions from the last 30 days, most liked first

```json
{
  "usernames": ["gymshark", "@sephora"],
  "datePosted": "pastMonth",
  "sortBy": "mostLiked",
  "maxResultsPerProfile": 100
}
```

### Example: only clickable tags, as much as TikTok shows

```json
{
  "usernames": ["https://www.tiktok.com/@billieeilish"],
  "mentionFilter": "tagged",
  "searchDepth": "deep",
  "maxResultsPerProfile": 500
}
```

### Example: daily monitoring of new posts with at least 10,000 views

```json
{
  "usernames": ["nike", "adidas", "puma"],
  "postedAfter": "1 day",
  "minPlayCount": 10000,
  "sortBy": "newest"
}
```
## Use cases

- **Brand and sponsorship monitoring:** watch who tags a brand handle, flag paid-partnership posts and keep a permanent copy of the video as proof.
- **Influencer discovery:** find creators who repeatedly tag a product or account, ranked by views or likes.
- **Campaign reporting:** export post-level engagement (views, likes, comments, shares, saves, reposts) and captions for dashboards.
- **Competitor watch:** see which creators a competitor's account tags and how often, or monitor several accounts in one run.
- **Market research:** search from a chosen country and compare which creators and posts mention a handle in each market.

## FAQ

**Do I need a TikTok account, cookies or a proxy?**
No. The tracker reads what TikTok shows logged-out visitors and picks its connection automatically.

**How many mentions can I expect per account?**
TikTok's search returns tens to a few hundred posts per account. Popular brands usually get dozens of tagged posts; small accounts may get a handful or none. Deep search typically finds 30-60% more posts than standard. The 500 limit is a cap, not a promise.

**Why are some rows `captionText` instead of `tagged`?**
TikTok only creates a clickable tag when the creator picks the account from the suggestion list while writing. Typing `@nike` by hand leaves plain text, so the post is a mention but not a tag.

**Why does the caption show "@Gymshark" when the handle is "gymshark"?**
Tags display the account's name, not always its handle. `mentionEntry.username` always holds the real handle and `displayText` holds what the caption shows.

**What does "Also follow related videos" add?**
TikTok search returns only a share of the posts that tag an account. With this option on, the tracker opens the related videos of every tagged post and keeps the ones that also mention the account, a few hops deep. In our tests it roughly doubled the tagged posts found for accounts that already had some, mostly from creators who tag the account regularly. Those rows have `foundVia: "relatedVideos"`. It makes runs slower and needs at least 4096 MB of memory (set it under the run options); with less memory the step is skipped and the run says so.

**How do I check sponsored posts?**
Filter on `isPaidPartnership`: it is `true` exactly when TikTok shows the "Paid partnership" label on the post. Combine it with `mentionType: "tagged"` to list paid posts that tag your brand.

**Do the video links work outside TikTok?**
TikTok's own media links that point at video or sound files (`video.playUrl`, `video.downloadAddr`, `music.playUrl` and the quality variants in `video.bitrateInfo`) are signed, expire (see `mediaUrlExpiresAt`) and usually only play inside TikTok. Turn on "Save video files" to get a permanent, playable copy in `downloadedVideoUrl`. Cover images, avatars, sound covers and slideshow photos open anywhere.

**Can I search by country or language?**
Yes. Set "Search from country" to see the posts TikTok shows people in that market, for example Japan or Brazil. Runs with a country take longer. To see where each post was actually made, also turn on "Add the country each post was made in" (`locationCreated`); `textLanguage` gives the caption language.

**Can I monitor accounts on a schedule?**
Yes. Schedule the task with `postedAfter` set to your interval (for example `1 day`), and deduplicate by `postId` across runs.

**Is this affiliated with TikTok?**
No. It is an independent tool that reads public TikTok pages.

## Known limits

- **TikTok decides how deep a search goes.** Each search stops when TikTok has nothing more to show, usually after tens to a couple of hundred posts. Deep search combines several searches to go further.
- **Most search results are related posts, not tags.** Only a small share of what TikTok returns for a handle actually tags it. That is why rows are labelled with `mentionType`, why the default keeps only real mentions, and why "Also follow related videos" exists. Accounts that no search result tags get nothing extra from it.
- **Results depend on time and region.** TikTok personalises search, so two runs can return slightly different posts. Pick a "Search from country" to look at one market, and for monitoring schedule runs and deduplicate by `postId`.
- **Comments are not searched.** TikTok offers no way to find comments that mention an account; scanning comments of related posts finds almost none.
- **Counts are a snapshot.** Views, likes and comments are as of `scrapedAt`; schedule runs to build a history.

## For AI agents and automations

- Filter on `mentionType` instead of reading captions: `tagged` is TikTok's own tag of the account, `captionText` is a typed `@handle` without a working tag, `searchResult` is only related.
- Use `targetUserId` to join rows to an account. Handles can change; IDs don't.
- Deduplicate across scheduled runs by `postId`. Engagement numbers are a snapshot at `scrapedAt`.
- An empty dataset with a successful run means TikTok had no matching posts. `TARGET_SUMMARY` tells you whether the account exists and how many posts were checked.
