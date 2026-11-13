# Reddit Subreddit Post Filter & Moderation Scraper

Monitor public subreddits and keep only the posts that matter. This actor reads Reddit's live subreddit feed, applies your keyword, metric, date, flair, type, author and domain filters before counting toward your limit, and writes clean post records with score, comments, upvote ratio, flair, media, gallery, video, poll and crosspost data.

No Reddit login, API key, cookie or proxy setup is required.

## What it does

- Scrapes one or many public subreddits, sorted hot, new, top, rising, controversial or best.
- Applies the time filter for top and controversial.
- Keeps paging until it finds the requested number of **matching** posts or reaches the source's listing limit.
- Filters by keywords, score, comment count, upvote ratio, date/age, flair, post type, author, domain, NSFW and stickied status.
- Emits explicit `status` records for private, banned, missing, age-gated, empty and no-match subreddits, and `error` records for blocked, rate-limited or failed reads. The rest of the run continues.
- Optionally emits one community metadata record per subreddit.
- Tags every post with `source` so you know which fetch path produced it.

## How it fetches Reddit

Reddit blocks plain HTTP clients on many networks. The actor therefore picks one transport on its first request and keeps it for the whole run:

1. **Browser feed (primary).** A headless Chromium session solves Reddit's JavaScript challenge once, waits for the server-rendered `shreddit-post` cards, reads the feed, and reuses the challenge cookies for the `community-more-posts` partial when paginating. This path carries the live score, comment count, upvote ratio, flair and media fields. The browser runs direct, with no account cookies and no proxy.
2. **Arctic Shift archive (full-field fallback).** If the browser cannot load Reddit or is blocked, the actor reads `arctic-shift.photon-reddit.com/api/posts/search`. It returns full Reddit fields (score, comments, ratio, media, gallery, poll, crosspost, author flair, moderation flags and awards). Archive metrics lag roughly 36 hours and rows are newest-first.
3. **Reddit RSS (last resort).** If both full-field paths fail, the actor reads the public Atom feed. It carries title, author, URL, body and timestamps, and can paginate with `after=t3_<last post>`, but has no score, comment count, upvote ratio or reliable media/flair.

The chosen transport is sticky: a later block is reported as an error or status record instead of silently switching sources or retrying five times. A post record's `source` is `reddit-shreddit`, `arctic-shift` or `reddit-rss`; RSS records also carry `reduced: true`.

**Cloud behavior.** From Apify cloud IPs the browser path may be blocked by Reddit. That is expected: the verified cloud runs selected Arctic Shift and returned full score/comment/ratio records. The actor does **not** escalate the browser through `AUTO` or `RESIDENTIAL` proxies. `AUTO` datacenter proxies do not make Reddit's JavaScript challenge more reliable, and `RESIDENTIAL` is a paid proxy outside this actor's cookieless/free design. The full-field Arctic fallback is the escalation path; RSS is only chosen if Arctic is also unavailable. Optional HTTP requests (Arctic metadata, RSS) can use an `AUTO` proxy rung when the Apify proxy configuration is available; residential proxy groups are never selected automatically.

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
- `source` (`reddit-shreddit`, `arctic-shift` or `reddit-rss`) and `reduced` on RSS-only records
- `author`, `author_fullname`, `author_id`
- `subreddit`, `subreddit_prefixed`, `subreddit_id`, `subreddit_subscribers`, `subreddit_type`
- `content`, `content_length` (self-post body; `content` is capped at 1,000 characters), `selftext_html` when the archive carries it
- `score`, `num_comments`, `upvote_ratio`
- `url`, `permalink`, `old_reddit_url`, `external_url`, `domain`
- `post_type`, `post_hint`, `language`
- `link_flair`, `link_flair_background_color`, `link_flair_text_color`
- `author_flair`, `author_flair_background_color`, `author_flair_text_color`
- `thumbnail_url`, `thumbnail_width`, `thumbnail_height`, `preview_url`, `preview_images`, `image_url`, `image_urls`
- `gallery_id`, `gallery_images`, `gallery_count`
- `is_self`, `is_stickied`, `is_locked`, `is_archived`, `is_nsfw`, `is_spoiler`, `is_gallery`, `is_crosspost`, `is_video`, `is_original_content`
- `is_reddit_media_domain`, `is_media_only`, `is_meta`, `is_quarantined`, `author_premium`
- `distinguished`, `removed_by_category`, `moderation_verdict`
- `is_edited`, `edited_utc`, `edited_at`
- `crosspost_parent`, `crosspost_parent_id`, `crosspost_parent_subreddit`, `crosspost_parent_url`
- `total_awards_received`, `top_award_id`, `top_award_icon_url`, `awards`, `gildings`, `gilded_count`
- `is_created_from_ads_ui`, `hide_score`, `send_replies`, `whitelist_status`, `parent_whitelist_status`
- `has_media`, `media_type`
- `video_url`, `video_hls_url`, `video_mp4_url`, `video_poster_url`, `video_duration_seconds`, `video_width`, `video_height`, `video_bitrate_kbps`
- `embed_provider`, `embed_html`, `embed_title`
- `poll_data` (closed flag, total votes, option positions, labels and votes when available)
- `title_word_count`, `post_age_seconds`, `created_utc`, `created_at`, `crawled_at`, `num_crossposts`, `num_duplicates`

Field availability differs by transport. Every field is emitted only when the transport actually provides it; absent fields are omitted rather than set to null or zero.

| Field group | Browser feed | Arctic archive | RSS |
|---|---|---|---|
| Score, comments, ratio, timestamps, author, title, URL | yes | yes (metrics lag ~36h) | timestamps/author/title/URL only |
| Self-post body, link flair, images, gallery, video, embed, poll, crosspost | yes | yes | body; first image/thumbnail and feed flair when present |
| Author flair | not in listing cards | yes | no |
| `distinguished`, `removed_by_category`, `moderation_verdict` | only when rendered in the card | yes | no |
| `is_edited`, `edited_utc`, whitelist/ad flags, `gildings`, `awards` | no | yes | no |
| `is_locked`, `is_archived` | status icons when rendered | yes | no |

Optional community record (`recordType: "subreddit"`): `subreddit`, `subreddit_prefixed`, `subreddit_id`, `display_name`, `description`, `subscribers`, `created_utc`, `created_at`, `crawled_at`, `source`. `weekly_active_users` and `weekly_contributions` are included only when the direct Reddit page header provides them; the Arctic Shift metadata fallback does not expose those two values, so they are omitted rather than fabricated.

Status and error records explain what happened without failing the run:

- `recordType: "status"` for community conditions: `private`, `banned`, `not_found`, `nsfw_gated`, `empty`, `no_matches` and `info_unavailable`, with `message`, `postCount`, `filteredCount` and `source`.
- `recordType: "error"` for fetch failures: `blocked`, `login_required`, `rate_limited`, `http_error` and `metrics_unavailable`, with `message`, optional `page_title`, `httpStatus` and `source`.

Fields Reddit does not expose anonymously are never fabricated. `is_promoted` is omitted because public listings do not carry a reliable value. `is_original_content`, `gilded_count` and `num_crossposts` are filled only when the transport provides them (the Arctic archive does) and omitted otherwise. `old_reddit_url` may redirect to a login page on old Reddit.

## Limits and behavior

- Reddit's own HTML feeds stop at roughly **1,000 posts** for hot/new and roughly **500** for top/controversial. The Arctic archive and RSS feeds have their own windows.
- `rising` is a small live listing; it may return fewer posts than `maxPosts`.
- `maxPosts` counts **matching** posts, not scanned posts. If a filter is restrictive, the actor pages deeper until it finds matches or reaches the source ceiling.
- On the RSS fallback, pages hold up to 100 posts and pagination uses `after=t3_<last post>`, paced between requests. The feed has no score, comment count, upvote ratio or reliable media/flair. Records are marked `reduced: true`.
- If score, comment-count or upvote-ratio filters are set and only RSS is available, the actor does **not** silently pass those filters. It emits a clear `metrics_unavailable` error record for that subreddit and skips it.
- Arctic Shift rows are archive snapshots ordered newest-first; metrics lag about 36 hours. Recent posts may be missing there until the archive catches up.
- A blocked browser path is not retried five times. The actor moves once to the next transport and then keeps the selected transport for the run; a later block becomes an `error` record.
- Browser cards can mount a few seconds after navigation. The actor waits up to 10 seconds for `shreddit-post` cards (or a subreddit header) before reading the DOM, which is required on slower live pages.
- Author flair, edit status, whitelist/ad flags, `gildings`, `removed_by_category` and `distinguished` are Arctic-only. Browser cards expose `distinguished`/locked/archived only when Reddit renders those tags; RSS exposes link flair only when the Atom entry carries a non-subreddit category.
- NSFW-only communities are age-gated for anonymous visitors and may appear as `nsfw_gated` or `not_found`. Per-post NSFW filtering works when the listing carries the flag.
- Video HLS/MP4 URLs can be signed and expire. `video_url` uses a stable low-resolution fallback; the HLS/MP4 fields are provided for convenience.
- Gallery images use the full-resolution `i.redd.it` URL when it can be derived and otherwise keep the best preview/direct URL available. This avoids dropping direct-only gallery items.
- The actor paces requests and backs off on transient server errors. It never uses a wall-clock stop that silently under-delivers rows.

## FAQ

**Do I need a Reddit account, API key or proxy?**
No. The actor solves Reddit's public JavaScript challenge in a headless browser when possible and falls back to a public archive and public RSS. No account cookies or paid proxy are used. The browser is direct; Arctic Shift is the full-field escalation when Reddit blocks the browser.

**Why did I get a status or error record instead of posts?**
The subreddit may be private, banned, missing, age-gated, empty or temporarily blocked. The record's `recordType`, `reason` and `message` explain which case applies. The rest of the run continues.

**Why are score, comments or media missing?**
Those fields exist on the browser feed and the Arctic archive. If Reddit blocks the browser and the archive is unavailable, the actor falls back to RSS, which has no metrics; those records say `source: "reddit-rss"` and `reduced: true`. Author flair, edit/whitelist/moderation flags and award breakdowns are archive-only; they are omitted when the browser or RSS path cannot provide them.

**Why did I get a `metrics_unavailable` error?**
Metric filters cannot be applied to RSS-only data. The actor will not pretend a score, comment or ratio filter passed. It skips that subreddit and emits the error; retry when the browser feed or archive is available, or remove the metric filter.

**Why are my filters returning fewer posts than `maxPosts`?**
`maxPosts` is the number of posts that pass your filters. If the source runs out before that, the actor returns what exists. The run status message reports filtered and skipped subreddits.

**Can I scrape comments?**
No. This actor is focused on subreddit posts and moderation filters. Use a dedicated Reddit comment scraper for threads.

**Is this affiliated with Reddit?**
No. This is an independent, third-party actor that reads public Reddit pages. It is not affiliated with or endorsed by Reddit, Inc.
