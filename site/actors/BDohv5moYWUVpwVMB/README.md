# Reddit Subreddit Post Filter & Moderation Scraper

Pulling posts from a subreddit is easy; pulling only the posts you actually want is the hard part. This actor scrapes one or more public subreddits and applies a stack of server-side filters — keyword, score floor, maximum age, NSFW, stickied status, author blocklist and link-domain allow/block lists — so the dataset you get back is already narrowed to what matters.

## What this actor does

- **Scrapes any number of public subreddits** in one run, sorted hot, new, top, rising or controversial
- **Filters posts before they reach your dataset**: minimum score, maximum age in days, a title/content keyword, NSFW, stickied, and Original-Content exclusions
- **Blocks by author or link domain**, or restricts results to an allowlist of domains
- **Flags subreddit-level problems** (banned, quarantined, private or missing subreddits) with a clear error record instead of silently returning nothing
- Fields a post doesn't have (such as `link_flair` on an unflaired post, or `crosspost_parent` on a non-crosspost) are left out of that record rather than sent empty

## Output per post

- `post_id`, `post_name` — Reddit's post ID and full post name (e.g. `t3_abc123`)
- `title`, `author`, `author_fullname` — post title and author identifiers
- `subreddit`, `subreddit_prefixed` — subreddit name, plain and with the `r/` prefix
- `content` — self-post text, when the post is a text post
- `score`, `num_comments` — post score and comment count
- `url`, `permalink` — the post's Reddit permalink
- `external_url`, `domain` — the linked URL and its domain, for link posts
- `link_flair` — post flair/tag text, when set
- `thumbnail_url`, `preview_url`, `image_url` — thumbnail and media preview URLs, when available
- `post_hint` — Reddit's classification of the post (e.g. image, link, self)
- `is_self`, `is_stickied`, `is_nsfw`, `is_spoiler`, `is_promoted`, `is_original_content`, `is_gallery` — boolean flags, present only when true
- `gallery_id` — gallery identifier, for gallery posts
- `gilded_count` — number of awards/gildings on the post, when greater than zero
- `num_crossposts`, `crosspost_parent` — crosspost count and the original post it was crossposted from, when applicable
- `title_word_count` — word count of the title
- `post_age_seconds` — how old the post was at scrape time, in seconds
- `created_utc`, `created_at` — Unix timestamp and ISO 8601 datetime of post creation
- `recordType` — set to `post` for every real post record (error records use `recordType: "error"` instead, with `reason` and `message` fields explaining what went wrong)

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `subreddits` | array | – | Subreddit names to scrape, without the `r/` prefix. |
| `maxPosts` | integer | `25` | Maximum posts to scrape per subreddit (1–1000). |
| `sort` | string | `hot` | `hot`, `new`, `top`, `rising` or `controversial`. |
| `timeFilter` | string | `day` | Time range used with `top`/`controversial`: `hour`, `day`, `week`, `month`, `year` or `all`. |
| `keywordFilter` | string | – | Only keep posts whose title or content contains this substring (case-insensitive). |
| `minScore` | integer | – | Drop posts with a score below this number. |
| `maxAgeDays` | integer | – | Drop posts older than this many days. |
| `excludeStickied` | boolean | `false` | Drop pinned/stickied posts (typically mod announcements). |
| `excludeNsfw` | boolean | `false` | Drop NSFW posts. |
| `excludeOriginalContent` | boolean | `false` | Drop posts marked as Original Content. |
| `authorBlocklist` | array | `[]` | Drop posts from these usernames (case-insensitive). |
| `domainAllowlist` | array | `[]` | If set, only keep posts whose link domain is in this list (self-posts always pass). |
| `domainBlocklist` | array | `[]` | Drop posts whose link domain is in this list. |

### Example: clean, high-score posts only

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

### Example: keyword monitoring across subreddits

```json
{
    "subreddits": ["technology", "artificial"],
    "sort": "new",
    "keywordFilter": "regulation",
    "maxAgeDays": 7,
    "maxPosts": 100
}
```

### Example: trusted-domain link roundup

```json
{
    "subreddits": ["machinelearning"],
    "sort": "hot",
    "domainAllowlist": ["arxiv.org", "github.com"],
    "maxPosts": 30
}
```

## Use cases

- **Community monitoring** — track keyword mentions across one or more subreddits, filtered to recent, non-stickied posts
- **Content curation** — build a trusted-source link digest using `domainAllowlist`
- **Brand or topic tracking** — follow discussion volume and sentiment proxies (score, comments) for a term over time
- **Moderation research** — audit stickied, NSFW or Original-Content posts separately using the exclude flags in reverse
- **Noise reduction** — drop known spam authors or domains with `authorBlocklist`/`domainBlocklist` before the data reaches your pipeline

## FAQ

**Do I need to log in to Reddit?**
No — only public subreddits are scraped, and no account or cookie is required.

**Can I scrape private or quarantined subreddits?**
No. If a subreddit is banned, quarantined, private or doesn't exist, the actor returns a single error record with `recordType: "error"` and a `reason` explaining the subreddit's status, instead of failing the whole run.

**Why is `content` missing from a post?**
`content` only holds text for self (text) posts. Link posts have no self-text to extract, so the field is left out.

**How do `domainAllowlist` and `domainBlocklist` interact?**
`domainAllowlist`, when set, restricts results to only those link domains (self-posts always pass). `domainBlocklist` removes specific domains regardless of the allowlist. Use one or the other for most cases.

**Why do filters reduce my post count below `maxPosts`?**
`maxPosts` caps how many posts are fetched from the subreddit before filtering; your keyword, score, age and exclusion filters are then applied on top, so the final count can be lower.

**What happens with `timeFilter` outside `top`/`controversial`?**
It's ignored for `hot`, `new` and `rising`, since those sorts aren't time-windowed on Reddit.

**Is this affiliated with Reddit?**
No, this is an independent, third-party actor that reads Reddit's public subreddit pages. It is not affiliated with or endorsed by Reddit, Inc.
