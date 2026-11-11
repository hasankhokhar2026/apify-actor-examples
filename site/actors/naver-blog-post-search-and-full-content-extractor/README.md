# Naver Blog Post Search & Full Content Extractor

Naver Blog is South Korea's largest blogging platform, and its posts hold first-hand reviews, local guides, recipes, and daily-life writing that rarely appear elsewhere. This actor searches Naver Blog by keyword, walks an entire public blog archive, or fetches a list of post URLs — returning clean post records with exact publish times, full text, images, tags, categories, and places.

No Naver account, login, API key, or proxy setup is required.

## What this actor does

- **Three modes:** `search` for keyword discovery, `blogPosts` for a blog's public archive, and `postDetails` for exact URLs.
- **Multiple targets per run:** search up to 50 keywords and read up to 50 blog IDs in one run, with duplicates removed across queries.
- **Real sorting and date filters:** relevance or newest-first, plus last hour/day/week/month/3 months/6 months/year and custom `YYYY-MM-DD` ranges.
- **Full posts, not snippets:** optional content enrichment adds the complete body, exact publish time, images, thumbnail, tags, category, and Naver Map places.
- **Exact publish times:** `publishedAt` is the post's real timestamp in Korea Standard Time (UTC+9), while `publishDateText` preserves what Naver displayed.
- **Reactions and comments:** like counts, reaction breakdowns, and optional comment counts and paginated comment threads (up to `maxComments` per post).
- **Empty fields are omitted:** every record is cleaned recursively, so absent data is never returned as `null`, `""`, or `[]`.

## Output per post

| Field | Description |
|---|---|
| `title` | Post title, HTML removed |
| `summary` | Search snippet or the post page's description |
| `authorName` | Author's display name |
| `authorUrl` | Author profile link, when Naver exposes one |
| `blogName` | Name of the blog |
| `blogId` | Blog identifier, e.g. `travel_lover` |
| `blogUrl` | Blog home URL |
| `postUrl` | Canonical post URL |
| `publishDate` | Publish date in `YYYY-MM-DD` format (KST) |
| `publishedAt` | Exact publish time as ISO 8601 with `+09:00` (content enrichment only) |
| `publishDateText` | Date as Naver displayed it, e.g. `2주 전` or `2026. 10. 23. 11:10` |
| `category` | Blog category name (content enrichment only) |
| `tags` | Hashtags found on the post (content enrichment only) |
| `images` | Full-size content image URLs (content enrichment only) |
| `imageCount` | Number of images in `images` |
| `thumbnail` | Representative image for the post |
| `places` | Naver Map places mentioned in the post (content enrichment only) |
| `hasVideo` | `true` when the post contains a video (only present when true) |
| `isSelfPurchased` | `true` when Naver shows its structured self-purchased review disclosure (내돈내산) |
| `content` | Complete post text, never truncated (content enrichment only) |
| `contentHtml` | Post body HTML, only when `includeHtml` is on |
| `contentLength` | Character count of `content` |
| `rank` | 1-based organic position for the query that found the post (`search` only) |
| `searchQuery` | First query that found the post (`search` only) |
| `matchedQueries` | Every processed query that found the post (`search` only) |
| `commentCount` | Total comments including replies; from the blog list or `includeComments` |
| `comments` | Comment threads up to `maxComments` (default 100), fetched in pages of 100, only when `includeComments` is on |
| `likeCount` | Main "like" (공감) count when Naver publishes it (content enrichment only) |
| `reactionCounts` | Counts by reaction type (`like`, `impressive`, `thanks`, `wow`, `haha`, `sad`) when Naver publishes them |
| `recordType` | Always `"blogPost"` |
| `scrapedAt` | UTC timestamp when the record was scraped |

Each place in `places` contains `name`, `address`, `latitude`, `longitude`, `phone`, `placeId`, and `bookingUrl`, with empty values omitted.

With `includeContent` off, search and blog-archive records contain list-level fields only: title, summary, author, blog, URLs, `publishDateText`, and the date when Naver shows an absolute date. `postDetails` always fetches the post page because that is the mode's purpose.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string (required) | `search` | `search`, `blogPosts`, or `postDetails` |
| `searchQueries` | array of strings | `["제주도 여행"]` | Keywords to search (mode=search); max 50 |
| `blogIds` | array of strings | – | Blog IDs or blog URLs (mode=blogPosts); max 50 |
| `postUrls` | array of strings | – | Post URLs to fetch (mode=postDetails); desktop, mobile, PostView, or `blogId/logNo` |
| `sortBy` | string | `sim` | `sim` for relevance, `date` for newest first (mode=search) |
| `publishedWithin` | string | `all` | `all`, `1h`, `1d`, `1w`, `1m`, `3m`, `6m`, `1y`, or `custom` (mode=search) |
| `dateFrom` | string | – | Start date `YYYY-MM-DD` for a custom range (mode=search) |
| `dateTo` | string | – | End date `YYYY-MM-DD` for a custom range (mode=search) |
| `categoryNo` | integer | `0` | Blog category number; `0` means every category (mode=blogPosts) |
| `maxItems` | integer | `20` | Hard cap on emitted records across all targets (1–10,000) |
| `includeContent` | boolean | `true` | Fetch each post page for full text and detail fields |
| `includeHtml` | boolean | `false` | Add `contentHtml`; turns content enrichment on |
| `includeComments` | boolean | `false` | Add `commentCount` and comment threads up to `maxComments`; turns content enrichment on |
| `maxComments` | integer | `100` | Maximum comments returned per post with `includeComments` (1–1,000) |
| `maxConcurrency` | integer | `3` | Parallel post-page requests when enriching content |

### Example: Korean keyword search, newest first

```json
{
  "mode": "search",
  "searchQueries": ["제주도 여행"],
  "sortBy": "date",
  "publishedWithin": "all",
  "maxItems": 50,
  "includeContent": true
}
```

### Example: several queries with a custom date range

```json
{
  "mode": "search",
  "searchQueries": ["K-beauty routine", "올리브영 추천"],
  "sortBy": "sim",
  "publishedWithin": "custom",
  "dateFrom": "2026-01-01",
  "dateTo": "2026-03-31",
  "maxItems": 200,
  "includeContent": false
}
```

### Example: a blog's full archive in one category

```json
{
  "mode": "blogPosts",
  "blogIds": ["ranto28"],
  "categoryNo": 17,
  "maxItems": 500,
  "includeContent": true,
  "includeHtml": false
}
```

### Example: full details for known posts

```json
{
  "mode": "postDetails",
  "postUrls": [
    "https://blog.naver.com/e_s_l/224451062514",
    "https://m.blog.naver.com/ranto28/224461024209",
    "https://blog.naver.com/PostView.naver?blogId=hoyaaaaa-&logNo=224458179821"
  ]
}
```

## Search limits and blog archives

Naver returns at most **1,000 posts per keyword search**. This is a source-side ceiling, not an actor setting. To collect more:

- split a broad topic into narrower queries;
- use `publishedWithin` presets or a custom `dateFrom`/`dateTo` window and run several windows;
- deduplicate with `postUrl` — the actor already removes duplicates inside a run.

Blog archives use a different source and are **not limited to 1,000 posts**: a public blog with 2,700 posts can return all 2,700. Search results are likely to repeat across pages, so deduplication is applied by canonical post URL.

Comment counts are included when Naver exposes them: from the blog list in `blogPosts` mode, or from the post page when `includeComments` is on. Likes (`likeCount` and `reactionCounts`) come from Naver's public reaction service and are omitted for posts with no reactions. With `includeComments`, `comments` returns up to `maxComments` per post (default 100, fetched in pages of 100) including replies when Naver returns them; `commentCount` is always the full total, so a post can have more comments than rows in `comments`.

### Limitations

- **Search ceiling:** Naver accepts search start positions up to 1,000, so one query exposes roughly a 1,000-result window; after deduplication a run can return fewer. Split by date or query for more.
- **Comment cap:** Naver serves comment pages cookielessly; the actor pages through them up to `maxComments` per post (default 100, max 1,000) to keep output and request cost bounded. `commentCount` still reports the full total. Increase the cap if you need more rows. Posts with comments disabled return neither field.
- **Not shipped (scope decisions, not source limits):** blogger profile totals (neighbors, visitors, post count), cafe/news article search, paid-sponsorship classification, and incremental only-new state. Profile and cafe/news data are reachable on separate Naver surfaces but are outside this post-oriented actor; paid sponsorship has no ground-truth label and remains a text heuristic for users; incremental state is an implementation choice, and date windows plus `postUrl` dedupe cover the same workflow. Self-purchased reviews are labeled by Naver and are exposed as `isSelfPurchased`.
- **Private, deleted, or members-only posts** are skipped; one bad post does not fail the run.
- **Search relevance** is Naver's own ranking, including Korean results for English queries; the actor does not re-rank.
- **Markup changes:** Naver redesigns can require a parser update. The actor ships fixtures and status messages instead of failing silently.

## Use cases

- **Consumer research** — collect how Korean bloggers describe a product, brand, or store before a launch.
- **Influencer and blog discovery** — find active blogs in K-beauty, food, travel, parenting, or finance.
- **Brand monitoring** — track mentions across the Korean blogosphere, then filter by exact publish date.
- **Content and trend analysis** — measure post volume and topic shifts across date windows.
- **Local travel research** — gather first-hand restaurant, cafe, and itinerary write-ups with mapped places.
- **Archive and migration** — export a public blog's full post history, including text and image URLs.

## FAQ

**Do I need a Naver account or API key?**
No. The actor reads public Naver Blog pages. There is no login, key, or proxy configuration to provide.

**Can I search in Korean and English?**
Yes. Korean, English, and mixed queries all work. Results are mostly Korean-language blogs because that is what Naver Blog contains.

**How do I find a blog ID?**
Use the segment right after `blog.naver.com/`. For `https://blog.naver.com/travel_lover`, the blog ID is `travel_lover`. The actor also accepts the full blog URL or `@travel_lover`.

**Why do some posts have no `content`, `images`, or `publishedAt`?**
Those fields come from the post page, so they require `includeContent`. They are also omitted for empty-body posts, private or deleted posts, and text-only posts with no images or places.

**What is the difference between `publishDate` and `publishedAt`?**
`publishDate` is the date in `YYYY-MM-DD` format. `publishedAt` is the exact timestamp with a `+09:00` offset. `publishDateText` keeps the original wording, which may be relative such as `3일 전`.

**Why did a keyword return fewer posts than expected?**
Naver caps one keyword at 1,000 results and may return fewer for narrow queries. Add more queries or split the period into smaller date windows.

**Why are there no likes or comments on some posts?**
Naver's reaction and comment services are public but conditional: posts with no reactions omit `likeCount`/`reactionCounts`, and posts with comments disabled omit `commentCount`/`comments`. Set `includeComments=true` to request comments; `commentCount` is the total and `comments` holds up to `maxComments` rows (default 100, paginated 100 at a time).

**What does `isSelfPurchased` mean?**
It is `true` only when Naver itself shows the structured self-purchased review disclosure (내돈내산) on the post. It is not a paid-sponsorship classifier; `협찬`/`광고` wording remains in `content` for your own rules.

**What happens to private, deleted, or blocked posts?**
They are skipped with a log message. One missing post does not fail the run. If every target is invalid, the run finishes with a status message explaining what to check.

**Can I fetch more than 10,000 posts?**
`maxItems` is capped at 10,000 per run. For larger archives, split the work into separate runs and deduplicate by `postUrl`.

**Is this affiliated with Naver?**
No. This is an independent third-party actor that reads public Naver Blog pages. It is not affiliated with, endorsed by, or sponsored by Naver Corporation.
