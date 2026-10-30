# Snapchat Snapcode Image Downloader

Every Snapchat account has its own Snapcode — the scannable, ghost-shaped code that opens an add-friend prompt the instant someone scans it with the Snapchat camera. This actor fetches the official Snapcode image for any username, in SVG or PNG, with or without the account's Bitmoji, and can save a permanent copy of the image to your run's storage.

## What this actor does

- Accepts any number of Snapchat usernames in a single run
- Fetches each user's snapcode directly from Snapchat's official snapcode endpoint
- Supports SVG (vector, scalable) and PNG (raster) formats
- Optionally includes or excludes the user's Bitmoji avatar in the snapcode
- Optionally saves the image binary to Apify Key-Value Store and returns a persistent URL
- Returns error records for invalid or non-existent usernames — no run failures

## Input

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `usernames` | string[] | Yes | — | Snapchat usernames to fetch snapcodes for. Example: `["brentrivera", "selenagomez"]` |
| `format` | string | No | `SVG` | Image format: `SVG` (vector, ~68 KB, recommended) or `PNG` (raster, ~25 KB) |
| `bitmoji` | string | No | `enable` | `enable` includes the user's Bitmoji avatar; `disable` shows the classic ghost icon only |
| `downloadToStorage` | boolean | No | `false` | Save the image binary to Apify Key-Value Store and include a persistent `kvStoreUrl` in the output |
| `proxyConfiguration` | object | No | — | Optional proxy configuration for requests |

### Example Input

```json
{
  "usernames": ["brentrivera", "selenagomez", "khaby.lame"],
  "format": "SVG",
  "bitmoji": "enable",
  "downloadToStorage": false
}
```

## Output

One record per username. If a username is invalid or not found, an error record is returned instead.

| Field | Type | Description |
|-------|------|-------------|
| `username` | string | Snapchat username as provided in input |
| `snapcodeUrl` | string | Direct URL to fetch the snapcode image from Snapchat's CDN |
| `format` | string | Image format used: `SVG` or `PNG` |
| `bitmojiEnabled` | boolean | Whether the Bitmoji avatar is included in the image |
| `contentType` | string | MIME type of the image: `image/svg+xml` or `image/png` |
| `byteLength` | integer | File size of the snapcode image in bytes |
| `kvStoreUrl` | string | Persistent Apify Key-Value Store URL for the saved image (only when `downloadToStorage` is `true`) |
| `scrapedAt` | string | ISO 8601 UTC timestamp of when the record was collected |

### Example Output — Success

```json
{
  "username": "waqarzaka",
  "snapcodeUrl": "https://app.snapchat.com/web/deeplink/snapcode?username=waqarzaka&type=SVG&bitmoji=enable",
  "format": "SVG",
  "bitmojiEnabled": true,
  "contentType": "image/svg+xml",
  "byteLength": 10314,
  "scrapedAt": "2026-06-28T06:48:12.863774+00:00"
}
```

### Example Output — Error Record

```json
{
  "username": "nonexistentuser99",
  "error": "Snapcode request failed (HTTP 400)",
  "scrapedAt": "2026-06-28T06:48:13.001000+00:00"
}
```

## Use Cases

- **Profile verification** — collect official snapcodes for a list of influencers or brand accounts
- **Marketing materials** — batch-download snapcodes for print campaigns, posters, or event badges
- **Brand asset archiving** — save snapcodes to persistent storage alongside other social media assets
- **Influencer research** — quickly verify which usernames are active Snapchat accounts
- **QR code aggregation** — build a library of Snapchat entry points for campaign landing pages

## FAQ

**What is a Snapcode?**
A Snapcode is Snapchat's proprietary QR-style code that uniquely identifies a user. When scanned with the Snapchat camera, it instantly opens an add-friend prompt for that user. They are widely used in marketing, printed materials, and digital campaigns.

**Should I use SVG or PNG?**
SVG is recommended for most uses. It is vector-based, scales to any resolution without pixelation, and is ideal for print or high-DPI displays. Use PNG if your downstream system does not support SVG rendering.

**What does enabling or disabling Bitmoji do?**
When `bitmoji` is set to `enable`, the snapcode includes the user's Bitmoji avatar inside the ghost outline. If the user has not set up a Bitmoji, Snapchat shows the default ghost icon regardless. Set to `disable` to always receive the plain ghost outline version.

**Why use `downloadToStorage`?**
The `snapcodeUrl` field points to Snapchat's live endpoint, which regenerates the image on each request and may change over time. Enabling `downloadToStorage` saves a copy of the image bytes to your Apify Key-Value Store and returns a stable `kvStoreUrl` that will not expire as long as the storage run exists.

**Do I need a Snapchat account or cookies?**
No. Snapcodes are publicly available for any Snapchat username — no login, session, or cookies are required.

**What happens for invalid or non-existent usernames?**
Instead of stopping the run, the actor emits an error record for that username with the `error` field explaining what went wrong. All other usernames continue to be processed normally.

**Can I scrape snapcodes for hundreds of usernames at once?**
Yes. Add as many usernames as needed to the `usernames` array. The actor processes them sequentially and outputs one record per username.

**Is this affiliated with Snapchat?**
No, this is an independent, third-party actor that reads Snapchat's public Snapcode endpoint. It is not affiliated with or endorsed by Snap Inc.
