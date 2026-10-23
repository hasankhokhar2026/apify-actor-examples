# Bilibili Video Search, Ranking & Metadata Scraper

Collect public video metadata from Bilibili without an account. Search a keyword with Bilibili's own sort and filter options, resolve video links or IDs, walk the popular feed, or pull all-time, origin, rookie, and weekly ranking charts. Each row carries the identifiers, uploader, engagement counters, duration, publish time, cover, and optional detail fields such as tags, coin/share counts, parts, resolution, and uploader followers.

## What this actor does

- **Four modes:** `search`, `byVideoUrl`, `popular`, and `ranking` (weekly charts are a ranking type).
- **Search filters:** sort by relevance, views, newest, danmaku, favorites, or comments; publication date range; duration bucket; and partition.
- **Ranking coverage:** 15 partitions across all-time, originals-only, rookie, and the weekly series (one issue per run, or a specific issue number).
- **Detail enrichment:** optional per-video enrichment adds tags, coin and share counts, cid, every part, resolution, uploader followers, and the full stat block. Video lookups are always enriched.
- **Duplicate-safe:** repeated videos across pages or queries are emitted once, and course-ad rows without a video ID are skipped.
- **Stable field names:** every mode uses the same names, and a field is omitted only when Bilibili has no real value for that video, never replaced with a placeholder.
- **Empty fields are omitted:** missing values are left out instead of being returned as `null`.

## Output per video

- `recordType` — `"video"` for normal rows, `"error"` for error rows.
- `bvid` — BV-format video ID.
- `aid` — numeric AV video ID.
- `cid` — main part content ID (detail, popular, ranking, weekly, and enriched rows).
- `title` — video title, with search highlighting and HTML entities cleaned.
- `description` — video description.
- `tags[]` — video tags (search rows and enriched rows).
- `typeName` — partition or category label.
- `partitionId` — Bilibili category ID for the video (often a subcategory of the selected partition).
- `author` — uploader display name.
- `authorMid` — uploader numeric member ID.
- `authorAvatar` — uploader avatar URL.
- `authorFollowers` — uploader follower count (enriched rows).
- `viewCount` — total views.
- `likeCount` — likes.
- `coinCount` — coins (enriched, popular, ranking, and weekly rows; absent on raw search rows).
- `favorites` — favorites/collections.
- `shareCount` — shares (enriched, popular, ranking, and weekly rows; absent on raw search rows).
- `danmaku` — aggregate danmaku count.
- `replyCount` — comment count.
- `duration` — length in seconds.
- `durationText` — length formatted as `H:MM:SS` or `M:SS`.
- `publishTime` — publish time in UTC ISO format.
- `publishDate` — publish date in `YYYY-MM-DD` (UTC).
- `coverUrl` — cover image URL.
- `pageCount` — number of parts in a multi-part upload.
- `pages[]` — per-part objects with `page`, `cid`, `title`, `duration`, `width`, and `height` (enriched rows).
- `resolution` — main part resolution, for example `1920x1080`.
- `dynamic` — the uploader's video dynamic text, when present.
- `copyright` — Bilibili copyright flag.
- `uploadRegion` — uploader's declared location, when published.
- `rankIndex` — 1-based chart position (ranking and weekly rows).
- `recReason` — recommendation reason shown by Bilibili (popular and weekly rows, when present).
- `engagementRate` — `(likes + coins + favorites + shares + replies) / views`, rounded to four decimals. Raw search rows have no coin/share counters, so their rate uses the counters Bilibili returns there.
- `coinLikeRatio` — `coins / likes`, rounded to four decimals, when likes are non-zero. Absent on raw search rows because Bilibili does not return coins in search results.
- `videoUrl` — canonical Bilibili video page.
- `sourceUrl` — the search page, chart, or video page the row came from.
- `sourceQuery` — original search keyword (search rows only).
- `dataSource` — `search`, `video`, `popular`, `ranking`, or `weekly`.
- `enriched` — `true` when per-video detail data was merged.
- `scrapedAt` — UTC timestamp of collection.

## Output per error record

Error rows carry `recordType: "error"`, an `errorType` (`invalid_input`, `not_found`, `blocked`, `rate_limited`, `upstream_error`, `parse_error`, or `empty_response`), a `message`, the `sourceUrl` that failed, optional `statusCode` and `biliCode` values, a `retryable` flag, and `scrapedAt`. Error rows never count toward `maxItems`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | String (select) | `search` | `search`, `byVideoUrl`, `popular`, or `ranking`. |
| `searchQueries` | List of strings | `[]` (prefill `["python"]`) | Keywords to search. Use one entry per alias; Bilibili does not translate Chinese and English keywords. Used in `search` mode. |
| `videoUrls` | List of strings | `[]` | Video pages, `b23.tv` short links, bare BV IDs, `av` IDs, or numeric AV IDs. Used in `byVideoUrl` mode. |
| `maxItems` | Integer | `20` | Maximum video rows (1-1000). Error rows do not count. |
| `sort` | String (select) | `totalrank` | Search order: `totalrank`, `click`, `pubdate`, `dm` (most danmaku), `stow` (most favorites), or `scores` (most comments). Used in `search` mode. |
| `publishedAfter` | Date | – | Keep videos published on or after this UTC date (`YYYY-MM-DD`). Used in `search` mode. |
| `publishedBefore` | Date | – | Keep videos published on or before this UTC date (`YYYY-MM-DD`). Used in `search` mode. |
| `duration` | String (select) | `all` | `all`, `short` (under 10 min), `medium` (10-30 min), `long` (30-60 min), or `verylong` (over 60 min). Used in `search` mode. |
| `partition` | String (select) | `0` | Partition for search filtering or the ranking chart (all plus 14 named partitions). Ignored for weekly charts. |
| `rankingType` | String (select) | `all` | `all`, `origin`, `rookie`, or `weekly`. Used in `ranking` mode. |
| `weekNumber` | Integer | – | A specific weekly issue number (1-10000). Omit for the latest issue. |
| `enrichDetails` | Boolean | `false` | Add a detail request per unique video to fill tags, coin/share counts, cid, parts, resolution, and uploader followers. Usually adds 3-10 seconds per video, depending on Bilibili latency. |
| `proxyConfiguration` | Object | – | Optional. The actor starts direct and retries through fresh and anonymous browser sessions; a proxy you provide is used only as the final escalation stage. |

Either date bound can be used alone; the scraper fills in the missing bound because Bilibili applies a publish-date filter only when both bounds are supplied.

### Example: newest short Python videos from the knowledge partition

```json
{
  "mode": "search",
  "searchQueries": ["python"],
  "sort": "pubdate",
  "partition": "36",
  "duration": "short",
  "publishedAfter": "2026-01-01",
  "maxItems": 40
}
```

### Example: enrich a batch of mixed video links

```json
{
  "mode": "byVideoUrl",
  "videoUrls": [
    "https://www.bilibili.com/video/BV1wD4y1o7AS/",
    "BV1Jgf6YvE8e",
    "av170001",
    "https://b23.tv/abc123"
  ]
}
```

### Example: top popular videos with full detail

```json
{
  "mode": "popular",
  "maxItems": 100,
  "enrichDetails": true
}
```

### Example: latest weekly chart in the food partition

```json
{
  "mode": "ranking",
  "rankingType": "weekly",
  "partition": "211",
  "maxItems": 50
}
```

## Use cases

- **Creator and niche research** — search Chinese and English keywords with date and duration filters to see who is active in a topic.
- **Trend tracking** — schedule daily pulls of a partition's all-time, origin, rookie, or weekly chart and compare rank movement.
- **Content benchmarking** — compare views, likes, coins, favorites, and comments across videos and partitions.
- **Dataset building** — export stable video metadata for recommendation models, topic analysis, or media monitoring.
- **Catalog resolution** — turn a list of saved links or BV IDs into complete metadata with one run.
- **Engagement analysis** — use the derived engagement rate and coin-to-like ratio to screen videos for authentic interaction.

## FAQ

### Do I need a Bilibili account or cookies?

No. Search, video lookups, the popular feed, and every ranking chart are read from public pages without a login.

### Does this actor collect comments, danmaku text, subtitles, creator video lists, or video files?

No. The actor returns public video metadata and aggregate counters only. Comment text, individual danmaku messages, subtitles, creator video lists, and media downloads are outside its scope. Uploader details and follower counts come from the videos themselves.

### Why are `coinCount` and `shareCount` missing on some search rows?

Bilibili's search results do not include coin or share counts. Set `enrichDetails` to `true` (or use `byVideoUrl`) to fill them from the video detail data.

### How much slower is detail enrichment?

Each enriched video usually adds 3-10 seconds, depending on Bilibili latency. A 1,000-row search with enrichment can take an hour or more; the default run is intentionally small.

### Why do I get fewer videos than `maxItems`?

Search returns at most 1,000 rows across 20 pages, the popular feed currently holds about 643 videos, a ranking chart has roughly 87-100 entries, and a weekly issue has about 48-49. Filters applied after collection can reduce the count further.

### What do `dm` and `scores` mean in the sort list?

`dm` sorts by danmaku count and `scores` sorts by comment count. Older actors labelled `scores` as a rating; that is not what Bilibili returns.

### Are course ads included in search results?

No. Search pages can contain course-promotion rows without a video ID; those are skipped, so a page of 50 results can yield fewer than 50 videos.

### What timezone are the date filters in?

Both `publishedAfter` and `publishedBefore` are interpreted in UTC, and `publishTime` is emitted in UTC ISO format.

### Can I fetch a specific weekly issue?

Yes. Set `rankingType` to `weekly` and pass the issue number in `weekNumber`. Leave `weekNumber` empty to get the latest issue.

### What happens with an invalid link or ID?

That input produces an error row with `recordType: "error"` and an `errorType`, so you can see exactly which entry failed. Valid entries in the same run still produce video rows.

### Do I need to configure a proxy?

No. The actor starts with a direct connection and retries through a fresh session and an anonymous browser session. If you provide a proxy, it is used only after those stages; without one, a persistent block ends in a typed error record.

### Is this actor affiliated with Bilibili?

No. It is an independent third-party tool and is not affiliated with, endorsed by, or sponsored by Bilibili or its operators.
