# YouTube Video Comment & Reply Thread Scraper

Give this actor a list of YouTube video links and it pulls their comment sections — top-level comments with their nested reply threads attached, author identity, like counts, and the pinned/hearted/verified flags that signal which comments the creator actually engaged with.

## What this actor does

- **Comments and replies:** top-level threads with nested replies
- **Sorting:** top comments or newest first
- **Engagement:** like counts, reply counts, pinned and hearted flags
- **Author data:** name, channel URL, and channel ID
- **Empty fields are omitted** — records only contain values that are actually populated.

## Output


Each dataset row is a top-level comment (`replyDepth: 0`). When `includeReplies` is enabled and a comment has replies, they're embedded in that row's `replies` field — an array of reply objects (`replyDepth: 1`, same shape as a comment row, plus `parentCommentId`) — rather than being pushed as separate top-level rows of their own.

| Field | Type | Description |
|-------|------|-------------|
| `commentId` | string | Unique comment identifier |
| `text` | string | Comment text content |
| `authorName` | string | Author's display name |
| `authorChannelId` | string | Author's YouTube channel ID |
| `authorChannelUrl` | string | Author's channel URL |
| `authorProfileImageUrl` | string | Author's profile image URL |
| `authorIsChannelOwner` | boolean | Whether the author is the video's channel owner |
| `likeCount` | integer | Number of likes on the comment |
| `replyCount` | integer | Number of replies (always `0` on reply objects themselves; only meaningful on top-level comments) |
| `replyCountText` | string | Reply count as text, e.g. `"963"` (present on top-level comments only; a bare number, not a formatted phrase) |
| `publishedTimeText` | string | Relative publish time (e.g., "2 days ago") |
| `commentUrl` | string | Direct link to the comment (`https://www.youtube.com/watch?v=VIDEO_ID&lc=COMMENT_ID`) |
| `isHearted` | boolean | Whether the creator hearted this comment |
| `isPinned` | boolean | Whether this comment is pinned |
| `isVerifiedAuthor` | boolean | Whether the author's channel is verified |
| `isCreator` | boolean | Alias for `authorIsChannelOwner` |
| `isArtist` | boolean | Whether the author is a YouTube Music artist |
| `isReply` | boolean | Whether this is a reply (true) or top-level comment (false) |
| `parentCommentId` | string | Parent comment ID (present only on reply objects, absent on top-level comments) |
| `replyDepth` | integer | 0 for top-level comments, 1 for replies |
| `videoId` | string | YouTube video ID |
| `videoUrl` | string | Full video URL |
| `videoTitle` | string | Video title |
| `videoChannelName` | string | Video channel name |
| `videoChannelId` | string | Video channel ID |
| `videoViewCount` | integer | Video's total view count |
| `videoPublishedDate` | string | Video's absolute publish date (e.g., "Oct 24, 2009") |
| `videoDescription` | string | Video's full description text |
| `totalCommentCount` | integer | Video's total comment count (present when available) |
| `scrapedAt` | string | ISO 8601 timestamp of when the data was scraped |
| `replies` | array | Nested reply objects (present only on top-level comment rows, only when `includeReplies=true` and the comment has replies) |

### Example Output

```json
{
    "commentId": "UgxB...",
    "text": "Great video!",
    "authorName": "John Doe",
    "authorChannelId": "UCxxx...",
    "authorChannelUrl": "https://www.youtube.com/@johndoe",
    "authorProfileImageUrl": "https://yt3.ggpht.com/...",
    "authorIsChannelOwner": false,
    "likeCount": 42,
    "replyCount": 3,
    "publishedTimeText": "2 days ago",
    "isHearted": false,
    "isPinned": false,
    "isReply": false,
    "replyDepth": 0,
    "videoId": "dQw4w9WgXcQ",
    "videoUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "videoTitle": "Rick Astley - Never Gonna Give You Up",
    "videoChannelName": "Rick Astley",
    "videoChannelId": "UCuAXFkgsw1L7xaCfnd5JJOw",
    "videoViewCount": 1811547602,
    "videoPublishedDate": "Oct 24, 2009",
    "videoDescription": "The official video for \"Never Gonna Give You Up\" by Rick Astley...",
    "totalCommentCount": 2400000,
    "scrapedAt": "2026-02-11T12:00:00.000000+00:00",
    "replies": [
        {
            "commentId": "UgxB....AbCdEfGhIj",
            "text": "I agree!",
            "authorName": "Jane Smith",
            "likeCount": 5,
            "publishedTimeText": "1 day ago",
            "isReply": true,
            "parentCommentId": "UgxB...",
            "replyDepth": 1,
            "commentUrl": "https://www.youtube.com/watch?v=dQw4w9WgXcQ&lc=UgxB....AbCdEfGhIj"
        }
    ]
}
```

Each reply object actually carries the full same field set as a top-level comment row (all author fields — `authorChannelId`, `authorChannelUrl`, `authorProfileImageUrl`, `authorIsChannelOwner`, `isVerifiedAuthor`, `isCreator`, `isArtist`, `isHearted`, `isPinned` — plus the full `video*` context block), not just the trimmed set shown above; the example above only highlights the fields that differ meaningfully from a top-level comment. The one exception is `totalCommentCount`, which is present on top-level comments but never on reply objects.

### Error Handling

If a video URL can't be parsed, doesn't resolve to a real video, has comments disabled, or fails to fetch, the actor pushes a single marker row instead of comment rows — so failures are visible in the dataset instead of silently producing nothing. Marker rows use `success` (boolean) and `error` (a human-readable message) instead of comment fields. `inputUrl` is the original raw input string only when the URL couldn't be parsed at all; for every other case (video not found, comments disabled, fetch failure, zero matches) it's the normalized/canonical video URL, since parsing already succeeded by that point:

| Case | `success` | `commentsDisabled` | Other fields |
|------|-----------|---------------------|--------------|
| URL couldn't be parsed into a video ID | `false` | `false` | No `videoId`/video metadata (never resolved far enough to have any) |
| Video ID doesn't resolve to a real page (deleted, never existed) | `false` | `false` | `videoId`/`videoUrl` present, but `videoTitle` and other video metadata are empty |
| Video exists, comments are disabled | `false` | `true` | Full video metadata (`videoTitle`, `videoViewCount`, etc.) is present |
| Video page/comments fetch failed (bot detection, network error) | `false` | `false` | `videoId`/`videoUrl` present; video metadata depends on how far the fetch got |
| Comments enabled but the video has zero (or zero matching your filters) | `true` | `false` | `commentCount: 0`, full video metadata present |

## Input


| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `videoUrls` | array | – | YouTube video URLs, short links (youtu.be), shorts URLs, or plain video IDs. Required. |
| `maxComments` | integer | 100 | Max top-level comments per video (1–50,000). Replies don't count toward this limit |
| `includeReplies` | boolean | true | Whether to fetch reply threads for each comment |
| `maxRepliesPerComment` | integer | 5 | Max replies to fetch per comment (0–100) |
| `sortBy` | string | "top" | Sort order: "top" (most relevant) or "newest" (chronological) |
| `commentKeywordFilter` | string | *(none)* | Only return comments/replies whose text contains this word or phrase (case-insensitive) |
| `minLikeCount` | integer | 0 | Only return comments/replies with at least this many likes |

### Supported URL Formats

- `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- `https://youtu.be/dQw4w9WgXcQ`
- `https://www.youtube.com/shorts/dQw4w9WgXcQ`
- `https://www.youtube.com/embed/dQw4w9WgXcQ`
- `https://www.youtube.com/live/dQw4w9WgXcQ`
- `https://www.youtube.com/v/dQw4w9WgXcQ`
- `dQw4w9WgXcQ` (bare video ID)

Extra query parameters (`&t=30s`, `&si=...`, etc.) and domain casing are both ignored — only the video ID is used. If the same video appears more than once (even in a different URL format), only the first occurrence is scraped; later duplicates are skipped. Within a single video, YouTube can also resurface the same comment more than once during pagination (most commonly a pinned comment, which appears both in its pinned slot and again in its normal chronological position) — the actor tracks comment IDs already returned and skips re-pushing them, so the dataset never contains duplicate comment rows for the same video.

### Example Input

```json
{
    "videoUrls": [
        "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    ],
    "maxComments": 100,
    "includeReplies": true,
    "maxRepliesPerComment": 5,
    "sortBy": "top"
}
```

## Examples

### Example: top comments

```json
{
  "videoUrls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
  "maxComments": 100,
  "sortBy": "top"
}
```

### Example: newest with replies

```json
{
  "videoUrls": ["https://www.youtube.com/watch?v=9bZkp7q19f0"],
  "maxComments": 50,
  "sortBy": "newest",
  "includeReplies": true,
  "maxRepliesPerComment": 5
}
```

## Use cases

- **Brand sentiment tracking** — pull comments on a product review or launch video to gauge audience reaction.
- **Creator engagement audits** — compare like counts and reply volume on top comments across competing channels.
- **Pinned-comment monitoring** — catch a creator's pinned announcement, discount code, or correction as soon as it's posted.
- **Moderation and toxicity research** — assemble comment and reply datasets for training or evaluating content-moderation models.
- **Audience Q&A mining** — scan high-traffic videos for recurring viewer questions worth addressing in future content.
- **Discourse analysis** — reconstruct full reply chains under a comment to study how a conversation developed.

## FAQ


**Why are some comments missing?**
YouTube loads comments page by page, and on very large videos it may stop serving further pages before every comment has been returned. The count is also limited by `maxComments`, and the keyword and like filters drop non-matching comments.

**Are replies included by default?**
Yes, when `includeReplies=true` (the default). You can set `includeReplies: false` or reduce `maxRepliesPerComment` to skip or cap reply fetching.

**Does this require a YouTube API key or cookies?**
No. The actor reads publicly available comment data and does not require any authentication, API keys, or cookies.

**What happens if a video URL is invalid or the video doesn't exist?**
The actor still produces one dataset row for that entry instead of silently skipping it, marked with `success: false` and an `error` message explaining why — see [Error Handling](#error-handling) above.

**What's the difference between `top` and `newest` sort?**
`top` returns comments in YouTube's own "Top comments" order. `newest` returns them in YouTube's "Newest first" order.

**Can I scrape comments for private or age-gated videos?**
No. Only public videos are supported. Age-gated and private videos require a logged-in session, which this actor does not use.

**How do the keyword filter and minimum like count work?**
Both are applied locally to the comments the actor already fetched — they don't change what YouTube returns, only what gets saved to the dataset. Both are checked against a top-level comment *before* deciding whether to fetch its replies: if a comment fails either filter, its replies are skipped entirely (not fetched at all, to save time) — even if some of those replies would individually have passed. Each reply that does get fetched is then checked against both filters again on its own merits.

**Is this affiliated with YouTube?**
No. This is an independent tool and is not affiliated with, endorsed by, or sponsored by YouTube or Google.
