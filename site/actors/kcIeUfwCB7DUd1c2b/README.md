# Twitter (X) Screenshot Generator

Capture clean screenshots of public X posts and profiles — **no login, no cookies, no API key**. Paste post links to get pixel-perfect post cards, or profile links to get the profile header or the full profile page. Choose dark, light or system theme, PNG/JPEG/WEBP output, and 1x–3x pixel density.

## What this actor does

- **Three capture modes:** `postCard` (one post), `profileHeader` (header + first posts) and `fullProfilePage` (the scrollable profile page)
- **Clean captures:** headers, sidebars, login prompts and community notes are hidden automatically; reply posts can be hidden too
- **Image control:** PNG, JPEG or WEBP, quality setting for JPEG/WEBP, and 1x/2x/3x pixel density
- **Custom viewport:** width and height from 320×240 up to 3840×2160
- **Optional details:** post ID, URL, author handle, text snippet, and profile or author follower counts when X shows them
- **Empty fields are omitted**

## Output per screenshot

Each row has a `type`: `screenshot` for a capture or `status` for a run message. If no post or profile link was provided at all, a single `status` row with `status: "noInput"` and a `message` field is emitted instead of the fields below.

| Field | Description |
|---|---|
| `targetUrl` | The post or profile URL that was captured |
| `targetType` | `post` or `profile` |
| `captureMode` | `postCard`, `profileHeader` or `fullProfilePage` |
| `status` | `success` or a friendly error description |
| `width`, `height` | Dimensions of the captured image in pixels |
| `format` | Saved image format (`png`, `jpeg` or `webp`) |
| `fileSizeBytes` | Size of the saved image |
| `filename` | File name in the key-value store |
| `downloadUrl` | Public signed link to download the image (omitted when signing fails) |
| `quality` | JPEG/WEBP quality setting used |
| `deviceScaleFactor` | Pixel density used for the capture (1, 2 or 3) |
| `capturedAt`, `collectedAt` | ISO timestamps of the capture |
| `profileUrl` | The profile URL, on profile captures |

With **Include post/profile details** on, post rows also carry `tweetId`, `tweetUrl`, `authorUsername`, `textSnippet`, `authorFollowers`, `authorFollowing` and `authorPostCount`; profile rows carry `username`, `name`, `followers`, `following` and `postCount`. Counts are only added when X shows them.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `postUrls` | array | – | Post links, bare post IDs, profile links or bare usernames |
| `tweetUrls` | array | – | Alias of post links |
| `profileUrls` | array | – | Profiles to capture (header or full page, depending on capture mode) |
| `captureMode` | string | `postCard` | `postCard`, `profileHeader` or `fullProfilePage`. In `postCard` mode, post links produce post cards; in `profileHeader` or `fullProfilePage` mode, post links capture the post's author profile instead |
| `theme` | string | `dark` | `dark`, `light` or `system` |
| `fullPage` | boolean | `false` | Capture the whole scrollable page instead of just the card or header |
| `hideReplies` | boolean | `true` | Hide reply posts so captures stay focused |
| `includeMetadata` | boolean | `false` | Add post/profile details and counts to each row |
| `format` | string | `png` | `png` (lossless), `jpeg` or `webp` |
| `quality` | integer | `90` | Quality for JPEG/WEBP (1–100); ignored for PNG |
| `deviceScaleFactor` | string | `1x` | `1x`, `2x` or `3x` pixel density |
| `viewportWidth` | integer | `1440` | Browser width used for the capture (320–3840) |
| `viewportHeight` | integer | `900` | Browser height used for the capture (240–2160) |
| `proxyConfiguration` | object | – | Optional, for large or repeated runs |

At least one post link or profile link is required. Any input works in any list — links, IDs and usernames are routed automatically.

### Example: post card

```json
{
  "postUrls": ["https://x.com/NASA/status/2107095768821576019"],
  "theme": "dark",
  "hideReplies": true,
  "includeMetadata": true
}
```

### Example: profile header

```json
{
  "profileUrls": ["https://x.com/apify"],
  "captureMode": "profileHeader",
  "theme": "light",
  "viewportWidth": 1280,
  "viewportHeight": 800
}
```

### Example: full profile page

```json
{
  "profileUrls": ["apify"],
  "captureMode": "fullProfilePage",
  "fullPage": true
}
```

### Example: high-density JPEG

```json
{
  "postUrls": ["2107095768821576019"],
  "format": "jpeg",
  "quality": 85,
  "deviceScaleFactor": "2x"
}
```

### Example record

```json
{
  "type": "screenshot",
  "targetUrl": "https://x.com/NASA/status/2107095768821576019",
  "targetType": "post",
  "captureMode": "postCard",
  "status": "success",
  "width": 1440,
  "height": 810,
  "format": "png",
  "fileSizeBytes": 412345,
  "filename": "screenshot_2107095768821576019.png",
  "downloadUrl": "https://api.apify.com/v2/key-value-stores/{STORE_ID}/records/screenshot_2107095768821576019.png?signature=...",
  "deviceScaleFactor": 1,
  "capturedAt": "2026-10-06T10:30:00+00:00",
  "tweetId": "2107095768821576019",
  "tweetUrl": "https://x.com/NASA/status/2107095768821576019",
  "authorUsername": "NASA",
  "textSnippet": "It's World Space Week! ..."
}
```

## Use cases

- **Social media reporting** — embed clean post captures in decks, newsletters and blogs
- **Brand monitoring** — archive screenshots of public posts as evidence
- **Community management** — capture profile pages for creator or partner reviews
- **Research** — build image datasets of public posts with consistent framing and theme
- **Content creation** — generate post images for roundups without manual screenshotting
- **Legal and compliance** — timestamped captures of public posts with source URLs

## FAQ

**Can I screenshot private accounts or posts?** No. Only public posts and profiles are accessible.

**What resolution are the screenshots?** The viewport defaults to 1440×900 and is configurable from 320×240 up to 3840×2160. With `2x` or `3x` pixel density the saved image is two or three times larger on each side. The actual dimensions are always reported in `width` and `height`.

**What is the difference between the three capture modes?** `postCard` captures a single post as a clean card; `profileHeader` captures the profile header plus the first posts; `fullProfilePage` captures the whole scrollable profile page. A post link captures a post card only in `postCard` mode — if `profileHeader` or `fullProfilePage` is selected, a post link captures that post's author profile instead.

**Does it support threads?** Each post link is captured individually. Paste each post in the thread as a separate link.

**What happens if a post contains a video?** The actor waits for the video to load and pauses it on a still frame before capturing, so the capture is clean.

**What gets hidden in a capture?** The left navigation, headers, sidebars, login prompts, sticky banners and community notes are hidden automatically. Reply posts are hidden when **Hide replies** is on.

**Which image format should I use?** PNG for lossless quality, JPEG for smaller files, WEBP for the smallest files. JPEG and WEBP use the quality setting.

**What if a link is invalid or the post was deleted?** The row gets a `status` explaining the problem instead of a screenshot. The run never crashes.

**How long do download links last?** They follow your Apify key-value store retention (typically 7 days on the free tier). Copy the images to your own storage for permanent archival.

**Is this affiliated with X?** No. This is a third-party actor that captures publicly visible pages.

## Limits

- Public content only — private or protected accounts cannot be captured.
- One capture per link; profile pages capture the first posts loaded at the chosen viewport.
- Metadata counts are added only when X displays them.
- Capture failures (for example a deleted post) produce a `status` row, so a run is never silently empty.
