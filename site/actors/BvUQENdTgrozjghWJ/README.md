# TikTok Explore Feed Trending Post Scraper

Collect the public TikTok Explore feed by category with no login, cookies or API keys. Choose All or any of the 20 topic feeds, target one or more country markets, filter by post age and engagement, and get one row per post with author stats, music, hashtags, mentions, subtitles, POI data and derived performance metrics. Signed TikTok media URLs can be copied to stable key-value store URLs in the same run, covering video, covers, avatars, music, slideshow images and subtitle files.

## What this actor does

- **21 Explore categories:** All (`120`) plus the 20 topic feeds; accepts category names, numeric IDs and legacy `{id,name}` objects.
- **Market and filter controls:** optional ISO country markets, post age, and minimum views, likes, comments and shares.
- **Rich post records:** rank, engagement rates, author stats, music, hashtags, mentions, POI, ad/AI flags and subtitle metadata.
- **Stable media:** with `rehostVideo`, TikTok video, covers, avatars, music, slideshow images and subtitle files are stored in the run's key-value store and emitted as durable public URLs.
- **Empty fields are omitted** — records contain no `null`, empty string, empty list or empty object.

## Output per post

One row per Explore post. `feedType` is always `explore` and `recordType` is `explorePost`. Empty values are removed, so a field that is not listed is absent for that post rather than `null`.

### Identity and position

| Field | Description |
|---|---|
| `postId` | TikTok post/video ID (string) |
| `postType` | `video` or `slideshow` |
| `postUrl`, `sourceUrl` | Public post URL; `sourceUrl` mirrors `postUrl` |
| `feedType` | Always `explore` |
| `categoryId`, `categoryName` | Requested Explore category; All is `120` |
| `itemCategoryId`, `itemCategoryName` | The post's own TikTok category, which can differ from the requested category |
| `rank`, `position` | 1-based rank and 0-based position within the market/category after filters and dedupe |
| `marketRegion` | Selected ISO country, or the region read from Explore page state when no country was selected; omitted rather than guessed |

### Content, engagement and flags

| Field | Description |
|---|---|
| `caption`, `textLanguage` | Post caption and detected caption language |
| `createTime`, `createdAt` | Original Unix timestamp and ISO 8601 UTC creation time |
| `locationCreated` | Emitted only when post-detail enrichment supplies it; the Explore feed payload does not contain it |
| `hashtags[]` | `name`, `id` and `isCommerce` |
| `mentions[]` | `username`, `start`, `end` and `awemeId` |
| `playCount`, `likeCount`, `commentCount`, `shareCount`, `collectCount`, `repostCount` | Raw TikTok counters |
| `engagementRate` | `(likes + comments + shares + collects) / plays`, 6 decimals; omitted when plays is zero |
| `ageHours` | Hours between post creation and run start, 2 decimals |
| `playsPerHour` | `playCount / ageHours`, 1 decimal; omitted when age is not positive |
| `stitchEnabled`, `duetEnabled`, `shareEnabled` | Post interaction settings |
| `isAd` | Whether the post is marked as an ad |
| `adFlags` | `adAuthorization`, `brandOrganicType`, `adLabelVersion`, `aigcLabelType`, `moderationAigcLabelType` and `isAiGenerated` |

### Author, music, video, place and subtitles

| Field | Description |
|---|---|
| `author` | Profile snapshot: `id`, `secUid`, `username`, `displayName`, `bio`, `verified`, `privateAccount`, `roomId`, `avatarUrl` (plus `avatarUrlOriginal` after rehosting), `followerCount`, `followingCount`, `heartCount`, `videoCount`, and `commentSetting`, `duetSetting`, `stitchSetting`, `downloadSetting`, `isEmbedBanned` when present |
| `music` | `id`, `title`, `authorName`, `original`, `duration`, `album`, `playUrl` (plus `playUrlOriginal`), `coverUrl` (plus `coverUrlOriginal`) |
| `video` | Metadata `width`, `height`, `duration`, `ratio`, `definition`, `bitrate`; URLs `playUrl`, `downloadUrl`, `sourcePlayUrl`, `sourceDownloadUrl`; images `cover`, `originCover`, `dynamicCover` and resolution-keyed `zoomCover`; after rehosting, the signed sources are kept in `playUrlOriginal`, `downloadUrlOriginal`, `coverOriginal`, `originCoverOriginal`, `dynamicCoverOriginal` and `zoomCoverOriginal` |
| `place` | POI data: `id`, `name`, `address`, `city`, `province`, `country`, `countryCode`, `category` and `typeName` |
| `images[]` | Slideshow images: `ordinal`, `width`, `height`, `urlList`, and `urlListOriginal` after rehosting |
| `subtitles[]` | `languageCode`, `format`, `url` (plus `urlOriginal` after rehosting), `expiresAt`, `sizeBytes`, `source`, `version`, and `text` when `includeTranscripts=true` |
| `mediaExpiresAt` | Per-asset source expiry: `video`, `cover`, `avatar`, `music`, `subtitles` |
| `mediaUrlExpiresAt` | Earliest of the media expiries |

### Media rehosting status

| Field | Description |
|---|---|
| `mediaRehosted` | `true` when the video was stored, or for a post without video when at least one other media field was stored |
| `mediaRehostedAll` | `true` when every attempted media field was stored |
| `rehostStatus` | Record outcome: `ok`, `partial`, or a fail-soft reason such as `http_403`, `no_video_response`, `not_mp4`, `not_vtt`, `network_error` or `kv_error` |
| `rehostStatusByField` | Per-field status keyed by output path, for example `video.cover`, `music.playUrl`, `author.avatarUrl`, `images[0].urlList` and `subtitles[0].url` |
| `mediaRehostedFields` | Boolean per-field success map derived from `rehostStatusByField` |
| `mediaSources` | Original signed URL or URL list for every rehosted field |

### Monitoring and provenance

| Field | Description |
|---|---|
| `isNew`, `firstSeen`, `lastSeen` | Present only when `onlyNew=true`: whether the post is new in this run, plus its state-store timestamps |
| `scrapedAt` | ISO 8601 UTC run-start time |
| `recordType` | Always `explorePost` |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `categories` | array | `["All"]` | Required. Names, numeric IDs or legacy `{id,name}` objects. Prefill is `["All"]`. |
| `maxItemsPerCategory` | integer 1–1,000 | `3` | Hard cap per category, checked before a page is emitted. Prefill is `3`. |
| `maxItems` | integer 1–1,000 | – | Legacy alias used only when `maxItemsPerCategory` is absent or exactly `3`; an explicit non-default `maxItemsPerCategory` wins. |
| `categoryId` | integer 1–100,000 | – | Legacy single-category shorthand. It replaces `categories`; `123` maps to `120`. |
| `autoDiscoverCategories` | boolean | `false` | Expand an empty or All-only selection to all 21 categories, or append missing categories to a partial selection. |
| `countries` | array of ISO 3166-1 alpha-2 | `[]` | Up to 10 markets. Empty means the current connection and no proxy. Each selected market needs its own egress. |
| `country` | string | `""` | Single-country shorthand; ignored when `countries` is non-empty. |
| `postedWithin` | string | `any` | `any`, `24h`, `7d`, `30d` or `90d`, applied to `createTime`. |
| `minViews` | integer | `0` | Drop posts below this play count. |
| `minLikes` | integer | `0` | Drop posts below this like count. |
| `minComments` | integer | `0` | Drop posts below this comment count. |
| `minShares` | integer | `0` | Drop posts below this share count. |
| `onlyNew` | boolean | `false` | Emit only post IDs that are not already in the state store. |
| `stateKey` | string | derived | Key inside the `tiktok-explore-only-new` state store; blank derives one from your categories, markets and filters. |
| `includeTranscripts` | boolean | `false` | Fetch subtitle WebVTT files and add `subtitles[].text`. Subtitle metadata is returned even when this is off. |
| `includePostDetails` | boolean | `false` | Fetch one public post-detail page per emitted post to add `locationCreated` and missing POI/slideshow data. Fail-soft. |
| `rehostVideo` | boolean | `true` | Copy every signed media field into the key-value store and emit stable public URLs. Default `true`; the form prefills `false` for a lighter first run. |

Category IDs: 100 Anime & Comics, 101 Shows, 102 Beauty Care, 103 Games, 104 Comedy, 105 Daily Life, 106 Family, 107 Relationship, 108 Drama, 109 Outfit, 110 Lipsync, 111 Food, 112 Sports, 113 Animals, 114 Society, 115 Cars, 116 Education, 117 Fitness & Health, 118 Technology, 119 Singing & Dancing, 120 All. `121` and `122` are empty upstream and `124+` are invalid upstream, so they are skipped with a warning. No TikTok account, cookies, API keys or user proxy credentials are needed.

### Example: default metadata run

```json
{
  "categories": ["All"],
  "maxItemsPerCategory": 3,
  "rehostVideo": false
}
```

### Example: rehost every media field

```json
{
  "categories": ["All"],
  "maxItemsPerCategory": 10,
  "rehostVideo": true
}
```

### Example: filtered multi-market run

```json
{
  "categories": ["All", "Sports"],
  "countries": ["PK", "TH"],
  "maxItemsPerCategory": 100,
  "postedWithin": "7d",
  "minViews": 10000,
  "minLikes": 500,
  "rehostVideo": false
}
```

### Example: only-new monitoring

```json
{
  "categories": ["Technology"],
  "maxItemsPerCategory": 100,
  "onlyNew": true,
  "stateKey": "tech-daily",
  "rehostVideo": false
}
```

## Use cases

- **Social media marketing** — see which formats, sounds and captions are trending across Explore categories and markets.
- **Creator and agency research** — benchmark author follower counts, engagement rates and post performance against category peers.
- **Content strategy** — compare hooks, hashtags and mentions across markets before planning a campaign.
- **Brand and ad monitoring** — filter ad-flagged posts and AI/AIGC labels within a category or country.
- **Dataset building** — export metadata-rich rows for recommendation models, trend dashboards and research datasets.
- **Localization research** — collect the same category through different country egresses to compare regional feeds.

## FAQ

### Do I need a TikTok login, cookies, or an API key?

No. The actor reads publicly available Explore data and needs no account, cookies, tokens or user proxy credentials.

### How many posts can I get per category?

Up to 1,000 per category. TikTok returns at most 30 items per request, and Explore has no cursor, so the actor repeats requests and removes duplicates until it reaches your cap or the feed stops producing new posts. A category can run short when TikTok rotates the feed; the run status message reports the actual count and stop reason.

### What is the difference between `categoryId` and `itemCategoryId`?

`categoryId` is the Explore feed you requested. `itemCategoryId` is the post's own TikTok category. Explore feeds are mixed, so a Sports request can contain posts classified as Comedy or Society. All is `120`; `123` is accepted as a legacy alias for All, while `121` and `122` are empty upstream and `124+` are invalid.

### Why can the same post appear more than once, and is rank stable?

Each selected country is a separate collection. Dedupe is per market and post ID, so a post appears once per market but can appear once for each requested country. `rank` and `position` are run-local emission order after filters and dedupe, not a permanent TikTok ranking; the Explore feed changes between calls, so ranks can differ in a later run.

### How do country and market targets work?

The TikTok feed follows the network egress, not a query parameter. With `countries` empty the actor uses the current connection and no proxy. Each selected country uses a per-country Apify proxy, starting with the automatic pool and escalating to residential only after a proven block. If a country is unavailable, it is skipped with a status message instead of silently using another market.

### Do TikTok media URLs expire?

Yes. Signed video, cover and avatar URLs usually expire in about 48 hours; music is often about 24 hours, and the fallback play carrier can be shorter. `mediaExpiresAt` exposes per-asset expiry and `mediaUrlExpiresAt` gives the earliest. With `rehostVideo=true`, the emitted media URLs point at the key-value store instead.

### What does media rehosting store?

For every emitted post it stores the video plus cover, origin cover, dynamic cover, all zoom-cover sizes, author avatar, music audio and cover, slideshow images, and subtitle VTT files in the run's key-value store. The main field becomes a stable public key-value store URL, while the signed source stays in `<field>Original` and in `mediaSources`. Rehosting is fail-soft per field: a failed cover or subtitle keeps the original URL and never drops the post, and the status fields tell you exactly what succeeded. Rehosted files last for the lifetime of the store record, not forever; the URLs are public, need no Apify token, and store retention settings still apply. Rehosting adds one post-page load and several media downloads per record plus storage, so keep `maxItemsPerCategory` small or set `rehostVideo=false` for metadata-only runs.

### Why are some fields missing?

Empty values are omitted, so a record contains only fields TikTok returned. `locationCreated` is not in the Explore feed payload and appears only with `includePostDetails=true` when the post detail page supplies it. Explore rarely exposes slideshows, so `images` is usually absent; detail enrichment can recover it for a known photo post. Subtitle metadata is source-dependent.

### What does `onlyNew` do?

It keeps a named set of post IDs in the `tiktok-explore-only-new` state store and emits only IDs that were not seen before. `stateKey` names the set; leave it blank to derive one from your categories, markets and filters. State is pruned to 90 days and capped at 200,000 IDs.

### Is this affiliated with TikTok?

No. This is an independent third-party actor that reads publicly available Explore data. It is not affiliated with or endorsed by TikTok.
