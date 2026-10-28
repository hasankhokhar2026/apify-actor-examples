# YouTube Trending Feed Extractor by Category & Market

Pull video lists for YouTube's Gaming, Music, News, Movies and main Trending sections in any of 31 regional markets, with position, channel, view count, duration and thumbnail for each entry, and a clear label on rows that came from a fallback search.

## What this actor does

- Tries YouTube's Gaming, Music, News and main Trending pages first
- Uses a labeled public YouTube search instead when a page can't be read (always for Movies, and for Gaming when the page lists fewer than 10 items), marking every row with `sourceType` and the `fallbackQuery` used
- Targets any of 31 regional markets so results reflect what's trending in that country
- Captures playlists and albums alongside individual videos when a category page shows them, and removes duplicates
- Omits any field that has no value for a given row rather than returning null

## Output per item

| Field | Description |
|---|---|
| `position` | Order in the returned list (page order for category pages, search order for search-fallback rows) |
| `type` | `video`, `playlist`, or `album` |
| `videoId` | YouTube video ID, for video rows |
| `playlistId` | YouTube playlist/album ID, for playlist or album rows |
| `url` | Link to the video or playlist |
| `title` | Video or playlist title |
| `channelName` | Channel display name |
| `channelId` | Channel's YouTube ID, when resolved |
| `channelUrl` | Full channel URL, when resolved |
| `channelHandle` | Channel's @handle, when available |
| `isVerified` | Whether the channel shows a verified badge (video rows only) |
| `viewCount` | View count as a number, when parseable |
| `viewCountText` | View count exactly as displayed, e.g. "3.2M views" |
| `publishedTimeText` | Relative publish time as displayed, e.g. "2 days ago" |
| `publishedDate` | Upload date, when it can be read from the video's own page (video rows) |
| `durationText` | Duration as displayed, e.g. "12:34" |
| `durationSeconds` | Duration converted to seconds |
| `thumbnailUrl` | Highest-resolution thumbnail URL available |
| `badges` | Badge labels shown on the item, e.g. "4K", "CC" |
| `isLive` | Whether the item is a live stream |
| `category` | The input category used for this run |
| `market` | The regional market used for this run |
| `sourceType` | `category_page` when read directly, or `search_fallback` when a fallback search was used |
| `fallbackQuery` | The search query used, only present when `sourceType` is `search_fallback` |
| `scrapedAt` | UTC timestamp of when the record was scraped |

**Status rows:** if a run finds nothing, the dataset gets a single status row instead of video rows. For `category: "now"` when even the search fallback fails, that row is `{success: false, category, market, sourceType: "auth_required", error, scrapedAt}`. For any other category with no results, it is `{recordType: "status", status: "no_results", category, market, resultCount: 0, scrapedAt}`. Filter these out by checking for `videoId`/`playlistId`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `category` | string | `gaming` | Trending section to read: now (main Trending feed), gaming, music, movies, or news |
| `maxResults` | integer | `50` | Maximum number of items to return (1–200) |
| `market` | string | `US` | Regional market (31 options), e.g. US, GB, CA, AU, DE, FR, JP, KR, BR, IN, MX. It sets the region and interface language used for the page or search |

### Category notes

- `gaming` reads the YouTube Gaming page; if that page shows fewer than 10 items, a search for "gaming" is used instead.
- `news` reads the YouTube News page's shelves; if they can't be read, it searches "latest news" (then "world news").
- `music` reads the YouTube Music channel's playlists and videos; if they can't be read, it searches "official music video" (then "new music").
- `now` tries the main Trending page, which usually needs a signed-in session; when it's unavailable, it searches "trending videos" (then "popular videos").
- `movies` always uses a search for "new movie trailer <current year>" (then "official movie trailer").

Search-fallback rows are ordinary search results for that phrase in the chosen market, not YouTube's own trending ranking.

### Example: gaming trending in Japan

```json
{
  "category": "gaming",
  "maxResults": 20,
  "market": "JP"
}
```

### Example: main trending feed, US

```json
{
  "category": "now",
  "maxResults": 50,
  "market": "US"
}
```

### Example: music trending in Brazil

```json
{
  "category": "music",
  "maxResults": 20,
  "market": "BR"
}
```

## Use cases

- **Daily trend monitoring** — schedule runs to track what's rising in Gaming or Music each day
- **Content strategy** — see which video lengths, formats and titles are performing well right now
- **Competitive and creator intelligence** — spot which channels keep appearing across trending categories
- **Cross-market comparison** — run the same category across several `market` values to compare regional trends
- **News-cycle tracking** — use `news` to capture the day's top-story videos

## FAQ

**Why do some rows say `search_fallback`?**
YouTube's main Trending feed and the Movies channel aren't available without signing in, and the other category pages sometimes can't be read either. Rather than returning nothing, the actor runs a public search instead and marks every resulting row with `sourceType: "search_fallback"` plus the `fallbackQuery` it used, so you always know where a row came from. Rows read from the category page itself carry `sourceType: "category_page"`.

**How many items can one run return?**
Up to `maxResults` (200 max). The real number depends on how many items the category page or fallback search shows on the day, after duplicates are removed.

**What does `market` actually change?**
It sets YouTube's region and interface language for the category page or fallback search, so results lean towards that country instead of a global default.

**Are playlists and albums included, or only videos?**
Category pages that show ranked playlists or albums alongside videos will include them, distinguished by the `type` field (`video`, `playlist`, or `album`); `playlistId` is only present on non-video rows.

**Are live streams included?**
Yes. Live items are flagged with `isLive: true` and usually carry a "LIVE" badge in `badges`.

**Why are fields like `durationText` or `publishedTimeText` missing from some rows?**
Live streams don't have a fixed duration or publish time yet, so those fields are left out of that row rather than filled with a placeholder.

**Is this affiliated with YouTube?**
No. This actor reads YouTube's public pages and is not affiliated with, endorsed by, or sponsored by YouTube or Google.
