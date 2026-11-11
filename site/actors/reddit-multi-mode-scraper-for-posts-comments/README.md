# Reddit Multi-Mode Scraper for Posts, Comments & Profiles

Extract public Reddit data without an account, cookie, or API key. Choose a subreddit feed, specific post URLs with their comment trees, a user profile and history, or a keyword search. Every record is JSON with a stable `recordType` (`post`, `comment`, `profile`, or `community`), the original `dataType`, and a `source` tag so mixed datasets stay easy to audit.

## What this actor does

- **Four modes:** `subreddit` (post listings), `post` (one or more post URLs plus comments), `profile` (account metadata, posts and comments), and `search` (posts, comments, communities, and users).
- **Two data sources with provenance:** `live` reads Reddit's public rendered pages, while `archive` reads the Arctic Shift historical snapshot. `auto` uses live data first and archive for depth, bulk history, or fallback.
- **Full comment trees:** the archive path returns nested replies with `depth` and `parent_id`; live mode starts with the visible tree and expands top-level pages up to your cap.
- **Rich post fields:** score, upvote ratio, comment count, flair, domain, media URLs, galleries, video metadata, awards, crossposts, NSFW/spoiler/locked flags, and derived engagement metrics.
- **Filters and incremental runs:** score, comment count, upvote ratio, date range, post type, text matches, author allow/deny lists, flair, domain, awards, and an optional `onlyNew` watermark.
- **Empty fields are omitted:** records never contain `null`, empty strings, or empty arrays/objects.

## Output per post

- `recordType: "post"`, `dataType: "post"`, `source`, `sourceDetail`, `fetchedAt`, `snapshotFreshness`
- `id`, `post_id`, `post_name`, `title`, `author`, `author_id`, `author_meta`
- `subreddit`, `subreddit_prefixed`, `subreddit_id`, `subreddit_subscribers`, `subreddit_type`
- `content` / `body`, `content_html`, `content_url`, `url`, `permalink`, `domain`, `is_self`, `post_type`, `media_type`
- `score`, `ups`, `downs`, `upvote_ratio`, `num_comments`, `commentCount`, `gilded`, `total_awards_received`, `awards[]`
- `link_flair`, flair colors/classes/richtext, `thumbnail_url`, `images[]`, `gallery_images[]`, `gallery_count`
- `video_url`, `video_duration_seconds`, `video_width`, `video_height`, `video_has_audio`, `video_bitrate_kbps`
- `poll_data`, embed metadata, `crosspost_parent_id`
- `created_utc`, `created_at`, `createdAt`, `edited`, `edited_at`
- `is_nsfw`, `nsfw`, `is_spoiler`, `is_stickied`, `is_locked`, `is_archived`, `is_original_content`, `is_crosspost`
- `derived` (`ageHours`, `scorePerHour`, `commentsPerHour`, `engagementTotal`)
- `warning` and `degraded` when the record came from the archive snapshot

## Output per comment

- `recordType: "comment"`, `dataType: "comment"`, `source`, `sourceDetail`, `fetchedAt`
- `id`, `comment_id`, `comment_name`, `post_id`, `post_url`, `post_title`, `link_id`
- `parent_id`, `parentId`, `parent_kind`, `depth`, `body`, `body_html`
- `author`, `author_id`, `author_meta`
- `subreddit`, `subreddit_prefixed`, `subreddit_id`, `subreddit_type`
- `score`, `ups`, `downs`, `controversiality`, `gilded`, `total_awards_received`, `awards[]`
- `is_op`, `is_stickied`, `is_locked`, `collapsed`, `removed_by_category`
- `replies_count`, `replies`, `created_utc`, `created_at`, `createdAt`, `edited`, `edited_at`, `permalink`
- `coverage` on the parent post when comment coverage is known
- `warning` and `degraded` for archive records

## Output per profile

- `recordType: "profile"`, `dataType: "user_profile"`, `source`, `fetchedAt`
- `id`, `username`, `user_id`, `profile_url`, `icon_img`, `snoovatar_img`
- `karma` (`total`, `post`, `comment`), plus the flat `post_karma`, `comment_karma`, `total_karma`
- `post_count`, `comment_count`, `created_utc`, `created_at`, `createdAt`
- `description`, `is_gold`, `is_mod`, `is_employee`, `has_verified_email`, `verified`
- Profile history records are emitted as separate `post` and `comment` records.

## Output per community

Community records appear when `includeSubredditInfo`, `searchCommunities`, or the MCP `get_subreddit_info` tool is used.

- `recordType: "community"`, `dataType: "community"`, `source`, `fetchedAt`
- `id`, `subreddit`, `subreddit_prefixed`, `subreddit_id`, `url`, `title`
- `subscribers`, `active_user_count`, `created_utc`, `created_at`, `createdAt`
- `description`, `public_description`, `subreddit_type`, `over18`, `quarantine`
- `rules[]` when rules are requested

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `subreddit` | `subreddit`, `post`, `profile`, or `search`. Legacy `comments` maps to `post`; `posts`, `profiles`, and `subreddits` are accepted aliases. |
| `source` | string | `auto` | `auto`, `live`, or `archive`. `auto` prefers live data and uses the archive for depth, history, or fallback. |
| `subreddits` | array | `["programming"]` | Subreddits for `mode=subreddit`; names, `r/` names, and URLs are accepted. |
| `postUrls` | array | - | Post URLs, comment URLs, share links, or bare post IDs for `mode=post`. |
| `usernames` | array | - | Reddit usernames for `mode=profile`; `u/` names and profile URLs are accepted. |
| `searchQuery` | string | - | Keyword or phrase for `mode=search`. Reddit search operators are supported by the live path. |
| `maxItems` | int | `50` | Hard cap on all records emitted by the run (1-10,000). |
| `maxPosts` | int | `25` | Posts per subreddit, keyword, or profile section (1-5,000). |
| `maxComments` | int | `100` | Comments per post, keyword, or profile comment section; `0` disables comment records. |
| `maxDepth` | int | `6` | Deepest reply level to emit (0-20). |
| `includeComments` | bool | `true` | Emit comment records in `mode=post`. |
| `includePost` | bool | `true` | Emit the parent post record before its comments in `mode=post`. |
| `sort` | string | `hot` | `hot`, `new`, `top`, `rising`, `controversial`, `best`, or search values `relevance` and `comments`. |
| `timeFilter` | string | `day` | `hour`, `day`, `week`, `month`, `year`, or `all`. |
| `commentSort` | string | `confidence` | `confidence`, `top`, `new`, `controversial`, `old`, or `qa`. |
| `includeNSFW` | bool | `false` | Include over-18 posts and communities. |
| `includeSubredditInfo` | bool | `false` | Emit one community record per subreddit. |
| `includeSubredditRules` | bool | `false` | Attach rules to community records. |
| `includeProfileInfo` | bool | `true` | Emit the profile record in `mode=profile`. |
| `sections` | array | `["overview"]` | Profile history sections: `overview`, `posts`, `comments`. |
| `searchPosts` / `searchComments` / `searchCommunities` / `searchUsers` | bool | posts on | Select which result types `mode=search` returns. |
| `withinCommunity` | string | - | Restrict search to one subreddit; required for archive keyword search. |
| `maxCommunities` / `maxUsers` | int | `10` / `25` | Caps for community and user search results. |
| `onlyNew` | bool | `false` | Emit only records newer than the watermark stored under `stateKey`. |
| `stateKey` | string | `reddit-mcp-state` | Key-value store key prefix for `onlyNew` watermarks. |
| `failOnEmpty` | bool | `true` | Fail the run with a clear message when no records are found. |
| `proxyMode` | string | `none` | `none`, `datacenter`, or `residential`. Residential is an explicit fallback and is capped by `maxProxyBytesMb`. |
| `maxProxyBytesMb` | int | `50` | Stop the run before paid proxy traffic exceeds this many megabytes. |
| `minScore` / `maxScore` | int | - | Score range for posts and comments. |
| `minPostComments` / `maxPostComments` | int | - | Comment-count range for posts. |
| `minUpvoteRatio` | number | - | Minimum post upvote ratio (0-1). |
| `postType` | string | - | `self`, `link`, `image`, `video`, `gallery`, or `poll`. |
| `titleContains` / `contentContains` / `flairContains` / `authorFlairContains` | string | - | Case-insensitive text matches. |
| `domain` | string | - | Link domain contains this text. |
| `authors` / `excludeAuthors` | array | - | Author allow/deny lists. |
| `excludeKeywords` | array | - | Drop posts whose title, body, or flair contains any term. |
| `excludeStickied` / `excludeRemoved` / `excludeCrossposts` / `excludeSpoilers` / `excludeLocked` / `excludeDeletedAuthor` / `excludeArchived` | bool | `false` | Exclusion toggles. |
| `onlyWithFlair` / `onlyOriginalContent` | bool | `false` | Flair and OC filters. |
| `minAwards` | int | - | Minimum total awards. |
| `minContentLength` / `maxContentLength` | int | - | Body length range. |
| `postedAfter` / `postedBefore` | string | - | UTC date bounds (`YYYY-MM-DD`); `postedBefore` is inclusive. |
| `restrictSubreddits` | array | - | Keep profile history only from these subreddits. |
| `keyword` | string | - | Keep profile posts/comments containing this phrase. |
| `minCommunitySubscribers` / `maxCommunitySubscribers` | int | - | Community search size filters. |
| `minUserKarma` / `maxUserKarma` | int | - | User search karma filters. |
| `distinguished` | string | - | `moderator`, `admin`, `special`, or `none`. |

## Example: subreddit listing

```json
{
  "mode": "subreddit",
  "subreddits": ["programming", "r/Python"],
  "sort": "top",
  "timeFilter": "week",
  "maxItems": 100,
  "maxPosts": 50,
  "includeNSFW": false
}
```

## Example: post URLs with comments

```json
{
  "mode": "post",
  "postUrls": [
    "https://www.reddit.com/r/programming/comments/1xbl8y1/",
    "https://www.reddit.com/r/Python/s/example"
  ],
  "maxComments": 250,
  "maxDepth": 6,
  "includePost": true,
  "source": "auto"
}
```

## Example: profile and history

```json
{
  "mode": "profile",
  "usernames": ["spez"],
  "sections": ["overview"],
  "maxPosts": 25,
  "maxComments": 50,
  "postedAfter": "2026-01-01"
}
```

## Example: keyword search

```json
{
  "mode": "search",
  "searchQuery": "asyncio",
  "withinCommunity": "python",
  "searchPosts": true,
  "searchComments": true,
  "sort": "relevance",
  "timeFilter": "month",
  "maxItems": 50
}
```

## MCP server (Standby)

The actor runs a native Streamable HTTP MCP server at `/mcp` when started in Standby mode. It exposes five typed tools that reuse the same scrapers as the batch modes:

| Tool | What it returns |
|---|---|
| `search_reddit` | Posts, comments, communities, or users matching a query, with optional subreddit scope, sort, time window, and NSFW toggle. |
| `get_subreddit_posts` | A subreddit's posts with sort, time window, NSFW toggle, and item cap. |
| `get_post_comments` | One post plus its flat, depth-tagged comments, with `max_comments`, `max_depth`, comment sort, and an optional parent-post record. |
| `get_user_profile` | Profile metadata plus recent posts/comments for one user. |
| `get_subreddit_info` | Community metadata, optional rules, subscriber count, and description. |

MCP responses include `items`, `count`, `source`, and `degraded`; archive-backed responses also include a freshness warning. Use the Actor's Standby URL followed by `/mcp`:

```json
{
  "mcpServers": {
    "reddit": {
      "type": "streamable-http",
      "url": "https://<your-actor-standby-host>/mcp",
      "headers": {
        "Authorization": "Bearer <your-apify-token>"
      }
    }
  }
}
```

## Use cases

- **Community monitoring:** follow new and top posts in a set of subreddits on a schedule with `onlyNew`.
- **Thread research:** export a full comment tree for sentiment, topic, or quote analysis.
- **Creator and moderator analysis:** profile karma, posting history, and subreddit participation.
- **Trend discovery:** keyword search across Reddit posts and comments, optionally scoped to one community.
- **AI and RAG pipelines:** consume flat JSON records or call the MCP tools from an agent.
- **Moderation and compliance review:** filter by flair, domain, score, date, NSFW, and author.

## Data source, freshness, and cost

Live records come from Reddit's public rendered pages. The archive path uses the Arctic Shift historical snapshot, which typically lags live Reddit by several hours and can have fewer comments or older scores. Archive records are marked `source: "archive"`, `degraded: true`, and include a `warning`; the `snapshotFreshness` field distinguishes them from live data.

The actor defaults to 1 GB of memory; Apify bills the run by allocated memory and any proxy traffic. Browser requests block images, fonts, and media to keep traffic and cost down. No proxy is used by default; `datacenter` is available when Reddit blocks a run, and `residential` is an explicit last resort. `maxProxyBytesMb` stops the run when the configured proxy traffic ceiling is reached.

## FAQ

### Do I need a Reddit account or API key?

No. The actor reads public pages and a public archive, and no cookies, login, or API key are required.

### Why do live and archive records disagree on score or comment count?

The archive is a historical crawl. Live pages reflect the current score, upvote ratio, and comment count; archive records can be several hours stale and are marked `degraded`.

### Why are some comments missing from a very large thread?

Live mode starts with the comments Reddit renders and expands top-level pages up to `maxComments`; replies can be limited by Reddit's pagination. Use `source: "auto"` or `"archive"` for deeper trees, and check the parent post's `coverage` fields.

### Why did my search return fewer results than expected?

Reddit limits search result pages and caps many queries. The actor follows the available result pages up to `maxItems`; use a narrower `withinCommunity`, a different sort, or a broader time window.

### What does `onlyNew` do?

It stores a watermark in the key-value store under `stateKey` and emits only records newer than the previous run. Archive watermarks keep a small overlap so a late-indexed comment is not skipped.

### Does the actor work for private or quarantined communities?

No. Only public, cookieless content is supported. NSFW posts can be included with `includeNSFW`, but login-gated or quarantined communities are out of scope.

### How do I get community rules?

Set `includeSubredditInfo` and `includeSubredditRules` in `mode=subreddit`, or call the `get_subreddit_info` MCP tool with `include_rules: true`.

### How do I keep runs cheap?

Use `source: "archive"` when you only need historical posts or deep trees, keep `maxItems` and `maxComments` small, and leave `proxyMode` at `none`. The actor defaults to 1 GB of memory and does not download images, fonts, or media. If you choose a proxy, `maxProxyBytesMb` stops the run when its traffic ceiling is reached.

### Is this affiliated with Reddit?

No. This is a third-party tool that reads public Reddit pages and a public archive. Respect Reddit's terms and applicable law when using the data.
