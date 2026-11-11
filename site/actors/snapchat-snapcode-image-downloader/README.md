# Snapchat Snapcode & Public Profile Scraper

Fetch the official add-friend Snapcode for any Snapchat username as a scalable SVG or a PNG at the size you need, and read the public profile details Snapchat shows to logged-out visitors: display name, subscriber count, bio, website, category, verification, profile picture, hero image, related accounts, and Bitmoji assets when the profile publishes them.

## What this actor does

- **Three modes:** `snapcode` for the image only, `profile` for public profile metadata, and `full` for both in one record.
- **Any username format:** plain usernames, `@handles`, `snapchat.com/add/...` links, and `snapchat.com/@...` links.
- **Image variants:** SVG or PNG, square sizes from 32 to 1000 pixels, with stable SVG and PNG URLs in every image record.
- **Public profile metadata:** display name, subscriber count, verification, bio, website, location, category, profile picture, hero image, creation and update dates, related accounts, and other public profile links when Snapchat publishes them.
- **Persistent image copies:** optionally save each fetched image to Apify key-value store and receive a stable download URL.
- **No login, cookies, or proxy setup required.**
- **Empty fields are omitted** instead of being written as `null` or an empty string.

## Output per record

Every record describes one username. Fields that the selected mode does not collect, or that Snapchat does not publish for that account, are omitted. `profile` mode returns public metadata only and does not add Snapcode image fields; use `snapcode` or `full` when you need the image details.

### Identity and record metadata

- `username` — normalized Snapchat username.
- `profileUrl` — canonical profile link, for example `https://www.snapchat.com/@brentrivera`.
- `recordType` — `snapcode`, `profile`, or `snapcodeProfile`.
- `scrapedAt` — UTC timestamp of the run.
- `error` — present only when that username could not be processed.

### Snapcode image fields (mode `snapcode` or `full`)

- `snapcodeUrl` — image URL in the selected format and size.
- `snapcodeSvgUrl` — SVG image URL at the selected size.
- `snapcodePngUrl` — PNG image URL at the selected size.
- `format` — `SVG` or `PNG`.
- `imageSize` — square image size in pixels.
- `bitmojiEnabled` — legacy compatibility field.
- `contentType` — image media type of the fetched file.
- `byteLength` — fetched image size in bytes.
- `kvStoreUrl` — persistent image URL when `downloadToStorage` is enabled.

### Public profile fields (mode `profile` or `full`)

- `accountType` — `public` or `personal`.
- `displayName` — name shown on the profile.
- `isVerified` — whether Snapchat marks the public profile as verified.
- `subscriberCount` — public subscriber count when Snapchat exposes a positive value.
- `bio` — public profile bio.
- `websiteUrl` — website listed on the profile, normalized to an absolute URL.
- `profilePictureUrl` — public profile picture.
- `snapcodeImageUrl` — canonical SVG Snapcode URL from the profile page.
- `address` — location text shown on the profile.
- `category`, `subcategory` — Snapchat's profile taxonomy.
- `heroImageUrl` — square hero image shown on the profile.
- `hasStory`, `hasCuratedHighlights`, `hasSpotlightHighlights` — public availability flags.
- `createdAt`, `lastUpdatedAt` — profile timestamps in ISO 8601 UTC.
- `relatedAccounts[]` — related public accounts with username, display name, verification, subscriber count, profile picture, and profile URL.
- `sameAsLinks[]` — other public profile links Snapchat publishes for the account, such as a TikTok page, when available.
- `bitmojiAvatarUrl`, `bitmojiAvatarFallbackUrl`, `bitmojiBackgroundUrl`, `bitmojiBackgroundFallbackUrl` — Bitmoji assets when the profile publishes them.

### Error records

A username that cannot be processed returns one record with `username`, `recordType`, `scrapedAt`, and an `error` message. Image modes also include the attempted `snapcodeUrl`, `format`, and `imageSize`; profile modes include `profileUrl` when the username itself is valid. Other usernames in the same run continue normally.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `snapcode` | `snapcode` (image only), `profile` (public metadata only), or `full` (both). |
| `usernames` | array | — | Required. Usernames, `@handles`, or Snapchat profile links. |
| `format` | string | `SVG` | `SVG` for a scalable image or `PNG` for a raster image (mode `snapcode` or `full`). |
| `imageSize` | integer | `320` | Square image size in pixels, 32–1000 (mode `snapcode` or `full`). |
| `downloadToStorage` | boolean | `false` | Save fetched images to Apify key-value store and add `kvStoreUrl`. |
| `maxItems` | integer | `1000` | Maximum number of records to save (1–5000). |

## Examples

### Example: download one Snapcode as SVG

```json
{
  "mode": "snapcode",
  "usernames": ["brentrivera"],
  "format": "SVG",
  "imageSize": 320
}
```

### Example: download high-resolution PNG Snapcodes

```json
{
  "mode": "snapcode",
  "usernames": ["kyliejenner", "khaby.lame", "@nasa"],
  "format": "PNG",
  "imageSize": 1000,
  "downloadToStorage": true
}
```

### Example: read public profile metadata from links

```json
{
  "mode": "profile",
  "usernames": [
    "https://www.snapchat.com/add/selenagomez",
    "https://www.snapchat.com/@nba",
    "nfl"
  ]
}
```

### Example: get the image and the profile together

```json
{
  "mode": "full",
  "usernames": ["snap", "nasa", "nike"],
  "format": "PNG",
  "imageSize": 640,
  "maxItems": 10
}
```

## Use cases

- **Influencer research** — collect subscriber counts, bios, categories, and verification alongside each creator's Snapcode.
- **Brand asset management** — download Snapcodes in SVG for print or high-resolution PNG for digital placements.
- **Campaign landing pages** — add a working “Add on Snapchat” image and profile link for every account in a campaign.
- **Creator list enrichment** — turn a list of usernames or profile links into structured public profile records for a CRM or spreadsheet.
- **Profile monitoring** — schedule recurring snapshots of subscriber counts, bios, categories, and update dates.
- **Agency reporting** — compare public profile data and Snapcode availability across a roster of accounts.

## FAQ

### What is a Snapcode?

A Snapcode is Snapchat's scannable add-friend image. Scanning it in the Snapchat camera opens an add-friend prompt for that account. Snapcodes are commonly used on websites, posters, event badges, and social profiles.

### Do I need a Snapchat account, cookies, or a proxy?

No. The actor reads the same public Snapcode images and logged-out profile pages that anyone can open in a browser. There is no login, cookie, API key, or proxy configuration to provide.

### Which username formats are accepted?

Plain usernames like `brentrivera`, handles like `@brentrivera`, and profile links like `https://www.snapchat.com/add/brentrivera` or `https://www.snapchat.com/@brentrivera`. Usernames are normalized to lowercase and duplicates are removed.

### Which image sizes and formats are available?

SVG and PNG, from 32 to 1000 pixels square. The default is 320 pixels, which matches Snapchat's standard Snapcode display size. SVG is best for print and high-density displays; PNG is best when your downstream system does not support SVG.

### Why do some profile fields appear for one account but not another?

Public creator and brand profiles publish subscriber counts, bios, websites, categories, and other metadata. Personal accounts publish only a display name and a Snapcode, so most metadata fields are omitted for them. Snapchat also hides subscriber counts for some accounts, in which case `subscriberCount` is omitted rather than shown as zero.

### Why is there no Bitmoji on/off switch?

Snapchat currently includes the account's Bitmoji in the public Snapcode automatically whenever the account has one. The image service ignores an explicit “disable” request for public profiles, so the old switch is not exposed. Bitmoji image URLs are still returned when a profile publishes them.

### Does a Snapcode image prove that a username exists?

No. The public image service returns a generic ghost image for unknown usernames. Use `mode: "profile"` or `mode: "full"` when existence matters: those modes read the profile page and return an error record for a username that does not exist.

### Can I search by display name or keyword?

No. Snapchat does not expose a public username search endpoint, so the actor resolves only exact usernames, `@handles`, and profile links that you provide.

### Why are some related accounts, subscriber counts, or links missing?

Snapchat publishes those fields only when it chooses to. Many public profiles show no related accounts, some show up to three, and an entry without a username is skipped, so a profile can show fewer than three even when Snapchat lists three. Subscriber counts are hidden for some accounts. Fields that are not published are omitted instead of shown as zero or blank.

### How many usernames can one run process?

`maxItems` accepts up to 5000 records. Very large lists take longer because each username needs one or two requests, so split a large list into several runs or allow a longer run timeout.

### Does the actor keep old Snapcodes or profile history?

No. Each run returns the current public image and the current public profile values. The actor does not store past versions; schedule repeated runs if you need to track changes.

### Is the Snapcode endpoint official?

The image endpoint Snapchat's own pages use is public but undocumented, so Snapchat can change it without notice. The actor retries temporary failures and returns a clear error record when the source is unavailable.

### Can I run the actor on a schedule?

Yes. Scheduled runs are useful for tracking subscriber counts, bios, categories, and profile update dates over time. The actor records a fresh `scrapedAt` timestamp on every record.

### Is this affiliated with Snapchat?

No. This is an independent, third-party actor that reads publicly available Snapchat pages and image endpoints. It is not affiliated with, endorsed by, or sponsored by Snap Inc.
