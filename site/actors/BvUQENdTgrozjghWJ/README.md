# TikTok Explore Feed Trending Post Scraper

TikTok's Explore tab surfaces whatever its discovery system is currently amplifying, broken out by content category. This actor paginates that feed for one or more categories and returns each trending post with its engagement stats, author snapshot, sound, and video details. Category 123 ("All") works without any extra configuration; an auto-discovery option tries to read the other category IDs from the live Explore page.

## What this actor does

- Accepts a list of category objects (`id` + `name`) and paginates TikTok's Explore feed for each one
- Tags every post with `feedType`, `categoryId`, and `categoryName` so results from multiple categories stay distinguishable
- Deduplicates posts that surface in more than one category so each video is only emitted once per run
- Can try to discover more category IDs by clicking the category tabs on TikTok's live Explore page
- Category 123 ("All") is the default and needs no extra setup
- Fields a post doesn't have (e.g. no detected caption language) are omitted rather than returned empty

## Output per post

- `feedType` — always `explore`
- `categoryId`, `categoryName` — the category this post was collected from (see the FAQ on category IDs)
- `postId`, `postType` (`video` or `slideshow`), `postUrl` — post identity
- `caption`, `textLanguage` — caption text and its detected language
- `locationCreated` — the region code TikTok attaches to the post, when present
- `createTime`, `createdAt` — publication time as a Unix timestamp and ISO 8601 date
- `playCount`, `likeCount`, `commentCount`, `shareCount`, `collectCount`, `repostCount` — engagement counts
- `isAd` — whether the post is marked as an advertisement
- `stitchEnabled`, `duetEnabled`, `shareEnabled` — creator-controlled interaction permissions
- `author.id`, `author.secUid` — author's TikTok IDs
- `author.username`, `author.displayName`, `author.bio` — author profile text
- `author.verified`, `author.privateAccount` — author account flags
- `author.roomId` — present when TikTok reports a live room for the author
- `author.avatarUrl` — author avatar image URL
- `author.followerCount`, `author.followingCount`, `author.heartCount`, `author.videoCount` — author stats snapshot
- `music.id`, `music.title`, `music.authorName`, `music.original`, `music.duration`, `music.album` — sound details
- `music.playUrl`, `music.coverUrl` — sound audio and cover URLs
- `video.width`, `video.height`, `video.duration`, `video.ratio` — video technical metadata
- `video.playUrl`, `video.cover` — signed video stream and cover image URLs
- `mediaUrlExpiresAt` — ISO 8601 timestamp when the signed media URLs expire, when it can be read from the URL
- `images` — slideshow image objects (`ordinal`, `width`, `height`, `urlList`), for `postType: "slideshow"` posts
- `hashtags` — array of hashtag objects with `name`, plus `id` and `isCommerce: true` when TikTok supplies them
- `mentions` — array of `{username, start, end}` objects marking caption offsets (with `awemeId` when present)

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `categories` | array | `[{"id": 123, "name": "All"}]` | Category objects with numeric `id` and human-readable `name`. |
| `maxItemsPerCategory` | integer | `50` | Maximum trending posts to collect per category (1–500). |
| `maxItems` | integer | – | Alias for `maxItemsPerCategory`. When set, it is used unless `maxItemsPerCategory` is set to a value other than `50`. |
| `categoryId` | integer | – | Shorthand for a single category. When set, it replaces the `categories` list entirely. |
| `autoDiscoverCategories` | boolean | `false` | Click through the category tabs on TikTok's Explore page and add every category ID found to the list. If none are found, the All category is used. |

### Example: default All-category feed

```json
{
  "categories": [{"id": 123, "name": "All"}],
  "maxItemsPerCategory": 10
}
```

### Example: multiple specific categories

```json
{
  "categories": [
    {"id": 123, "name": "All"},
    {"id": 4, "name": "Entertainment"},
    {"id": 9, "name": "Sports"}
  ],
  "maxItemsPerCategory": 50
}
```

### Example: auto-discover all categories

```json
{
  "categories": [],
  "autoDiscoverCategories": true,
  "maxItemsPerCategory": 30
}
```

## Use cases

- **Trend analysts** — monitor which video formats and topics are surfacing on TikTok's Explore feed each day
- **Content strategists** — identify high-performing content styles within specific categories like Sports or Entertainment
- **Brand safety teams** — review what trending content is appearing in categories near planned ad placements
- **Academic researchers** — build time-series datasets of trending TikTok content for algorithmic studies
- **Media benchmarking** — track which creators and formats are being amplified by TikTok's discovery system
- **Trend dashboards** — feed breakout content into a notification system that flags momentum early

## FAQ

**What is category 123?**
Category 123 is TikTok's "All" Explore feed — the default tab showing trending posts across all content types, and the recommended starting point. If none of the IDs you ask for match the feed TikTok actually loads on the Explore page, the actor switches to the ID TikTok served, so `categoryId` on the records can differ from the one you entered (your `categoryName` label is kept).

**How do I find other category IDs?**
Set `autoDiscoverCategories` to `true`. The actor clicks each category tab on TikTok's live Explore page and records the ID behind it; the run log lists what it found, so you can reuse those IDs in later runs. Discovery is best-effort: if TikTok's page layout doesn't expose the tabs, only the All category is scraped.

**Do posts get deduplicated across categories?**
Yes. If the same video appears in more than one requested category, it's only emitted once in the dataset.

**How many posts can I get per category?**
Up to 500 per category, set via `maxItemsPerCategory`. A category stops earlier when TikTok reports no more posts or a whole page contains only posts already collected. With a very small limit, the first page TikTok returns is saved in full, so a category can come out a few posts over the limit.

**Do I need login or cookies?**
No. There are no login or cookie inputs.

**Do the video URLs expire?**
Yes. TikTok signs video and audio URLs with short-lived tokens. `mediaUrlExpiresAt` tells you exactly when they expire, so download or cache anything you need promptly.

**Can I use this to monitor trending content over time?**
Yes. Schedule recurring runs and compare `categoryId`, `postId` and the engagement counts between runs to see how the feed shifts over time.

**Is this affiliated with TikTok?**
No. This is an independent, third-party actor that reads TikTok's publicly viewable Explore feed; it isn't affiliated with or endorsed by TikTok.
