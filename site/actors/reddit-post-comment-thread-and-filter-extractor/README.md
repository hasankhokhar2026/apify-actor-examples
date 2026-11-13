# Reddit Post Comment Thread & Filter Extractor

Paste in one or more Reddit post links and get every comment on that thread as a flat dataset row, in the order the thread tree expands collapsed replies. A companion record with the post's own stats is added for each URL, and a set of optional filters lets you narrow a huge thread down to only the comments worth reading before you export anything.

## What this actor does

- Loads each Reddit post from the public www.reddit.com new UI and, when `expandThreads` is enabled, opens collapsed "load more" and "continue this thread" sections so deep replies are not left out.
- Returns every comment with its author, text, score, nesting depth, and the ID of the comment it replies to, so you can rebuild the thread tree.
- Captures the award count Reddit reports for each comment and post, plus controversiality, distinguished (mod/admin) status, stickied/locked state and author flair when Reddit renders them for logged-out visitors.
- Captures post-level media metadata Reddit renders: image/gallery URLs, video and MP4 URLs, poll options and votes, link embeds and crosspost parents.
- Applies any score, depth, age, author, keyword or word-count rule you set, dropping non-matching comments before they reach the dataset.
- Optionally fills static fields Reddit no longer renders (author fullname, award/gilding detail, distinguished, archived/locked) from the public Arctic Shift archive, with explicit provenance fields. Page data always wins.
- Omit any field Reddit did not provide for a given comment or post, instead of writing a blank or null value.
- Adds a coverage record when the dataset holds fewer comments than Reddit's own `num_comments` reports, and an error record when a post could not be fetched, so a partial run is visible in the dataset instead of only in the log.

## Output per record

Each run produces one post-metadata record per successfully loaded URL, one record per comment that passed your filters, and optionally coverage or error records.

- Comment and post records use **snake_case** fields.
- Error and coverage records use **camelCase** fields, matching their diagnostic purpose.

### Post metadata record

| Field | Description |
| --- | --- |
| recordType | Always `post` for this record type |
| post_id | Reddit's post ID |
| post_name | Fullname in Reddit's `t3_<id>` format |
| title | Post title |
| author | Username of the poster |
| author_fullname | Poster's Reddit fullname ID, when Reddit renders it (or archive enrichment fills it) |
| author_flair | Poster's rendered author flair/badge, when present (or archive `author_flair_text`) |
| subreddit | Subreddit name without the `r/` prefix |
| subreddit_prefixed | Subreddit name with `r/` prefix |
| domain | Link domain for link posts (e.g. `self.programming`) |
| post_type | Reddit's post type: `text`, `link`, `image`, `gallery`, `video`, `gif`, `poll` or `crosspost` |
| upvote_ratio | Share of upvotes, from Reddit's `upvote-ratio` attribute |
| score | Post score (upvotes minus downvotes) |
| num_comments | Total comment count reported by Reddit |
| permalink | Full URL of the post |
| url | Same as permalink |
| content_url | Outbound, image, gallery or video content URL, when it differs from the post URL |
| selftext | Post body text, for text posts |
| selftext_html | Post body as HTML, for text posts |
| link_flair | Post flair text, if the subreddit uses flairs |
| is_self | True for text posts |
| is_stickied | True if the post is pinned |
| is_nsfw | True if marked over-18 |
| is_spoiler | True if marked as a spoiler |
| is_original_content | True if flagged as OC |
| is_locked | True if comments are locked |
| is_archived | True if the post is archived (or archive enrichment supplies it) |
| is_edited | True when Reddit renders an edit marker for the post |
| edited_at | Post edit timestamp, when Reddit or archive discloses one |
| distinguished | `moderator`/`admin`/`special` tag, when rendered or supplied by archive |
| removed_by_category | Removal category, when rendered or supplied by archive |
| thumbnail_url | Preview/poster image URL Reddit renders for image, gallery and video posts |
| media_url | Primary image or video URL for image/video posts |
| gallery_images | Gallery image URLs rendered in the initial server response |
| video_url | HLS video playlist URL for Reddit-hosted video |
| video_mp4_url | Highest-bitrate MP4 fallback URL from the player's packaged media JSON |
| video_duration_seconds | Video duration, when the player exposes it |
| poll_data | `options`, `total_votes` and `closes_at` for poll posts |
| embed_url | First iframe URL in a link post's rendered embed |
| embed_provider | Embed provider name (e.g. `YouTube`) |
| crosspost_parent_id | Original post ID for a crosspost, when Reddit renders the parent |
| crosspost_parent_url | Original post URL for a crosspost |
| award_id | Award ID Reddit renders on the post's award button |
| award_icon_url | Icon URL for the rendered award |
| awards_count | Award count Reddit reports for the post |
| total_awards_received | Total awards from archive enrichment, when available |
| awards | Normalized award list (`name`, `count`, `icon_url`, `id`) from archive enrichment |
| gildings | Legacy gilding counts (`gid_1`/`gid_2`/`gid_3`) from archive enrichment |
| more_comments_count | Count of "load more" sources Reddit still showed after expansion, when any remain |
| comment_sort | Comment sort order active on the page (e.g. `confidence`, `top`) |
| created_utc | Post creation time as a Unix timestamp |
| created_at | Post creation time as an ISO 8601 datetime |
| enrichment_source | `arctic_shift` when archive enrichment filled at least one field |
| enrichment_fields | Names of fields filled from the archive |
| archive_retrieved_utc | When the archive snapshot was captured, when known |

### Comment record

| Field | Description |
| --- | --- |
| recordType | Always `comment` for this record type |
| comment_id | Reddit's comment ID |
| comment_name | Fullname in Reddit's `t1_<id>` format |
| author | Username of the commenter, or `[deleted]` |
| author_fullname | Commenter's Reddit fullname ID, when Reddit renders it (or archive enrichment fills it) |
| author_flair | Rendered author flair/badge text (for example `Top 1% Commenter`), when present |
| text | Comment body text |
| body_html | Comment body as HTML |
| score | Comment score (upvotes minus downvotes), when visible |
| score_hidden | True when Reddit's action row marks the score as hidden |
| permalink | Direct link to the comment |
| post_url | URL of the post the comment belongs to |
| depth | Nesting level in the thread (0 = top-level reply to the post) |
| parent_comment_id | ID of the comment this one replies to, when it is not top-level |
| replies_count | Number of direct replies visible among the comments scraped for this post |
| subreddit | Subreddit the post belongs to |
| subreddit_prefixed | Subreddit with the `r/` prefix |
| is_op | True if the commenter is the post's original author (legacy alias of `is_submitter`) |
| is_submitter | True if the commenter is the post's original author |
| is_edited | True if the comment was edited after posting |
| edited_at | Edit timestamp, when Reddit discloses one |
| is_stickied | True if the comment is pinned by a moderator |
| is_locked | True when the comment's badges mark it locked |
| is_archived | True when archive enrichment reports the comment archived |
| is_collapsed | True if the comment was shown collapsed on the page |
| is_deleted | True if the comment body or author shows as deleted/removed |
| is_automod | True if posted by AutoModerator |
| is_likely_bot | True if the author name matches a common bot-naming pattern |
| comment_age_seconds | Seconds between posting and the time the comment was scraped |
| distinguished | `moderator`/`admin`/`special` tag, when rendered or supplied by archive |
| controversiality | True when Reddit marks the comment controversial |
| removed_by_category | `moderator`, `reddit`, `automoderator`, `deleted` or `removed`, inferred from rendered removal text or archive metadata |
| user_flair | Subreddit flair text, from the rendered flair slot or archive enrichment |
| word_count | Whitespace-separated word count of the comment body |
| body_quote_count | Number of quote blocks in the comment body |
| body_code_count | Number of code blocks in the comment body |
| body_link_count | Number of links in the comment body |
| award_id | Award ID Reddit renders on the comment's award button |
| award_icon_url | Icon URL for that rendered award |
| awards_count | Number of awards Reddit reports for the comment |
| total_awards_received | Total awards from archive enrichment, when available |
| awards | Normalized award list (`name`, `count`, `icon_url`, `id`) from archive enrichment |
| gildings | Legacy gilding counts (`gid_1`/`gid_2`/`gid_3`) from archive enrichment |
| created_utc | Comment creation time as a Unix timestamp |
| created_at | Comment creation time as an ISO 8601 datetime |
| enrichment_source | `arctic_shift` when archive enrichment filled at least one field |
| enrichment_fields | Names of fields filled from the archive |
| archive_retrieved_utc | When the archive snapshot was captured, when known |

Reddit's logged-out pages expose an award **count** and one representative award button (`award_id`, `award_icon_url`), but not the complete award list or legacy gilding. When `enrichFromArchive` is enabled, the archive can add the complete `awards` list, `gildings`, `total_awards_received`, `author_fullname`, `author_flair_text`, `distinguished`, and archived/locked flags. Archive award payloads are often sparse for very recent items, so the page's `awards_count` remains authoritative and the provenance fields show exactly what came from the archive.

### Archive enrichment

`enrichFromArchive: true` makes one optional batch lookup per post and one per set of kept comments against the public [Arctic Shift](https://arctic-shift.photon-reddit.com) Reddit archive. It fills only fields that the rendered page did not supply:

- **Post**: `author_fullname`, `author_flair`, `distinguished`, `is_locked`, `is_archived`, `is_edited`/`edited_at`, `upvote_ratio`, `removed_by_category`, `awards`, `gildings`, `total_awards_received`, `awards_count`.
- **Comment**: `author_fullname`, `author_flair`, `user_flair`, `distinguished`, `is_submitter`, `is_stickied`, `score_hidden`, `controversiality`, `is_collapsed`, `is_locked`, `is_archived`, `removed_by_category`, `awards`, `gildings`, `total_awards_received`, `awards_count`.

Rendered page values are never overwritten. Filled records gain `enrichment_source: "arctic_shift"`, an `enrichment_fields` list, and `archive_retrieved_utc` when the snapshot time is known. If the archive is unavailable or rate-limits the request, the actor logs a warning and continues with page data only; it never fails a post because enrichment failed.

### Coverage record

A coverage record is added whenever the number of kept comments is lower than the post's reported `num_comments`. It explains whether the gap came from your filters, a cap, or comments Reddit counts but does not serve to logged-out visitors.

| Field | Description |
| --- | --- |
| recordType | Always `coverage` |
| type | Always `reddit_comment_scraper_pro_coverage` |
| postUrl | The URL you supplied |
| postId | Reddit's post ID |
| expectedComments | Reddit's reported `num_comments` |
| scrapedComments | Unique comments read before filters |
| keptComments | Comment records emitted after filters |
| expandThreads | Whether thread expansion was enabled |
| reason | Comma-separated reasons such as `max_comments_reached`, `fetch_call_cap`, `more_comments_remaining`, `fewer_comments_served` or `filters_applied` |
| remainingSources | Number of unopened "load more" sources left, when any |
| filtersApplied | Active filter names, when any |
| scrapedAt | When the record was written (ISO 8601) |

### Error record

A failed post now produces one error record instead of only a log line.

| Field | Description |
| --- | --- |
| recordType | Always `error` |
| type | Always `reddit_comment_scraper_pro_error` |
| reason | Short failure code such as `not_found`, `blocked`, `login`, `challenge` or `exception` |
| message | Human-readable failure detail |
| postUrl | The URL that failed, when known |
| httpStatus | HTTP status returned by Reddit, when available |
| scrapedAt | When the record was written (ISO 8601) |

## Input

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `postUrls` | array | – | Reddit post URLs to scrape comments from (required) |
| `maxComments` | integer | `100` | Maximum number of comments kept per post, counted after filters, 1-10000 |
| `expandThreads` | boolean | `false` | Fetch "load more comments" partials and "continue this thread" pages to reveal collapsed replies |
| `commentSort` | string | `confidence` | Comment sort: `confidence` (Best), `top`, `new`, `controversial`, `old` or `qa` |
| `enrichFromArchive` | boolean | `false` | Fill static fields Reddit no longer renders (author fullname, award/gilding detail, distinguished, archived/locked) from the public Arctic Shift archive. Page data always wins |
| `minScore` | integer | – | Drop comments scoring below this number; comments with no visible score are also dropped |
| `maxDepth` | integer | – | Drop comments nested deeper than this (0 keeps only top-level replies) |
| `maxAgeDays` | integer | – | Drop comments older than this many days |
| `excludeDeleted` | boolean | `false` | Drop comments where the author is `[deleted]` or the body is `[removed]` |
| `authorFilter` | string | – | Keep only comments by an author whose name contains this text (case-insensitive) |
| `keywordFilter` | string | – | Keep only comments whose body contains this text; prefix with `!` to drop matches instead |
| `minWordCount` | integer | – | Drop comments shorter than this many words |
| `maxWordCount` | integer | – | Drop comments longer than this many words |

### Example: default scrape of one thread

```json
{
  "postUrls": ["https://www.reddit.com/r/programming/comments/1s9jkzi/announcement_temporary_llm_content_ban/"],
  "maxComments": 200
}
```

### Example: top-scored replies from a busy thread

```json
{
  "postUrls": ["https://www.reddit.com/r/AskReddit/comments/1xuraoz/what_animal_do_you_think_could_successfully_take/"],
  "commentSort": "top",
  "maxComments": 500,
  "expandThreads": true
}
```

### Example: only substantial, positively-scored replies

```json
{
  "postUrls": ["https://www.reddit.com/r/AskScience/comments/1abc123/why_is_the_sky_blue/"],
  "minScore": 5,
  "minWordCount": 15,
  "excludeDeleted": true
}
```

### Example: top-level comments from one author across two posts

```json
{
  "postUrls": [
    "https://www.reddit.com/r/technology/comments/1xyz789/post_one/",
    "https://old.reddit.com/r/technology/comments/1xyz790/post_two/"
  ],
  "maxDepth": 0,
  "authorFilter": "throwaway",
  "maxComments": 500
}
```

## Use cases

- **Sentiment and discourse research**: pull every reply to a thread to study how a community reacted to an announcement or news post.
- **Moderation audits**: use `excludeDeleted` and `authorFilter` to review what a specific user posted before their comments were removed.
- **Dataset building**: filter by `minWordCount` to collect substantive comments for training or evaluating language models.
- **Brand and product monitoring**: track replies mentioning a product name with `keywordFilter` across multiple relevant threads.
- **Thread archiving**: capture a full comment tree, including depth and parent IDs, before a thread is locked or archived.

## Data source and reliability

The actor reads the public www.reddit.com new-UI pages as a logged-out visitor. Anonymous Reddit `.json` endpoints currently return HTTP 403, so the actor loads the rendered page, its internal `more-comments` partials and its "continue this thread" pages, and parses the `<shreddit-comment>` markup. It never needs a Reddit account, cookie, API key or proxy setup: it opens a direct connection first and automatically moves through the available Apify proxy routes when Reddit blocks it.

When `enrichFromArchive` is enabled, the actor also queries the public Arctic Shift ID-lookup API in batches of up to 500 IDs. No key or account is needed. The lookup is optional and non-fatal: if it is slow, rate-limited or unavailable, the actor logs a warning, leaves page data untouched and continues.

To keep a single post from consuming an unbounded run, the actor stops after 500 partial/continue requests or 20,000 unique comments per post, whichever comes first. When either cap stops expansion, the post record keeps `more_comments_count` and a coverage record names the cap.

## FAQ

**Does this need a Reddit account or login?**
No. It reads the same public comment pages a logged-out visitor sees, so only posts and comments visible without logging in can be collected.

**Why are some comments missing from my results?**
Deleted or removed comments, comments beyond `maxComments`, comments under an unexpanded "load more" link (when `expandThreads` is off), and comments Reddit counts in `num_comments` but no longer serves to logged-out visitors will not appear. Your score, depth, age, author, keyword or word-count filters can also remove comments that were successfully scraped. A coverage record names the reason when the kept count is below Reddit's reported total.

**Why is `awards_count` present but there is no award list?**
Reddit's logged-out pages expose only the number of awards and one representative award button. The complete award names, counts and legacy gilding are not rendered without a login. Enable `enrichFromArchive` to ask the public Arctic Shift archive for `awards`, `gildings` and `total_awards_received`; the page's `awards_count` remains authoritative and the provenance fields tell you which values came from the archive. Archive award data is often sparse for very recent posts.

**What does `enrichFromArchive` add?**
It asks the public Arctic Shift archive for static fields that the logged-out page does not render: author fullname, subreddit author flair, award/gilding detail, distinguished status, archived/locked flags and removal category. It never replaces a value the page supplied, and it adds `enrichment_source`, `enrichment_fields` and `archive_retrieved_utc` so you can tell archive values apart.

**What does `maxDepth: 0` give me?**
Only comments posted directly on the post itself, with no replies-to-replies.

**How is `keywordFilter` different from a normal search?**
It is a plain, case-insensitive substring match against the comment body. Prefixing the value with `!` inverts it, so `!spam` keeps everything except comments mentioning "spam".

**Why is a field missing on some comment or post records?**
Fields Reddit does not expose for that record (for example `edited_at` on a comment that was never edited) are left out of the record instead of being written as null or empty.

**What are the camelCase records in my dataset?**
`recordType: "error"` and `recordType: "coverage"` rows are diagnostics. Normal comment and post rows use snake_case. Filter them out with `recordType` if you only want content rows.

**Can I scrape a subreddit's whole post list, not just comments?**
No, this actor only works from direct post URLs you supply; it does not crawl subreddit listings.

**Does `old.reddit.com` vs `www.reddit.com` in my input matter?**
No, either form works — `post_url` in the output is normalized to the `www.reddit.com` form regardless of which you paste in.

**Is this affiliated with Reddit?**
No. This is an independent tool that reads Reddit's public comment pages and is not operated by or affiliated with Reddit, Inc.

## Limitations

- Reddit does not render the complete award list, legacy gilding, `ups`/`downs`, post-author flair on every surface, score-hidden reasons, or every moderation field to logged-out visitors. Direct fields are omitted rather than guessed; enable `enrichFromArchive` for the static subset the archive still holds.
- Archive enrichment is best-effort. Arctic Shift snapshots can lag, and its award/gilding payload is often empty for recent posts. Provenance fields identify what was filled; page values are never replaced.
- `gallery_images` covers the images Reddit renders in the initial server response (typically the first few gallery pages), not necessarily every image in a large gallery.
- Video metadata depends on Reddit rendering `<shreddit-player>` and its packaged-media JSON; the HLS URL can expire, while `video_mp4_url` is a point-in-time fallback.
- Crosspost fields are emitted only when Reddit renders a nested crosspost container; some crosspost layouts expose only a link.
- `num_comments` includes removed, deleted and otherwise unserved comments. On large threads the kept count can stay below that number even after every available "load more" branch is opened; the coverage record makes the gap explicit.
- `expandThreads: false` intentionally reads only the comments rendered on the initial post page.
- The 500-request and 20,000-comment per-post caps bound runtime; raise `maxComments` does not raise those caps.
- Reddit may rate-limit or block a route during a long run. The actor retries, can escalate to the next proxy route mid-run and records a failed post as an error record, but a heavily throttled run can still return fewer rows than requested.
