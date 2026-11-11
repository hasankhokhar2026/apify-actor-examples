# TikTok Video, Audio & Cover Downloader

Download TikTok posts as **clean no-watermark MP4**, watermarked MP4, sound, cover images, slideshow frames, and post metadata. Each file can be re-hosted in Apify Key-Value Store with a stable public link, and every input gets a dataset row — including posts that are deleted, private, region-blocked, age-gated, duplicated, or too large to download.

No TikTok account, cookies, API key, or proxy setup is required.

## What you get

- One row per asset: video variant, audio, cover, slideshow frame, or metadata
- Explicit status rows instead of silent skips
- Clean MP4 (no watermark) downloaded inside the page session and re-hosted to Apify storage
- Watermarked MP4, covers, audio, and slideshow images returned as stable KV links and/or expiring CDN URLs
- Resolution-first quality selection (`best`, `1080p`, `720p`, `540p`, `360p`, `smallest`)
- Post and author metadata: caption, create time, stats, sound details, post type
- Short-link support (`vm.tiktok.com`, `vt.tiktok.com`, `/t/`) and embed/bare-ID inputs
- Duplicate detection, `maxItems`, `maxFileSizeMb`, and 1–3 way concurrency

## How it works

TikTok exposes two different media paths, and this actor uses both:

1. **Embed fast path** — the public embed page returns the watermarked MP4, cover, sound, slideshow images, author, stats, and caption without a browser or login.
2. **Browser page session** — the clean `playAddr` URL is bound to first-party cookies from the same page load and returns `403` when fetched outside that session. The actor opens the post in Chromium, downloads the selected clean stream inside the session, and stores it in Apify Key-Value Store so the output link keeps working.

Watermarked and direct assets are downloaded to Key-Value Store when `downloadToKv` is `true`. When it is `false`, their source URLs are returned instead. Clean video is always downloaded and re-hosted because a bare source URL would not work for you.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `postUrls` | array of strings | required | Canonical post URLs, short links, embed URLs, or numeric post IDs. Duplicates are processed once. |
| `assetTypes` | multi-select | `["video"]` | `video`, `audio`, `cover`, `slideshow`, `metadata`. |
| `videoVariant` | select | `clean` | `clean`, `watermarked`, or `both`. |
| `quality` | select | `best` | `best` sorts by resolution then bitrate. `1080p`, `720p`, `540p`, `360p`, `smallest` target the closest available stream. Watermarked copies are single-resolution. |
| `downloadToKv` | boolean | `true` | Store watermarked video, audio, cover, and slideshow files and return `kvsUrl`. Clean video is always stored. |
| `maxFileSizeMb` | integer | `100` | Per-file cap (1–100 MB). Larger files produce a `too_large` row. |
| `maxItems` | integer | `1000` | Maximum unique posts to process (1–1000). Extra inputs get a `limit_reached` row. |
| `maxConcurrency` | integer | `3` | Posts processed in parallel (1–3). |
| `proxyConfiguration` | object | none | Optional. The actor uses a direct connection by default. |

### Example — one clean video at 540p

```json
{
  "postUrls": ["https://www.tiktok.com/@nba/video/7693329153680035102"],
  "assetTypes": ["video"],
  "videoVariant": "clean",
  "quality": "540p",
  "downloadToKv": true,
  "maxItems": 1
}
```

### Example — both video variants, cover, and metadata

```json
{
  "postUrls": ["https://www.tiktok.com/@nba/video/7693329153680035102"],
  "assetTypes": ["video", "cover", "metadata"],
  "videoVariant": "both",
  "quality": "720p",
  "downloadToKv": true
}
```

### Example — slideshow frames and sound

```json
{
  "postUrls": ["https://www.tiktok.com/@khaby.lame/photo/7574844184952081686"],
  "assetTypes": ["slideshow", "audio", "metadata"],
  "downloadToKv": true
}
```

### Example — URL-only mode for direct assets

```json
{
  "postUrls": ["https://www.tiktok.com/@nba/video/7693329153680035102"],
  "assetTypes": ["audio", "cover"],
  "downloadToKv": false
}
```

## Output

Each dataset row contains the non-empty fields that apply:

- `postId`, `postUrl`, `postType`
- `assetType`: `video`, `audio`, `cover`, `slideshow`, `metadata`, or `post` for post-level status rows
- `variant`: `clean` or `watermarked` for video
- `quality`: selected quality label
- `ordinal`: slideshow frame index
- `mimeType`, `byteSize`, `width`, `height`, `duration`
- `kvsKey`, `kvsUrl` for stored files
- `originalUrl`, `expiresAt` for the source CDN URL
- `downloadedAt`, `requiresSession`
- `status`, `error`
- Metadata rows add `caption`, `createTime`, author fields, play/like/comment/share/collect counts, music fields, and `imageCount`

### Status values

| Status | Meaning |
|---|---|
| `ok` | At least one requested asset or metadata row delivered |
| `not_found` | Deleted, removed, or unavailable post |
| `private` | Private account or friends-only post |
| `region_blocked` | Not available in the current region |
| `login_required` | Age-gated or login-gated post |
| `blocked` | TikTok bot wall or rate limit after retries |
| `unsupported_url` | Input is not a recognizable TikTok post |
| `short_link_dead` | Short link redirected to a homepage/profile, not a post |
| `no_video` | Video requested for a slideshow post |
| `no_slideshow` | Slideshow requested for a video post |
| `no_audio` | No sound track exposed |
| `no_cover` | No cover image exposed |
| `no_assets` | Post resolved but none of the requested assets were available |
| `download_failed` | CDN download or Key-Value Store write failed |
| `too_large` | File exceeds `maxFileSizeMb` |
| `duplicate` | Same post ID appeared earlier in the input |
| `limit_reached` | `maxItems` cap reached before this input was processed |

## URL expiry and storage

- TikTok CDN URLs (`originalUrl`) are signed and expire in **about 48 hours** (some music URLs expire within 24 hours). They are useful for traceability, not long-term hosting.
- `kvsUrl` points to the run's Apify Key-Value Store and lasts for that store's retention period. Download important files to your own storage.
- Clean video source URLs only work with the extracting page session (`requiresSession: true`). That is why the actor always downloads and re-hosts clean video instead of selling a bare URL.

## Limits and behaviour

- **Caps:** 1–1000 posts per run, 3 concurrent posts, 100 MB per file.
- **Deduplication:** the first occurrence of a post ID is processed; later occurrences get a `duplicate` row.
- **Clean video:** requires a browser session; if the page is blocked, the actor returns a status row for the clean asset while still delivering metadata/watermarked assets when the embed fast path succeeded.
- **Region, private, and age-gated posts:** no login and no user cookies are used. Posts that require either are reported with a status row rather than silently omitted.
- **Field drift:** the parser accepts both `imagePost.images` (modern page data) and `imagePostInfo.displayImages` (embed/legacy), and MIME types are taken from the CDN response rather than assumed.
- **Watermarked resolution:** TikTok exposes one watermarked copy per post, so `quality` affects clean video only.

## FAQ

**Do I need a TikTok account or cookies?**
No. The actor uses public pages and browser-generated first-party cookies only.

**Why can't I get a no-watermark URL without downloading?**
TikTok's clean `playAddr` returns `403 text/html` unless it is fetched with cookies from the same page session. The actor downloads the file in that session and re-hosts it.

**How long do links stay valid?**
`kvsUrl` lasts for the Key-Value Store retention period. `originalUrl` is a signed CDN URL that expires in about 48 hours.

**What happens to posts that cannot be downloaded?**
They produce a status row with `status` and `error`, so you can audit the run instead of diffing post IDs.

**Are short links supported?**
Yes. `vm.tiktok.com`, `vt.tiktok.com`, and `/t/` links are resolved with an HTTP redirect. A dead link gets `short_link_dead`.

**Can I use a proxy?**
It is optional. The actor is direct by default. If you want to route requests through Apify Proxy, select a proxy configuration in the input.

**Why is a clean video row missing on a slideshow?**
Slideshows have no video file. Request `slideshow` or `audio` instead; a `no_video` status row is emitted when video is requested.

**Is this affiliated with TikTok?**
No. It is an independent tool for publicly available TikTok media. Only download content you have the right to use.
