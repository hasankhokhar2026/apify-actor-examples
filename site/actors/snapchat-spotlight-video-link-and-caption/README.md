# Snapchat Spotlight Video Link & Caption Downloader

A Snapchat Spotlight link on its own doesn't give you a file you can save or embed. This actor turns one or more of those links into a direct video URL alongside thumbnail, caption, creator info, and engagement counts — with AI-generated descriptions, a WebVTT transcript, comment threads, and related videos available on request. No login or cookies required.

## What this actor does

- Resolves a Spotlight link (including short `t.snapchat.com` links) into a direct, downloadable video URL
- Extracts data from JSON-LD first, Next.js Flight data second, and legacy `__NEXT_DATA__` last
- Requires an exact match for the requested snap ID, so a dead or mismatched link never returns another video
- Captures caption, creator info, and full engagement stats — shares, likes, comments, recommendations
- Preserves real zero counts instead of dropping them
- Adds AI-generated title, description, keywords and detected languages, on request
- Parses the video's WebVTT transcript into timestamped segments, on request
- Can also pull comment threads and up to 24 related Spotlight stories from the same feed
- Leaves a field out of the record when Snapchat didn't provide a value for it, rather than sending it empty

## Input

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `spotlightUrls` | string[] | Yes | — | One or more Snapchat Spotlight URLs to process |
| `includeTranscript` | boolean | No | `true` | Parse WebVTT transcript into timestamped segments |
| `includeAiMetadata` | boolean | No | `true` | Include LLM title, description, keywords, context cards, detected languages |
| `includeComments` | boolean | No | `false` | Decode comment threads from the page |
| `includeRelatedStories` | boolean | No | `false` | Include up to 24 related Spotlight stories |
| `proxyConfiguration` | object | No | — | Optional proxy settings |

### Supported URL Formats

```
https://www.snapchat.com/spotlight/{id}
https://snapchat.com/spotlight/{id}
https://www.snapchat.com/@{username}/spotlight/{id}
https://www.snapchat.com/t/{id}
https://story.snapchat.com/o/{id}
https://story.snapchat.com/s/{id}
https://t.snapchat.com/{code}
```

All forms are normalized to a canonical Spotlight URL. Short links (`t.snapchat.com`) are resolved automatically before scraping, and duplicate snap IDs are skipped within a run.

## Output Fields

### Core Fields

`snapId`, `inputUrl`, `videoUrl`, `availability`, and `scrapedAt` are always present on success. The remaining fields are emitted when the current JSON-LD/Flight/legacy payload exposes them.

| Field | Type | Description |
|-------|------|-------------|
| `snapId` | string | Unique Spotlight snap identifier |
| `inputUrl` | string | The URL you provided as input |
| `videoUrl` | string | Direct CDN video URL |
| `availability` | string | `available`, `restricted`, `unavailable`, or `unknown` |
| `thumbnailUrl` | string | Thumbnail image URL |
| `caption` | string | Caption or description text on the snap |
| `creatorUsername` | string | Creator's Snapchat username |
| `profileUrl` | string | Full profile URL (`snapchat.com/@username`) |
| `creatorDisplayName` | string | Creator's display name |
| `durationSeconds` | number | Video duration in seconds |
| `uploadedAt` | string | ISO 8601 upload timestamp |
| `scrapedAt` | string | ISO 8601 timestamp of when this record was collected |
| `shareCount` | integer | Number of times the video was shared |
| `commentCount` | integer | Number of comments |
| `likeCount` | integer | Number of likes (boosts) |
| `recommendCount` | integer | Number of recommendations |
| `mediaPreviewUrl` | string | Preview/thumbnail variant URL (legacy page data only) |
| `width` | integer | Video width in pixels (video snaps only) |
| `height` | integer | Video height in pixels (video snaps only) |
| `restricted` | boolean | Whether Snapchat marks the content as age- or region-restricted |
| `isAttributed` | boolean | Whether Snapchat attributes the snap to a creator account rather than an unattributed feed item |

> `viewCount` is omitted for very recent videos — Snapchat returns -1 as a sentinel value for posts still accumulating views.

### AI Metadata (when `includeAiMetadata: true`)

| Field | Type | Description |
|-------|------|-------------|
| `llmTitle` | string | AI title when the page exposes it (legacy pages) |
| `llmDescription` | string | AI description when the page exposes it |
| `llmKeywords` | string[] | Keyword tags from the page metadata |
| `textMetadataKeywords` | string[] | Text-based keyword tags (legacy page data only) |
| `hashtags` | string[] | Hashtags associated with the snap |
| `contextCards` | object[] | Context cards shown on the snap (sound info, creator card, etc.) |
| `detectedLanguages` | object[] | Detected languages with confidence scores (legacy page data only) |

### Transcript (when `includeTranscript: true`)

| Field | Type | Description |
|-------|------|-------------|
| `transcript` | object[] | Array of `{startTime, endTime, text}` WebVTT segments |
| `transcriptUrl` | string | URL of the raw WebVTT transcript file |

### Comments (when `includeComments: true`, up to 500 via the public cursor API)

Each item in `comments[]`:

| Field | Type | Description |
|-------|------|-------------|
| `commentId` | string | Unique comment identifier |
| `snapId` | string | ID of the snap this comment belongs to |
| `replyText` | string | Comment text |
| `reactionCounts` | object[] | Array of `{reactTypeId, count}` reaction tallies |
| `commenterDisplayName` | string | Commenter's display name |
| `approvalState` | any | Moderation approval state |
| `postedAt` | string | ISO 8601 timestamp when the comment was posted |

### Related Stories (when `includeRelatedStories: true`)

Each item in `relatedStories[]`:

| Field | Type | Description |
|-------|------|-------------|
| `thumbnailUrl` | string | Thumbnail URL of the related story |
| `storyPageUrl` | string | Full Spotlight URL of the related story |
| `durationSeconds` | number | Duration of the related story in seconds |
| `creatorUsername` | string | Creator's username |
| `caption` | string | Related story caption when present |

### Error Records

If a URL fails, an error record is saved instead of a video record:

| Field | Type | Description |
|-------|------|-------------|
| `inputUrl` | string | The URL that failed |
| `snapId` | string | Snap ID if it could be extracted |
| `error` | string | Human-readable error message |
| `availability` | string | `unavailable` when the snap was not found, `unknown` for fetch/parse failures |
| `scrapedAt` | string | ISO 8601 timestamp |

A dead, deleted, or mismatched link returns an `unavailable` record with the requested `snapId` and no `videoUrl`; the actor never substitutes a different video.

## Example Input

```json
{
  "spotlightUrls": [
    "https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYZmRwYmVqcm5wAZ8Kxg_vAZ8Kxgn9AAAAAQ",
    "https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYZG5iaHJuY2phAZ8KF10GAZ8KETc1AAAAAQ"
  ],
  "includeTranscript": true,
  "includeAiMetadata": true,
  "includeComments": false,
  "includeRelatedStories": false
}
```

## Example Output

```json
{
  "snapId": "W7_EDlXWTBiXAEEniNoMPwAAYZG5iaHJuY2phAZ8KF10GAZ8KETc1AAAAAQ",
  "inputUrl": "https://www.snapchat.com/spotlight/W7_EDlXWTBiXAEEniNoMPwAAYZG5iaHJuY2phAZ8KF10GAZ8KETc1AAAAAQ",
  "availability": "available",
  "videoUrl": "https://bolt-gcdn.sc-cdn.net/v/udlVbjK0wdjHbPx1FRph0.27.IRZXSOY?...",
  "thumbnailUrl": "https://bolt-gcdn.sc-cdn.net/v/udlVbjK0wdjHbPx1FRph0.256.IRZXSOY?...",
  "caption": "Another Spotlight Snap brought to you by Snapchat",
  "creatorUsername": "waqarzaka",
  "profileUrl": "https://www.snapchat.com/@waqarzaka",
  "creatorDisplayName": "Waqar Zaka",
  "durationSeconds": 130.23,
  "width": 540,
  "height": 960,
  "shareCount": 0,
  "likeCount": 3,
  "commentCount": 0,
  "recommendCount": 0,
  "uploadedAt": "2026-06-27T17:12:08.245000+00:00",
  "scrapedAt": "2026-06-28T06:43:34.588497+00:00",
  "isAttributed": true,
  "textMetadataKeywords": ["bitcoin", "hacker", "crypto", "cryptocurrency", "blockchain"],
  "contextCards": [
    {
      "contextType": 3,
      "title": "Waqar Zaka",
      "subtitle": "waqarzaka",
      "url": "https://www.snapchat.com/@waqarzaka",
      "thumbnailType": 0,
      "hasBadge": true,
      "id": "36d0088b-39d5-4765-a237-bb147a292272"
    }
  ],
  "detectedLanguages": [
    { "languageCode": "hi", "score": 0.910262405872345 }
  ]
}
```

## FAQ

**Does this require a Snapchat account or cookies?**
No. All data is extracted from public Snapchat Spotlight pages. No login, no cookies, and no proxy are required in most regions.

**Do video URLs expire?**
There is no fixed expiry that this actor relies on or promises. The returned URL is the CDN URL Snapchat served at scrape time; Snapchat can rotate, restrict, or remove it at any time. Save the file promptly if you need a durable copy.

**Why is `viewCount` missing from some records?**
Snapchat returns -1 as a sentinel for videos that are too new to have an accurate view count. The actor omits this field rather than storing a misleading -1. A real zero is kept as `0`.

**Are `width` and `height` always present?**
Only for video snaps. Some Spotlight posts are images or have incomplete metadata, in which case these fields are absent.

**Can I scrape a large batch of URLs at once?**
Yes. Provide all URLs in the `spotlightUrls` array. The actor processes them sequentially with a short delay between requests to stay respectful of rate limits. Duplicate snap IDs are skipped after normalization.

**What is the `isAttributed` flag?**
When `true`, Snapchat attributes the snap to a creator account. When absent, Snapchat did not expose the flag.

**What happens when a link is dead or points to a removed snap?**
The actor verifies the requested snap ID against the page data. If it cannot find that exact ID, it writes an `availability: "unavailable"` record with the error message and no `videoUrl`. It never returns a different video.

**What does `availability` mean?**
`available` means a video URL was returned. `restricted` means the page only exposed restricted content. `unavailable` means the exact snap was not found. `unknown` means a fetch or parse failure prevented a decision. `restricted: true` means Snapchat marks the content as age- or region-restricted.

**Can I get comments and transcripts from all videos?**
Set `includeComments` and/or `includeTranscript`. Comments and WebVTT transcripts are only returned when Snapchat exposes them for that snap. Related stories are limited to the first 24 usable entries.

**Is this affiliated with Snapchat?**
No. This is an independent data extraction tool and has no connection to Snap Inc.

## Limits

- Public Spotlight pages only; no login, cookies, private profiles, or Stories.
- The requested snap ID must appear in the page data. There is no "first video on the page" fallback.
- JSON-LD, Flight, and legacy `__NEXT_DATA__` layouts are supported, but Snapchat can change them at any time.
- Comments, transcripts, AI metadata, and related stories depend on what Snapchat includes for each snap.
- Short links are resolved over the network; a dead short link becomes an `unavailable` record.
- CDN URLs are not guaranteed to remain valid after collection.
