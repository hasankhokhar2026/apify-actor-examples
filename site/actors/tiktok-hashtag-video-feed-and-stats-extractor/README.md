# TikTok Hashtag Stats and Video Feed Collector

Collect the numbers behind a TikTok hashtag and the videos underneath it. For each tag you get one all-time stats row — total videos, total views, cover images, commerce flag — plus, when you ask for them, video rows with captions, authors, music, engagement counts, and the exact source each video came from. No TikTok login, cookies, or API key is needed.

## What this actor does

- **Four modes:** `stats` (cheapest), `feed` (the public hashtag video feed), `search` (one page of TikTok keyword/hashtag results), and `auto` (stats plus feed, with search added when the feed is short)
- **One aggregate row per hashtag:** all-time `videoCount` and `viewCount`, canonical hashtag name and ID, description, commerce flag, cover images, and campaign announcement text when TikTok provides it
- **Video rows with provenance:** `source` (`feed` or `search`), 1-based `position`, `region`, `scrapedAt`, and `carriesSearchedHashtag` so you can tell a true tag video from a search match
- **Rich video payload:** post ID/URL/caption/language/creation time, play/like/comment/share/collect/repost counts, author profile and stats, music metadata, video dimensions and cover, slideshow images, hashtags, and mentions
- **Deduplicated and capped:** repeated videos are removed by post ID, and every mode honours `maxVideosPerHashtag`
- **Empty fields are omitted** from every record instead of being written as `null`

## Output per hashtag stats row

Stats rows have `recordType: "hashtag_metadata"`.

- `recordType` — always `"hashtag_metadata"`
- `searchedHashtag` — the requested hashtag, lowercased and without `#`
- `hashtag` — the same requested hashtag, for convenient filtering
- `hashtagId` — TikTok's internal challenge ID
- `hashtagName` — hashtag name as TikTok stores it
- `desc` — hashtag description, when present
- `isCommerce` — whether TikTok marks the hashtag as commercial
- `videoCount` — all-time video count, as a string because values can be very large
- `viewCount` — all-time view count, as a string
- `profileLarger` / `profileMedium` / `profileThumb` — hashtag image URLs
- `coverLarger` / `coverMedium` / `coverThumb` — cover images, when present
- `announcementTitle` / `announcementBody` — campaign announcement text, when present
- `shareMeta` — `{title, desc}` share preview, when present
- `source` — always `"challenge_detail"` on stats rows
- `region` — market used for the run
- `scrapedAt` — UTC ISO 8601 timestamp

## Output per video

Video rows have `recordType: "post"`.

- `recordType` — always `"post"`
- `searchedHashtag` — the hashtag whose run produced this video
- `source` — `"feed"` for the hashtag feed or `"search"` for keyword-search results
- `position` — 1-based order in the collected list for that hashtag
- `carriesSearchedHashtag` — `true` when the video's own hashtag entities include the searched tag
- `carriesAnyHashtag` — `true` when the caption carries at least one hashtag
- `region` — market used for the run
- `scrapedAt` — UTC ISO 8601 timestamp
- `postId`, `postType` (`video` or `slideshow`), `postUrl`
- `caption`, `textLanguage`, `locationCreated`
- `createTime` (Unix epoch), `createdAt` (ISO 8601)
- `stitchEnabled`, `shareEnabled`, `duetEnabled`, `isAd`
- `playCount`, `likeCount`, `commentCount`, `shareCount`, `collectCount`, `repostCount`
- `author` — `{id, secUid, username, displayName, bio, verified, privateAccount, avatarUrl, followerCount, followingCount, heartCount, videoCount}`
- `authorStats` — the author's follower, following, heart, video, and digg counts as integers
- `music` — `{id, title, authorName, original, duration, playUrl, coverUrl}`
- `video` — `{width, height, duration, ratio, playUrl, cover}`
- `hashtags[]` — `{name, id, isCommerce}` entries from the caption
- `mentions[]` — `{username, start, end, awemeId}` entries from the caption
- `textExtra` — raw caption entities when present
- `images[]` — `{ordinal, width, height, urlList}` for slideshow posts
- `mediaUrlExpiresAt` — UTC ISO 8601 expiry of the signed media URLs, when detectable

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `hashtags` | array | – | Hashtags to collect. Accepts `fitness`, `#fitness`, or a TikTok tag URL. Required, 1–10 values |
| `mode` | string | `stats` | `stats`, `feed`, `search`, or `auto` |
| `maxVideosPerHashtag` | integer | `30` | Upper bound per hashtag (0–300). Use `0` for stats only. This is a cap, not a promise — TikTok often returns fewer |
| `maxHashtags` | integer | `10` | Process only the first N hashtags (1–10) |
| `includeStatsRow` | boolean | `true` | Emit the stats row before video rows in `feed`, `search`, and `auto`. `stats` mode always emits it |
| `region` | string | `US` | Market used for the feed. Only `US` is verified |
| `proxyConfiguration` | object | – | Optional. Leave empty to use the built-in US residential connection with automatic fallback |

### Example: cheapest stats check

```json
{
  "hashtags": ["fitness"],
  "mode": "stats",
  "maxVideosPerHashtag": 0
}
```

### Example: collect 60 videos from a campaign hashtag

```json
{
  "hashtags": ["summerfashion"],
  "mode": "feed",
  "maxVideosPerHashtag": 60,
  "includeStatsRow": true
}
```

### Example: keyword search fallback

```json
{
  "hashtags": ["booktok"],
  "mode": "search",
  "maxVideosPerHashtag": 40,
  "includeStatsRow": false
}
```

### Example: several tags with auto mode

```json
{
  "hashtags": ["#fitness", "gymtok", "https://www.tiktok.com/tag/workout"],
  "mode": "auto",
  "maxVideosPerHashtag": 90,
  "maxHashtags": 3
}
```

## Use cases

- **Campaign sizing** — compare all-time video and view counts across several brand or campaign hashtags in one run
- **Content research** — sample current top videos under a niche tag and study hooks, captions, and creators
- **Creator discovery** — rank authors by follower and engagement counts inside a hashtag feed
- **Social listening** — track how a hashtag's totals change across repeated snapshots
- **Agency reporting** — export one clean dataset of hashtag totals plus video-level evidence for a client deck
- **Search-gap analysis** — compare true feed rows against keyword-search rows using `source` and `carriesSearchedHashtag`

## Limits and data freshness

- **Region:** the public video feed is verified for the United States only. Other markets are not exposed until each one is verified.
- **Feed size:** TikTok serves roughly 30 videos per page and stops early for many tags. A typical run gets about 100–150 videos before the tag's own feed stops; very large tags can stop sooner. The platform's practical ceiling is far below “all videos”.
- **Search size:** search returns one page of roughly 50–90 results. It is keyword search, not guaranteed tag membership — use `carriesSearchedHashtag` to filter.
- **No date or sort filter:** TikTok's public hashtag feed does not expose a reliable date range or sort order, so this actor does not offer one.
- **Stats are all-time:** `videoCount` and `viewCount` describe every video ever posted with the tag, not only the rows in your dataset.
- **Freshness:** every record carries `scrapedAt`. Stats and video counts move continuously on TikTok.
- **Media URLs expire:** video, audio, cover, and avatar URLs are signed and time-limited. `mediaUrlExpiresAt` tells you when they were expected to expire. Download or copy media promptly if you need it; this actor does not rehost files.
- **Empty fields are omitted:** if TikTok does not return a field for a record, the field is absent rather than `null`.

## FAQ

**Do I need a TikTok login or cookies?**
No. The actor reads public hashtag pages and public search results without any account.

**Do I need to configure a proxy?**
No. Leave `proxyConfiguration` empty and the actor picks a working US connection, falling back automatically if the preferred one is unavailable. Feed mode depends on a US residential connection, which is billed by Apify proxy usage. As a guide, feed runs often add roughly $0.05–0.06 per hashtag in residential transfer; stats-only runs are cheaper. Actual cost varies with run time, row count, and current Apify pricing.

**Why did I get fewer videos than `maxVideosPerHashtag`?**
TikTok stops serving the public feed after its own internal limit. The actor also stops when TikTok reports no more pages, when no new videos arrive after repeated scrolls, or when the tag's feed is empty. `maxVideosPerHashtag` is an upper bound, never a guarantee.

**Why is the stats row's view count larger than the views in my videos?**
Stats are all-time aggregates for the whole hashtag. Your dataset holds only the videos this run could collect.

**Why do some search videos not carry my hashtag?**
TikTok search matches keywords and related content, not exact tag membership. Check `carriesSearchedHashtag`; `false` means the video appeared in search but does not list the searched tag as a hashtag entity.

**What is the difference between `feed` and `search`?**
`feed` is TikTok's hashtag video feed and is the closest thing to "videos posted under this tag". `search` is a single page of keyword results and may include only loosely related videos. `auto` uses the feed and only adds search when the feed returns less than one page.

**Does `auto` always add search results?**
No. Search is a supplement, not a replacement. It is used only when the feed delivers no rows or fewer than a full page, up to your per-hashtag cap.

**Are duplicate videos removed?**
Yes. Videos are deduplicated by post ID within each hashtag. The same video can still appear under two different hashtags because each row records its `searchedHashtag`.

**Do old saved tasks still work?**
Yes. Inputs using `metadata`, `posts`, `topPosts`, `maxPostsPerHashtag`, or `includeHashtagMetadata` are mapped to the new fields automatically.

**Will media links still work tomorrow?**
TikTok media links are signed and expire. Use `mediaUrlExpiresAt` as a guide and refresh the dataset when you need current URLs.

**Is this affiliated with TikTok?**
No. This is an independent third-party actor that reads publicly available TikTok pages and is not operated or endorsed by TikTok.
