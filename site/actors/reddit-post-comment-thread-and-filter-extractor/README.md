# Reddit Post Comment Thread & Filter Extractor

Paste in one or more Reddit post links and get every comment on that thread as a flat dataset row, in the order the thread tree expands collapsed replies. A companion record with the post's own stats is added for each URL, and a set of optional filters lets you narrow a huge thread down to only the comments worth reading before you export anything.

## What this actor does

- Loads each Reddit post you give it and opens collapsed "load more" and "continue this thread" sections so deep replies are not left out.
- Returns every comment with its author, text, score, nesting depth, and the ID of the comment it replies to, so you can rebuild the thread tree.
- Captures awards, gilding, controversiality, distinguished (mod/admin) status and user flair for each comment, when Reddit shows them.
- Applies any score, depth, author, keyword or word-count rule you set, dropping non-matching comments before they reach the dataset.
- Omits any field Reddit did not provide for a given comment or post, instead of writing a blank or null value.

## Output per record

Each run produces one post-metadata record per URL and one record per comment that passed your filters.

### Post metadata record

| Field | Description |
| --- | --- |
| recordType | Always `post` for this record type |
| post_id | Reddit's post ID |
| post_name | Fullname in Reddit's `t3_<id>` format |
| title | Post title |
| author | Username of the poster |
| author_fullname | Poster's Reddit fullname ID |
| subreddit | Subreddit name without the `r/` prefix |
| subreddit_prefixed | Subreddit name with `r/` prefix |
| domain | Link domain for link posts (e.g. `self.programming`) |
| score | Post score (upvotes minus downvotes) |
| num_comments | Total comment count reported by Reddit |
| permalink | Full URL of the post |
| url | Same as permalink |
| selftext | Post body text, for text posts |
| selftext_html | Post body as HTML, for text posts |
| link_flair | Post flair text, if the subreddit uses flairs |
| is_self | True for text posts |
| is_stickied | True if the post is pinned |
| is_nsfw | True if marked over-18 |
| is_spoiler | True if marked as a spoiler |
| is_original_content | True if flagged as OC |
| is_locked | True if comments are locked |
| is_archived | True if the post is archived |
| more_comments_count | Count of "load more" links Reddit still showed after expansion |
| comment_sort | Comment sort order active on the page (e.g. `best`, `top`) |
| created_utc | Post creation time as a Unix timestamp |
| created_at | Post creation time as an ISO 8601 datetime |

### Comment record

| Field | Description |
| --- | --- |
| recordType | Always `comment` for this record type |
| comment_id | Reddit's comment ID |
| comment_name | Fullname in Reddit's `t1_<id>` format |
| author | Username of the commenter, or `[deleted]` |
| author_fullname | Commenter's Reddit fullname ID |
| text | Comment body text |
| body_html | Comment body as HTML |
| score | Comment score (upvotes minus downvotes) |
| permalink | Direct link to the comment |
| post_url | URL of the post the comment belongs to |
| depth | Nesting level in the thread (0 = top-level reply to the post) |
| parent_comment_id | ID of the comment this one replies to, when it is not top-level |
| replies_count | Number of direct replies visible under this comment |
| subreddit | Subreddit the post belongs to |
| subreddit_prefixed | Subreddit with the `r/` prefix |
| is_op | True if the commenter is the post's original author |
| is_edited | True if the comment was edited after posting |
| edited_at | Edit timestamp, when Reddit discloses one |
| is_stickied | True if the comment is pinned by a moderator |
| is_collapsed | True if the comment was shown collapsed on the page |
| is_deleted | True if the comment body or author shows as deleted/removed |
| is_automod | True if posted by AutoModerator |
| is_likely_bot | True if the author name matches a common bot-naming pattern |
| comment_age_seconds | Seconds between posting and the time the comment was scraped |
| distinguished | Moderator/admin distinguish tag, when present |
| controversiality | Reddit's controversiality flag for the comment |
| user_flair | Commenter's subreddit flair text |
| word_count | Whitespace-separated word count of the comment body |
| body_quote_count | Number of quote blocks in the comment body |
| body_code_count | Number of code blocks in the comment body |
| body_link_count | Number of links in the comment body |
| awards | List of award objects (`name`, `icon`) the comment received |
| awards_count | Total number of awards received |
| gilded_count | Number of times the comment was gilded |
| created_utc | Comment creation time as a Unix timestamp |
| created_at | Comment creation time as an ISO 8601 datetime |

## Input

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `postUrls` | array | – | Reddit post URLs to scrape comments from (required) |
| `maxComments` | integer | `100` | Maximum number of comments to collect per post, 1-10000 |
| `expandThreads` | boolean | `true` | Click "load more" and "continue this thread" to reveal collapsed replies |
| `minScore` | integer | – | Drop comments scoring below this number |
| `maxDepth` | integer | – | Drop comments nested deeper than this (0 keeps only top-level replies) |
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

## FAQ

**Does this need a Reddit account or login?**
No. It reads the public comment pages the same way a logged-out visitor would, so only posts and comments visible without logging in can be collected.

**Why are some comments missing from my results?**
Deleted or removed comments, comments beyond `maxComments`, and comments beneath unexpanded "load more" links (when `expandThreads` is off) will not appear. Your score, depth, author, keyword or word-count filters can also remove comments that were successfully scraped.

**What does `maxDepth: 0` give me?**
Only comments posted directly on the post itself, with no replies-to-replies.

**How is `keywordFilter` different from a normal search?**
It is a plain, case-insensitive substring match against the comment body. Prefixing the value with `!` inverts it, so `!spam` keeps everything except comments mentioning "spam".

**Why is a field missing on some comment or post records?**
Fields Reddit does not expose for that record (for example `edited_at` on a comment that was never edited) are left out of the record instead of being written as null or empty.

**Can I scrape a subreddit's whole post list, not just comments?**
No, this actor only works from direct post URLs you supply; it does not crawl subreddit listings.

**Does `old.reddit.com` vs `www.reddit.com` in my input matter?**
No, either form works — `post_url` in the output is normalized to the `www.reddit.com` form regardless of which you paste in.

**Is this affiliated with Reddit?**
No. This is an independent tool that reads Reddit's public comment pages and is not operated by or affiliated with Reddit, Inc.
