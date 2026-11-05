# Reddit Subreddit Post Filter & Moderation Scraper

Pull posts from public subreddits, then keep only the ones that matter. This actor reads Reddit's public subreddit listings, applies a full set of filters before it counts toward your limit, and writes clean post records with score, comments, flair, media, gallery, video, poll and crosspost data.

No Reddit login, API key, cookie or proxy setup is required.

## What it does

- Scrapes one or many public subreddits, sorted hot, new, top, rising, controversial or best.
- Applies the time filter for top and controversial.
- Keeps paging until it finds the requested number of **matching** posts or reaches Reddit's listing limit.
- Filters by keywords, score, comment count, upvote ratio, date/age, flair, post type, author, domain, NSFW and stickied status.
- Emits explicit `status` or `error` records when a subreddit is blocked, private, banned, missing or empty, instead of silently returning nothing.
- Optionally emits one community metadata record per subreddit.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `subreddits` | array | — | Subreddit names, `r/` names or full Reddit URLs. Required. |
| `sort` | select | `hot` | `hot`, `new`, `top`, `rising`, `controversial` or `best`. |
| `timeFilter` | select | `day` | `hour`, `day`, `week`, `month`, `year` or `all`; used with top/controversial. |
| `maxPosts` | integer | `25` | Maximum matching posts per subreddit (1–1000). |
| `maxItems` | integer | `1000` | Overall cap across all subreddits (1–10,000). |
| `includeKeywords` | array | `[]` | Keep posts containing any/all of these words or phrases. |
| `excludeKeywords` | array | `[]` | Drop posts containing any of these words or phrases. |
| `keywordMatch` | select | `any` | `any`, `all` or `exact` (join include keywords into one phrase). |
| `searchIn` | select | `title-and-body` | `title-and-body`, `title` or `body`. |
| `minScore` / `maxScore` | integer | empty | Score range. |
| `minComments` / `maxComments` | integer | empty | Comment-count range. |
| `minUpvoteRatio` | number | empty | Minimum upvote ratio, 0–1. |
| `postedAfter` / `postedBefore` | string | empty | ISO date or relative value such as `7 days` or `24 hours`. |
| `maxAgeDays` | integer | empty | Shortcut for a recent-post cutoff. |
| `flairAllowlist` | array | `[]` | Only these exact flair names (case-insensitive). |
| `postType` | select | `all` | `all`, `text`, `link`, `image`, `video`, `gallery`, `poll`, `crosspost`, `gif` or `multi_media`. |
| `excludeStickied` | boolean | `false` | Drop pinned posts. |
| `excludeNsfw` | boolean | `false` | Drop posts marked NSFW. |
| `authorAllowlist` / `authorBlocklist` | array | `[]` | Username allow/block lists. |
| `domainAllowlist` / `domainBlocklist` | array | `[]` | Link-domain allow/block lists. Self-posts pass. |
| `includeSubredditInfo` | boolean | `false` | Emit one community metadata record per subreddit. |

### Examples

High-score, clean posts:

```json
{
  "subreddits": ["python", "programming"],
  "sort": "top",
  "timeFilter": "week",
  "minScore": 100,
  "excludeNsfw": true,
  "excludeStickied": true,
  "maxPosts": 50
}
```

Keyword monitoring:

```json
{
  "subreddits": ["technology", "artificial"],
  "sort": "new",
  "includeKeywords": ["regulation", "policy"],
  "excludeKeywords": ["giveaway"],
  "postedAfter": "7 days",
  "maxPosts": 100
}
```

Trusted-domain links only:

```json
{
  "subreddits": ["machinelearning"],
  "sort": "hot",
  "domainAllowlist": ["arxiv.org", "github.com"],
  "maxPosts": 30
}
```

## Output

Each post record includes:

- `recordType` (`post`), `post_id`, `post_name`, `title`
- `author`, `author_fullname`, `author_id`
- `subreddit`, `subreddit_prefixed`, `subreddit_id`
- `content`, `content_length` (self-post body; `content` is capped at 1,000 characters)
- `score`, `num_comments`, `upvote_ratio`
- `url`, `permalink`, `old_reddit_url`, `external_url`, `domain`
- `post_type`, `post_hint`, `language`
- `link_flair`, `link_flair_background_color`
- `thumbnail_url`, `preview_url`, `image_url`, `image_urls`
- `gallery_id`, `gallery_images`, `gallery_count`
- `is_self`, `is_stickied`, `is_nsfw`, `is_spoiler`, `is_gallery`, `is_crosspost`
- `crosspost_parent`, `crosspost_parent_id`, `crosspost_parent_subreddit`, `crosspost_parent_url`
- `total_awards_received`, `top_award_id`, `top_award_icon_url`
- `has_media`, `media_type`
- `video_url`, `video_hls_url`, `video_mp4_url`, `video_poster_url`, `video_duration_seconds`, `video_width`, `video_height`, `video_bitrate_kbps`
- `embed_provider`, `embed_html`, `embed_title`
- `poll_data` (closed state, total votes, option positions/votes where rendered)
- `title_word_count`, `post_age_seconds`, `created_utc`, `created_at`, `crawled_at`

Optional community record (`recordType: "subreddit"`): `subreddit`, `subreddit_prefixed`, `subreddit_id`, `display_name`, `description`, `subscribers`, `created_utc`, `created_at`, `crawled_at`. `weekly_active_users` and `weekly_contributions` are included only when the direct Reddit page header provides them; the Arctic Shift metadata fallback does not expose those two values, so they are omitted rather than fabricated.

Status/error records explain what happened without failing the run:

- `recordType: "error"` with `reason` (`blocked`, `login_required`, `private`, `banned`, `not_found`, `nsfw_gated`, `rate_limited`, `http_error`), `message`, `subreddit`, optional `page_title` and `httpStatus`.
- `recordType: "status"` with `reason` (`empty`, `no_matches`, `rising_cap`, `info_unavailable`), `message`, `postCount`, `filteredCount`.

Fields Reddit does not expose anonymously are never fabricated. `is_promoted`, `is_original_content`, `gilded_count` and `num_crossposts` remain documented for compatibility but are omitted because the public listing does not carry reliable values. `old_reddit_url` may redirect to a login page on old Reddit.

## Limits and behavior

- Reddit's full HTML listing feeds stop at roughly **1,000 posts** for hot/new and roughly **500** for top/controversial. The cloud RSS fallback is capped at **100 posts per subreddit**. Split by sort, time range or subreddit to collect more.
- `rising` is a small live listing; it may return fewer posts than `maxPosts`.
- `maxPosts` counts **matching** posts, not scanned posts. If a filter is restrictive, the actor pages deeper until it finds matches or reaches the listing ceiling.
- NSFW-only communities are age-gated for anonymous visitors and may appear as `not_found` or `nsfw_gated`. Per-post NSFW filtering works when the listing carries the flag.
- Poll option labels are not always rendered in the public listing; vote counts and positions are captured when present.
- Video HLS/MP4 URLs can be signed and expire. `video_url` uses a stable low-resolution fallback; the HLS/MP4 fields are provided for convenience.
- If Reddit blocks the direct listing, the actor first reads the same listing through a Google Translate mirror. That mirror keeps the full post fields. If it is unavailable, the actor falls back to the public Atom/RSS feed. The RSS fallback carries title, author, URL, body and timestamps, but not score, comment count, media, gallery, video or poll fields; the run status message says when it is used.
- If score, comment-count or upvote-ratio filters are set and only RSS is available, the actor does **not** silently pass those filters. It emits a clear `metrics_unavailable` error record for that subreddit and skips it, rather than returning unfiltered posts as if they matched.
- When `includeSubredditInfo` is enabled, the actor tries the direct subreddit page header first and falls back to Arctic Shift's public `subreddits/search` endpoint. Arctic supplies subscribers, description and creation time; weekly active users and weekly contributions are not available there, so those fields are omitted.
- The actor paces requests and backs off on rate limits. It never uses a wall-clock stop that silently under-delivers rows.

## FAQ

**Do I need a Reddit account, API key or proxy?**
No. The actor reads public listing HTML directly and escalates its own internal proxy only if Reddit blocks the request.

**Why did I get a status or error record instead of posts?**
The subreddit may be private, banned, missing, age-gated, temporarily blocked or empty. The record's `reason` and `message` explain which case applies. The rest of the run continues.

**Why did I get a `metrics_unavailable` error?**
Reddit’s RSS fallback has no score, comment count or upvote ratio. The actor will not pretend a metric filter passed on RSS-only data. It skips that subreddit and emits the error; retry when the full listing or Translate mirror is available, or remove the metric filter.

**Why are my filters returning fewer posts than `maxPosts`?**
`maxPosts` is the number of posts that pass your filters. If the source runs out before that, the actor returns what exists. The run status message reports filtered outages.

**Can I scrape comments?**
No. This actor is focused on subreddit posts and moderation filters. Use a dedicated Reddit comment scraper for threads.

**Is this affiliated with Reddit?**
No. This is an independent, third-party actor that reads public Reddit pages. It is not affiliated with or endorsed by Reddit, Inc.
