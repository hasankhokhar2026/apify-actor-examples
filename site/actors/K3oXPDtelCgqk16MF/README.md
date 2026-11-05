# YouTube Channel Video Feed Quick Scraper

Point this actor at one or more YouTube channels and get back their current video list — newest, most popular or oldest first — plus the channel's own profile numbers, without opening a browser tab for each one. It's built for runs where you need a lot of channels processed quickly rather than every last enrichment field.

## What this actor does

- Accepts any mix of channel handles (`@name`), full channel URLs, or raw channel IDs across a single run
- Lists each channel's videos sorted newest, most popular, or oldest first, up to a per-channel cap
- Optionally also pulls the channel's About-page data (total views, join date, location, external links), Shorts tab, Playlists tab, and Live/Streams tab
- Returns a channel-info-only row (no video fields) when `maxVideos` is set to `0`, for lightweight profile lookups
- Localizes results to a market/country code, affecting what YouTube itself serves for that region
- Omits any field YouTube didn't expose for that video or channel — it never fills a gap with an empty string or a made-up value

## Output per video row

Every row carries one video's fields plus the full `authorMetadata` object for its channel.

- `videoId`, `title`, `url`
- `viewCount` — only when YouTube's own data exposes an exact integer; a rounded label like "93K views" stays in `viewCountText` and is never converted into a fake exact number
- `viewCountText`, `publishedTimeText`
- `duration` — may be the literal string `"LIVE"` for an ongoing stream; `durationSeconds` is only present once YouTube reports a finite length
- `thumbnailUrl`, `description`
- `isLive`, `isShort`
- `badges` — labels shown on the video tile, e.g. `["LIVE"]` or `["NEW"]`, when any apply
- `shorts[]`, `playlists[]`, `liveVideos[]` — only present when the matching `include...` input is on
- `scrapedAt`

### `authorMetadata` fields

- `channelId`, `channelName`, `handle`, `channelUrl`
- `description` — the channel's short header description
- `aboutDescription` — the longer description shown on the channel's About page, when `includeAbout` is on
- `subscriberCount` — only when YouTube's source data gives an exact integer; `subscriberCountText` always carries the displayed label (e.g. "466M subscribers")
- `videoCount`, `videoCountText` — same exact-vs-rounded distinction as subscribers
- `country`, `location` — `location` and `totalViews`/`totalViewsText`/`joinedDateText` come from the About page (`includeAbout`)
- `joinedDateText`, `totalViews`, `totalViewsText`
- `externalLinks[]` — links listed on the About page (`includeAbout`); `channelLinks[]` — links shown directly on the channel header
- `rssUrl`, `avatarUrl`, `bannerUrl`
- `isVerified`, `isFamilySafe`
- `isOfficialArtistChannel` — only present when the channel carries YouTube's official-artist badge
- `keywords[]`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `channelUrls` | array | – | Channel URLs, handles or channel IDs, any mix |
| `maxVideos` | integer | `50` | Max videos per channel (0–10000); `0` returns channel info only |
| `sortVideosBy` | string | `newest` | `newest`, `popular` or `oldest` |
| `includeAbout` | boolean | `true` | Pull total views, join date, location and external links from the About page |
| `includePlaylists` | boolean | `false` | Include the channel's Playlists tab |
| `maxPlaylists` | integer | `20` | Max playlists to return when `includePlaylists` is on (1–500) |
| `includeShorts` | boolean | `false` | Include the channel's Shorts tab |
| `maxShorts` | integer | `20` | Max Shorts to return when `includeShorts` is on (1–2000) |
| `includeLiveVideos` | boolean | `false` | Include the channel's Live/Streams tab |
| `maxLiveVideos` | integer | `20` | Max live/stream videos to return (1–500) |
| `market` | string | `US` | Country code controlling localized content (one of 31 supported) |

### Example: a few channels' latest uploads

```json
{
  "channelUrls": ["@Apify", "@mkbhd"],
  "maxVideos": 10,
  "sortVideosBy": "newest"
}
```

### Example: most popular videos with full channel profile data

```json
{
  "channelUrls": ["@Fireship"],
  "maxVideos": 20,
  "sortVideosBy": "popular",
  "includeAbout": true
}
```

### Example: channel profile only, no videos

```json
{
  "channelUrls": ["@mrbeast"],
  "maxVideos": 0
}
```

### Example: including Shorts and playlists

```json
{
  "channelUrls": ["@mkbhd"],
  "maxVideos": 25,
  "includeShorts": true,
  "maxShorts": 15,
  "includePlaylists": true,
  "maxPlaylists": 10
}
```

## Use cases

- **Bulk channel monitoring** — track upload activity across a long list of channels on a recurring schedule
- **Competitor benchmarking** — compare view counts and posting cadence across several creators in a niche at once
- **Influencer shortlisting** — pull subscriber counts and verification status for a batch of candidate channels
- **Content inventory** — build a catalog of a channel's videos, Shorts and playlists for cataloging or archival
- **Growth tracking** — re-run on a schedule to watch subscriber and view counts change over time

## FAQ

**Is a YouTube API key needed?**
No — this actor reads YouTube's own public channel and video pages and needs no API key or login.

**Which channel reference formats work?**
A `@handle`, a full `/channel/UC...` URL, a full `@handle` URL, or a raw channel ID all resolve to the same channel — use whichever you already have.

**Can it reach private or members-only channels?**
No, only publicly accessible channels are supported; content requiring a logged-in session isn't reachable.

**Why is `viewCount` sometimes missing even though `viewCountText` shows a number?**
YouTube's video-card label is often rounded (e.g. "93K views"). This actor only fills `viewCount` when the underlying data gives an exact figure, rather than reverse-engineering an approximate one.

**Why would `duration` show `"LIVE"` with no `durationSeconds`?**
That's an ongoing live stream — its length isn't final yet, so there's nothing finite to report until the broadcast ends.

**How fresh is the data?**
Every run reads the channel live, so results reflect whatever YouTube is currently showing — there's no caching layer.

**Does `market` change which videos are returned?**
It sets the country/language context YouTube uses when rendering the page, which can affect things like localized text and regionally restricted content, not which channel you're looking at.

**Can I fetch 5,000+ videos from one channel?**
Yes — `maxVideos` goes up to 10,000; the actor keeps paging through the channel's video list until it reaches your cap or runs out of videos.
