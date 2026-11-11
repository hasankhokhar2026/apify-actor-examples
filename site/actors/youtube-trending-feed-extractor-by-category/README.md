# YouTube Trending Feed Extractor by Category & Market

Scrape **YouTube's current trending surfaces** — the official music, movie-trailer and podcast charts, plus the Gaming, News, Sports, Learning and Courses category hubs. Choose from seven chart types across 68 markets and global where published, or read up to 50 videos from Gaming trending and Gaming live. Every row keeps its chart rank or page position, and optional exact video details add lifetime views, likes, comment counts, upload dates, channel subscriber counts where published, YouTube category, descriptions, tags and Shorts eligibility. No login, API key or proxy setup is required.

## What this actor does

- **Two modes:** `charts` for YouTube's official rankings and `hubs` for category pages
- **Seven charts across 68 markets plus global** where the selected chart publishes a global ranking
- **Category hubs:** Gaming trending, Gaming live, News with selectable sections, Sports, Learning and Courses
- **Exact video details:** optional lifetime views, likes, exact comment counts, upload date and description, plus player-only category, tags and Shorts flags when YouTube exposes them; channel subscriber counts are added when YouTube publishes an exact number
- **Empty fields are omitted** — no nulls, blank strings or empty arrays in any row

## Output per chart entry

Chart rows describe ranked music, trailer or podcast entries. Each row keeps the chart position and adds movement and history fields where the chart publishes them.

- `position` — chart rank
- `recordType` — `chartEntry`
- `type` — `video`, `track`, `artist` or `podcastShow`
- `videoId`, `trackId`, `artistId`, `playlistId` — identifiers available for the entry type
- `title` — entry title
- `url` — watch, channel or playlist URL
- `channelName`, `channelId`, `channelUrl`, `channelHandle` — channel details where the chart exposes them
- `artists` — performing artists
- `songwriters`, `producers` — credits where published
- `label` — record label for song charts
- `releaseDate` — music, trailer or podcast release date
- `primaryGenre`, `numEpisodes`, `lastUpdatedDate` — podcast-show details
- `chartViewCount` — views accumulated during the chart period
- `viewCount` — exact lifetime views when exact details are enabled
- `likeCount` — exact likes when exact details are enabled
- `commentCount` — exact comment count when comments are enabled and exact details are on
- `subscriberCount`, `subscriberCountText` — exact channel subscriber count when YouTube publishes one, plus the displayed text (which is rounded for large channels)
- `durationText`, `durationSeconds` — track, video or trailer duration
- `thumbnailUrl`, `thumbnails` — highest-resolution image and all available sizes
- `previousPosition`, `rankChange`, `periodsOnChart`, `viewsChangePercent`, `isNewEntry` — chart movement; `rankChange` is positive when an entry moved up
- `chartDate`, `chartType`, `chartPeriod` — chart date, requested chart and daily/weekly period
- `countryCode`, `countryName` — chart market
- `category` — `music`, `movies` or `podcasts`
- `market` — same country code as `countryCode`
- `sourceType` — `youtube_charts`
- `sourceName` — the chart slug, such as `topSongs`
- `sourceUrl` — the public chart page
- `rankSource` — `chart`
- `description`, `keywords`, `youtubeCategory`, `isShortsEligible`, `isFamilySafe` — added when exact details are enabled and YouTube exposes the player response; `description` can also come from the watch-next endpoint
- `publishedDate`, `publishedTimeText`, `isLive`, `liveStatus`, `scheduledStartTime`, `viewsPerHour` — publication and live status when available
- `badges` — badge labels where the source provides them
- `fallbackQuery` — reserved for labelled fallback rows; normally absent
- `scrapedAt` — UTC timestamp

## Output per category-hub video

Hub rows are individual videos read from a category page. They keep the same identity, channel, duration, thumbnail and provenance fields as chart rows, plus:

- `position` — page order
- `recordType` — `video`
- `type` — `video`
- `channelAvatarUrl` — channel avatar shown on the hub card
- `isVerified` — present when the channel carries a verified badge
- `viewCountText`, `publishedTimeText` — display text from the page
- `viewCount` — exact lifetime views when exact details are enabled, or when the hub shows an unabridged count
- `commentCount`, `subscriberCount`, `subscriberCountText` — added by exact details when YouTube publishes exact values
- `badges`, `isLive` — badges and live status from the page
- `category` — `gaming`, `news`, `sports`, `learning` or `courses`
- `countryCode`, `countryName` — hub market
- `market` — same country code as `countryCode`
- `sourceType` — `category_page`
- `sourceName` — `gaming`, `gamingLive`, `news`, `news_business`, `sports`, `learning` or `courses`
- `sourceUrl` — the public hub page
- `rankSource` — `page`
- `chartViewCount`, `chartDate`, `chartType`, `chartPeriod`, `previousPosition`, `rankChange`, `periodsOnChart`, `viewsChangePercent`, `isNewEntry` — not used for hub rows

## Output per status record

A status row explains a source that was skipped, unsupported or empty. It always carries `recordType: "status"`, `status`, `message`, `mode` and `scrapedAt`, plus the relevant `category`, `chartType`, `countryCode`, `market`, `period`, `date` and `resultCount` when known. Status values are `no_results`, `unsupported_country`, `unsupported_chart_period`, `retired` and `partial_source`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `charts` | `charts` for official rankings, `hubs` for category pages |
| `charts` | array | `["trendingVideos"]` | One or more chart types (mode=charts) |
| `categories` | array | `["gaming"]` | One or more category hubs (mode=hubs) |
| `newsSections` | array | `["top"]` | News tabs to read (mode=hubs, categories includes `news`) |
| `countries` | array | `["US"]` | One or more of the 68 chart markets, plus `global` where supported |
| `period` | string | `daily` | `daily` or `weekly` for charts that publish both |
| `date` | string | – | Historical date in `YYYY-MM-DD`; empty for the most recent chart |
| `maxItems` | integer | `100` | Total data rows across all sources (1–10,000) |
| `maxItemsPerChart` | integer | `100` | Rows per chart or hub feed (1–100) |
| `includeVideoDetails` | boolean | `true` | Fetch exact lifetime views, likes, dates and descriptions; player-only extras when available |
| `maxConcurrency` | integer | `5` | Parallel exact-detail requests (1–10) |
| `onlyNew` | boolean | `false` | Skip rows already emitted by the same monitor |
| `monitorName` | string | `default` | Separate only-new histories by name |

### Example: trending music videos in the United States

```json
{
  "mode": "charts",
  "charts": ["trendingVideos"],
  "countries": ["US"],
  "maxItems": 3,
  "includeVideoDetails": false
}
```

### Example: weekly top songs with history in Germany and the United Kingdom

```json
{
  "mode": "charts",
  "charts": ["topSongs"],
  "countries": ["DE", "GB"],
  "period": "weekly",
  "date": "2026-10-22",
  "maxItems": 100,
  "includeVideoDetails": true
}
```

### Example: gaming trending and live in Japan

```json
{
  "mode": "hubs",
  "categories": ["gaming", "gamingLive"],
  "countries": ["JP"],
  "maxItems": 50
}
```

### Example: top stories, business and technology news in the United States

```json
{
  "mode": "hubs",
  "categories": ["news"],
  "newsSections": ["top", "business", "technology"],
  "countries": ["US"],
  "maxItems": 60
}
```

## Use cases

- **Music-industry tracking** — follow top songs, artists and videos across markets and chart dates
- **Creator and label intelligence** — compare chart movement, periods on chart and view growth
- **Gaming and esports research** — capture the current Gaming trending and live line-up by country
- **Newsroom monitoring** — pull top stories and section feeds for one or more markets
- **Cross-market comparison** — run the same chart in several countries to compare regional taste
- **Trend and virality research** — combine exact lifetime views, publish dates and chart rank history

## Limitations and honest caveats

- **General Trending is gone.** YouTube retired the general Trending page and Trending Now list on 21 July 2025. `trendingVideos` is the official Trending **music** chart, not a general video feed. Legacy `category: "now"` inputs are mapped to it with a `retired` status row.
- **Exact details depend on YouTube's detail responses.** Views, likes, comment counts, subscriber counts and upload dates are filled from the player and the public watch-next endpoint. On some datacenter IPs YouTube strips the player response, so `youtubeCategory`, `keywords`, `isShortsEligible` and `isFamilySafe` may be omitted and `publishedDate` may be date-only. The listing row itself is never dropped.
- **Courses can be empty from some networks.** In some cloud environments YouTube serves no videos for `/courses` even though the page works elsewhere. The run returns a `no_results` status row; choose `learning` for a reliable editorial education feed.
- **Some Shorts songs have no video ID.** A small number of Shorts chart entries have no linked video, so those rows keep `trackId` and omit `url`.
- **Hype and some hubs are not available cookielessly.** Hype, shopping and podcast hubs, and a localised fashion hub return no usable rows. They are not shipped rather than filled with invented values.
- **Comments and subscribers are partial.** `commentCount` is exact when comments are enabled; it needs one extra comments-continuation request. `subscriberCount` is exact only when YouTube publishes an exact number — small channels do, while large channels publish rounded text. The displayed value is always kept in `subscriberCountText`.
- **Coverage is chart-specific.** Podcasts are published only in US, CA and MX. Shorts songs cover 22 markets plus global. Trending music videos and trailers are country-only. Top music videos, top songs, top artists and Shorts songs have a global ranking; the other charts do not.
- **History is chart-specific.** Weekly top music videos, top songs and top artists accept `date` back to 21 September 2017. Daily top music videos start on 6 November 2023. Shorts songs start on 2 November 2023 (weekly) or 6 November 2023 (daily). Trending music videos, trailers and podcasts return the current chart only. Dates before those floors, or after the latest published chart, return an `unsupported_chart_period` status row.
- **Charts are fixed lists.** YouTube returns about 30, 50–54 or 100 entries per chart (Shorts can return 51 in some markets) and does not expose pagination. Use `maxItems`/`maxItemsPerChart` and split by country, chart or date to cover more.
- **`viewsPerHour` is an average.** It is lifetime views divided by hours since upload, not live velocity. When only a date is available it is approximate by up to 24 hours.
- **`onlyNew` is bounded.** Each monitor name keeps up to 50,000 keys in its key-value store; older keys roll off.
- **This is not a keyword search actor.** Use the separate YouTube search actor for keyword discovery.

## FAQ

### What happened to YouTube's general Trending page?

YouTube retired the general Trending page and the Trending Now list on 21 July 2025. The `trendingVideos` chart returns YouTube's official Trending music chart, which is the current replacement. A legacy `category: "now"` input is mapped to that chart and the run adds a `retired` status row explaining the change.

### What is the difference between `charts` and `hubs`?

`charts` reads YouTube's official ranked lists with chart positions and movement. `hubs` reads editorial category pages such as Gaming trending, News, Sports, Learning and Courses. Hub order reflects the page layout, not an official chart rank, and `rankSource` tells you which one a row uses.

### Which charts work globally?

Top music videos, top songs, top artists and Shorts songs publish a global ranking. Trending music videos and trending movie trailers are country-only. Podcast shows are published only for the United States, Canada and Mexico.

### Which charts support historical dates?

Weekly top music videos, top songs and top artists accept a `date` back to 21 September 2017. Daily top music videos start on 6 November 2023, and Shorts songs start on 2 November 2023 (weekly) or 6 November 2023 (daily). Trending music videos, trending movie trailers and podcast shows return the current chart only.

### Are comment and subscriber counts exact?

`commentCount` is an exact integer when the video has comments and exact details are enabled. `subscriberCount` is an exact integer only when YouTube publishes one — this is common for small channels. Large channels publish rounded text such as `15.1M subscribers`, which is kept in `subscriberCountText` and never expanded into a fake exact number.

### Why is the Shorts chart a song chart?

YouTube's Shorts chart ranks songs used in Shorts, not individual Shorts videos. The actor labels those rows as `track` and keeps the chart honest rather than presenting a video ranking that does not exist.

### Why are some fields missing from a row?

Each chart and hub exposes a different field set. For example, artists have no video ID, podcasts have no lifetime view count, and live videos have no fixed duration. Missing values are omitted rather than filled with zero or null.

### Are the view and like counts exact?

`chartViewCount` is the views accumulated during the chart period. `viewCount` and `likeCount` are exact lifetime counters and appear when `includeVideoDetails` is enabled; a hub row can also carry `viewCount` when the page itself shows an unabridged count. The actor first asks YouTube's player, then the public watch-next endpoint, then the watch page. On some cloud IPs only the watch-next path is available, which still supplies exact views and likes but only a date (not a time) for `publishedDate`. Display text such as `1.2M views` is kept separately in `viewCountText` and is never expanded into a fake exact number.

### Do I need an API key, login or proxy?

No. The actor reads public YouTube chart data and public category pages without an account, API key, cookies or proxy configuration.

### Is this affiliated with YouTube?

No. This actor is an independent third-party tool and is not affiliated with, endorsed by or sponsored by YouTube or Google.
