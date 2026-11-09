# Reddit Keyword Search with Advanced Filters

Search Reddit for one or more keywords and get back matching posts plus optional keyword-matched comments, narrowed down with subreddit allow/block lists, a minimum score, a relative or absolute date window, an NSFW toggle, and an author blocklist.

Reddit's anonymous old.reddit and public JSON endpoints are blocked, so this actor uses a multi-source transport with explicit provenance instead of pretending a blocked page was an empty successful run.

## What this actor does

- Runs a separate search for each keyword and tags every record with the keyword that found it
- Uses a source cascade: Google Translate `community-more-posts` partial (subreddit-scoped live listing), Reddit RSS `search.rss?type=link` (global/subreddit search), Redlib (search, comment search, opaque cursors), Arctic Shift archive (backfill/hydration), and an optional user-supplied OAuth token
- Adds `source`, `sourceUrl`, `retrievedAt`, `dataFreshness`, `scoreAsOf`, `upvoteRatioAsOf` and `archiveLagSeconds` to every record so live metrics are never confused with archive snapshots
- Searches comment bodies with `searchComments` via Redlib, with RSS `type=comment` parent discovery plus hydration as fallback
- Supports `onlyNew` + `monitorId` watermarks for scheduled monitoring, including relative windows (`hour` … `all`)
- Applies subreddit, score, age, date range, NSFW, author and multi-keyword AND filters
- Does not treat unknown NSFW flags or missing score metrics as safe/passing; it emits a typed status instead
- De-duplicates posts by `t3_id` and comments by `t1_id` across keywords and sources, merging provenance and preferring live metrics over archive snapshots
- Fails loudly when every source fails; a working source with zero matches emits `no_results`, not an error
- **Empty fields are omitted:** never null, empty strings or empty arrays/objects

## Output records

### Post records (`recordType: "post"`)

Legacy fields are preserved: `keyword`, `post_id`, `post_name`, `title`, `author`, `author_fullname`, `subreddit`, `subreddit_prefixed`, `content`, `score`, `num_comments`, `url`, `permalink`, `external_url`, `thumbnail_url`, `link_flair`, `created_utc`, `created_at`, `is_self`, `is_stickied`, `is_nsfw`, `is_spoiler`, `is_promoted`, `is_original_content`, `gilded_count`, `num_crossposts`, `crosspost_parent`, `post_hint`, `title_word_count`, `post_age_seconds`.

Added fields include: `keywords`, `upvote_ratio`, `source`, `sourceUrl`, `retrievedAt`, `dataFreshness`, `scoreAsOf`, `upvoteRatioAsOf`, `archiveLagSeconds`, `metricsAvailable`, `isNsfwKnown`, `isGallery`, `galleryItems`, `mediaUrls`, `videoUrl`, `removedByCategory`, `removalType`, `wasDeletedLater`, `subreddit_id`, `postType` and `provenance`.

`subreddit` is the bare name (`Python`); `subreddit_prefixed` is `r/Python`. `domain` is the linked domain for link posts. Every pushed record also carries `scrapedAt` (the run timestamp) in addition to source provenance.

### Comment records (`recordType: "comment"`)

`keyword`, `keywords`, `commentId`, `comment_id`, `post_id`, `link_id`, `parentId`, `depth`, `body`, `author`, `author_fullname`, `subreddit`, `subreddit_prefixed`, `score`, `created_utc`, `created_at`, `permalink`, `isSubmitter`, `stickied`, `distinguished`, `scoreHidden`, `edited`, `collapsed`, `source`, `sourceUrl`, `retrievedAt`, `dataFreshness`, `scoreAsOf` and `provenance`.

### Status/error records (`recordType: "status"` or `"error"`)

Emitted when sources partially fail, are rate-limited, return no results, cannot supply a requested metric/NSFW flag, or when every source fails. They include `reason`, `message`, `keywords`, `sources`, `attemptedSources`, `counts`, `appliedFilters`, `sourceFailures` and `retryAfterSecs`.

Typed reasons include: `invalid_input`, `all_sources_failed`, `transport_blocked`, `login_required`, `challenge_required`, `rate_limited`, `source_timeout`, `source_unavailable`, `metrics_unavailable`, `nsfw_status_unavailable`, `all_filters_dropped_results`, `partial_results` and `no_results`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `keywords` | array | – | Keywords to search; each runs as its own search (required) |
| `resultLimit` | integer | `100` | Max posts per keyword (1-1000). Source caps are real: RSS 100/request, Translate 24/page, Redlib 7/page, Arctic 100/page |
| `sort` | string | `relevance` | `relevance`, `hot`, `top`, `new`, or `comments` |
| `relativeWindow` | string | `all` | `hour`, `day`, `week`, `month`, `year`, or `all` |
| `onlyNew` | boolean | `false` | Emit only records newer than the stored watermark |
| `monitorId` | string | – | Stable key for the onlyNew watermark/seen IDs |
| `searchComments` | boolean | `false` | Search comment bodies and emit `recordType=comment` records |
| `commentLimit` | integer | `50` | Max matching comments per keyword |
| `subredditFilter` | array | `[]` | Only keep posts/comments from these subreddits (with or without `r/`) |
| `subredditBlocklist` | array | `[]` | Drop posts/comments from these subreddits |
| `minScore` | integer | – | Drop records below this score; skipped/reported when no reliable score is available |
| `maxAgeDays` | integer | – | Drop records older than N days |
| `excludeNsfw` | boolean | `false` | Drop NSFW records; unknown flags are reported, not silently passed |
| `authorBlocklist` | array | `[]` | Drop these usernames (case-insensitive) |
| `keywordRequireAll` | boolean | `false` | With multiple keywords, keep only records containing all of them |
| `dateFrom` | string | – | Earliest `created_at` (inclusive, `YYYY-MM-DD` or ISO) |
| `dateTo` | string | – | Latest `created_at` (inclusive end-of-day) |
| `includeArchive` | boolean | `true` | Use Arctic Shift for subreddit backfill/comment hydration |
| `redditOAuthToken` | secret | – | Optional user OAuth Bearer token; never required |
| `redlibInstances` | array | `[]` | Optional Redlib hostnames in priority order |
| `resolveChallenges` | boolean | `true` | Best-effort Playwright solve for Redlib Anubis challenges |
| `proxyConfiguration` | object | – | Optional Apify proxy configuration |

### Example: single keyword, top posts

```json
{
  "keywords": ["machine learning"],
  "resultLimit": 100,
  "sort": "top",
  "relativeWindow": "month"
}
```

### Example: brand monitoring with only-new watermarks

```json
{
  "keywords": ["mybrand", "mybrand review"],
  "resultLimit": 100,
  "sort": "new",
  "onlyNew": true,
  "monitorId": "mybrand-daily",
  "relativeWindow": "day",
  "excludeNsfw": true
}
```

### Example: subreddit-scoped comments

```json
{
  "keywords": ["layoffs"],
  "subredditFilter": ["technology", "cscareerquestions"],
  "searchComments": true,
  "commentLimit": 50,
  "maxAgeDays": 30,
  "resultLimit": 50
}
```

## Source behavior and limits

- **Translate partial**: live, subreddit-scoped listing; 24 posts/page with opaque cursors; keyword matching is client-side on title/body. No per-post NSFW/locked/spoiler flags. All gallery images found in the post element are exposed through `mediaUrls`/`galleryItems`.
- **Reddit RSS**: live global/subreddit search; max 100 entries per request, no pagination, roughly one request per minute per IP, and no score/comment/ratio metrics. Expected to be retired by Reddit.
- **Redlib**: live third-party front-end; 7 posts / 10 comments per page with opaque cursors; Anubis challenges and upstream rate limits are common. This is the primary cookieless comment-body search. Default instances are `redlib-1.privadency.com` and `red.artemislena.eu`; override with `redlibInstances`.
- **Arctic Shift**: archive, not a monitor. Scoped keyword searches may return HTTP 422 “Timeout”; score/comment/ratio values are snapshots (`dataFreshness` and `scoreAsOf` say which). Used for subreddit-scoped backfill/hydration and as the third comment-body rung via `comments/search?subreddit=...&body=...`.
- **OAuth**: only when you supply a token; the actor never obtains one. `oauth.reddit.com` without a token returns a login/block page, so there is no fake “cookieless OAuth”.

### Hard limits (2026-11)

- **old.reddit.com**: anonymous requests redirect to a login wall (`/login/?reason=lor2`). The actor does not use old.reddit.
- **Reddit RSS retirement**: RSS search is scheduled to stop on **2026-11-13**. Until then it is best-effort; afterwards global live search depends on Redlib and the intermittent Translate path.
- **Global Arctic search**: `posts/search?query=` and `comments/search?body=` without `subreddit`, `author`, `link_id`, or `parent_id` return HTTP 400. Global keyword/comment search cannot use Arctic; only subreddit-scoped archive queries are supported.
- **Arctic archive staleness**: scores, comment counts, upvote ratios and removal flags are snapshots, not live. Check `dataFreshness`, `scoreAsOf`, `upvoteRatioAsOf` and `archiveLagSeconds` before treating archive engagement as current; removed/deleted flags may lag live Reddit state.
- **Legal/ToS**: Reddit requires approved API access and prohibits unapproved scraping and commercialization. Arctic Shift, Redlib and the Translate proxy are third-party services and do not create Reddit authorization. Get legal/product sign-off and provide provenance and removal handling; this actor is not affiliated with Reddit.

## Use cases

- **Brand and product monitoring** - track new Reddit discussions about a product, feature or competitor across subreddits.
- **Community research** - collect posts and comment bodies for a niche to understand recurring questions, pain points and language.
- **Trend discovery** - compare keyword volumes and engagement across time windows and sort orders.
- **Support and risk triage** - find comments mentioning outages, billing issues or safety concerns and route them to the right team.
- **Dataset building** - export provenance-rich posts/comments with live or archive freshness labels for analytics and NLP.

## FAQ

**Do I need a Reddit account or API credentials?**
No. The cookieless cascade works without credentials. An optional OAuth token improves live metrics if you have one.

**Why are some posts missing `score` or `num_comments`?**
RSS does not expose them. Records from RSS carry `metricsAvailable: false`; requesting a score filter causes a typed metrics status instead of silently passing rows.

**Why did I get fewer results than `resultLimit`?**
Source caps are real (RSS 100 with no pagination; Translate 24/page; Redlib 7/page; Arctic 100/page). A partial result is reported in the status record rather than silently hidden.

**What does `dataFreshness` mean?**
`live` for RSS/Translate/Redlib/OAuth; `archive_initial` or `archive_second_snapshot` for Arctic. Check `scoreAsOf`, `upvoteRatioAsOf` and `archiveLagSeconds` before treating archive engagement as current.

**Is this affiliated with Reddit?**
No. This is an independent actor. Reddit's terms, the Responsible Builder Policy, and third-party service terms still apply; get legal/product approval for commercial or automated collection.
