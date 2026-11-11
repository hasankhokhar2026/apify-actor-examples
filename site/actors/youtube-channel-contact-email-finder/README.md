# YouTube Channel Contact Email Finder

Build a public contact list from YouTube channels: channel metadata, linked websites and socials, and every public email address found across the channel description, linked site, recent videos, and link-in-bio pages. Start from channel URLs or let keyword search discover creators.

No login, cookies, API key, or CAPTCHA solving required.

## What this actor does

- Accepts channel URLs, `@handles`, `UC...` channel IDs, and video URLs (the channel is resolved from the video).
- Discovers channels from one or more keyword searches (about 20 channels per query).
- Reads the About page through `ytInitialData.aboutChannelViewModel`: name, handle, channel ID, subscriber count, country, description, and links.
- Unwraps YouTube's `/redirect?q=...` link wrapper, so you get the real website and social URLs.
- Runs a bounded email cascade:
  1. channel About description;
  2. up to two linked websites (home, contact/about pages, and common paths such as `/contact` and `/about`);
  3. the latest five video descriptions;
  4. one linked link-in-bio hub (Linktree, Beacons, and similar).
- Deduplicates emails, filters placeholder/asset/no-reply noise, ranks role mailboxes, and returns the best address as `primaryEmail`.
- Flags channels that have a native YouTube business email behind the sign-in wall with `hasHiddenEmail: true`. The gated address itself is never claimed or guessed.
- Omits empty fields from every record.

## Input

| Field | Type | Default | Description |
| --- | --- | --- | --- |
| `mode` | select | `channels` | `channels` scrapes the list you provide; `search` discovers channels from `searchQueries`. |
| `channels` | array | – | Channel URLs, `@handles`, `UC...` IDs, or video URLs (mode=channels). |
| `searchQueries` | array | – | Keywords for channel discovery (mode=search). Each query yields about 20 channels. |
| `maxChannels` | integer | `100` | Maximum unique channels per run, 1–500. |
| `includeWebsite` | boolean | `true` | Scan up to two linked websites and one link-in-bio hub per channel. |
| `includeVideoDescriptions` | boolean | `true` | Read descriptions of the latest five videos per channel. |
| `onlyWithEmail` | boolean | `false` | Drop channel records that have no public email. Error records are still reported. |
| `emailDomains` | array | – | Optional allowlist such as `["brand.com", "gmail.com"]`. Matching is case-insensitive and includes subdomains. |
| `maxEmailsPerChannel` | integer | `5` | Cap after ranking, 1–20. |
| `proxyConfiguration` | object | – | Optional Apify Proxy override. The actor works without a proxy. |

### Example: channels

```json
{
  "mode": "channels",
  "channels": [
    "@mkbhd",
    "@LinusTechTips",
    "https://www.youtube.com/channel/UCBJycsmduvYEL83R_U4JriQ",
    "https://www.youtube.com/watch?v=DN953UW8iJ8"
  ],
  "maxChannels": 10,
  "includeWebsite": true,
  "includeVideoDescriptions": true,
  "onlyWithEmail": false,
  "maxEmailsPerChannel": 5
}
```

### Example: keyword search

```json
{
  "mode": "search",
  "searchQueries": ["home espresso", "personal finance"],
  "maxChannels": 30,
  "includeWebsite": true,
  "includeVideoDescriptions": true,
  "onlyWithEmail": true,
  "emailDomains": ["gmail.com", "outlook.com"]
}
```

## Output

One record per channel. Fields with no value are omitted.

```json
{
  "recordType": "channel",
  "channelId": "UCBJycsmduvYEL83R_U4JriQ",
  "handle": "@mkbhd",
  "name": "Marques Brownlee",
  "url": "https://www.youtube.com/@mkbhd",
  "subscriberCount": 21400000,
  "country": "United States",
  "description": "MKBHD: Quality Tech Videos... business@MKBHD.com",
  "links": [
    {"title": "Twitter", "url": "https://twitter.com/MKBHD", "type": "social"},
    {"title": "Instagram", "url": "https://instagram.com/MKBHD", "type": "social"}
  ],
  "socials": {
    "x": "https://twitter.com/MKBHD",
    "instagram": "https://instagram.com/MKBHD"
  },
  "emails": [
    {
      "email": "business@mkbhd.com",
      "source": "channel_description",
      "sourceUrl": "https://www.youtube.com/@mkbhd/about"
    }
  ],
  "primaryEmail": "business@mkbhd.com",
  "emailSource": "channel_description",
  "hasHiddenEmail": true,
  "sourceUrl": "https://www.youtube.com/@mkbhd/about",
  "scrapedAt": "2026-10-26T12:00:00+00:00"
}
```

**Field notes**

- `recordType` – `channel` for a contact record, `error` for a failed input/search.
- `channelId` / `handle` / `name` / `url` – stable channel identity. `url` is the canonical channel URL.
- `subscriberCount` – expanded from YouTube's displayed label (`21.4M` becomes `21400000`; approximate for large channels).
- `country` – the country shown in the About panel.
- `description` – the full About description.
- `links` – every external link with a title, absolute URL, and `type` (`website`, `social`, or `link_hub`).
- `socials` – one URL per recognised platform (`x`, `instagram`, `tiktok`, `facebook`, `linkedin`, `discord`, `twitch`, `patreon`, `telegram`, `threads`, `spotify`, `github`, and more).
- `websiteCandidate` – the first non-social, non-hub linked website.
- `emails` – deduplicated and ranked email objects. `source` tells you where the address came from; `sourceUrl` points at the exact page.
- `primaryEmail` / `emailSource` – the highest-value public address and its source.
- `hasHiddenEmail` – `true` when the About page shows YouTube's `Sign in to see email address` gate. The actor cannot read that address without login, so it does not pretend to.
- `sourceUrl` / `scrapedAt` – canonical About page and UTC timestamp.

**Email sources**

| `source` | Where the address was found |
| --- | --- |
| `channel_description` | The channel's About description. |
| `website` | A linked website page (home, contact/about page, or common path). |
| `video_description` | One of the latest five video descriptions. |
| `link_hub` | A Linktree/Beacons-style link-in-bio page. |

### Error record

```json
{
  "recordType": "error",
  "reason": "not_found",
  "message": "Channel page returned 404.",
  "input": "https://www.youtube.com/@missing-handle",
  "sourceUrl": "https://www.youtube.com/@missing-handle/about",
  "scrapedAt": "2026-10-26T12:00:00+00:00"
}
```

`reason` is one of: `invalid_input`, `invalid_url`, `not_found`, `fetch_failed`, `blocked`, `rate_limited`, `parse_failed`, `channel_unavailable`, `video_resolve_failed`, or `scrape_error`. If every channel fails, the run fails loudly instead of silently returning an empty dataset.

## How the email cascade works

1. **Channel description first.** This is the creator-authored text on the About page and the highest-signal source.
2. **Linked websites next.** For up to two non-social websites, the actor reads the home page, selected contact/about links, and common paths (`/contact`, `/contact-us`, `/about`, `/about-us`, `/impressum`, `/support`, `/press`). Website emails must share the site's registrable domain, which removes support addresses from embedded vendors and analytics scripts.
3. **Recent video descriptions.** The latest five videos are read from the channel's Videos tab. This catches creators who put business contacts in every upload description.
4. **One link hub.** Linktree, Beacons, and similar pages are read for public addresses.

All hits are deduplicated. The primary email favours role mailboxes such as `business@`, `partnerships@`, `contact@`, and `press@`, with the source order above as the next tie-breaker. `maxEmailsPerChannel` caps the ranked list.

## Limits and honest limitations

- **The native YouTube business email is login-gated.** The About page exposes only a sign-in prompt; the address is not in the HTML. This actor reports `hasHiddenEmail` and never claims the gated value. Treat `hasHiddenEmail: true` plus no `emails` as a real lead that needs manual or logged-in follow-up.
- **Public coverage is not 100%.** Many creators publish no public address anywhere the actor can read. Coverage is higher for large brands and creators who link a website.
- **Website crawling is bounded.** Two sites × up to five pages, plus one link hub and five videos per channel. This keeps runs affordable and predictable.
- **Search returns about 20 channels per query.** Add more queries to widen discovery; `maxChannels` is the hard ceiling.
- **TikTok bios are not a core source.** Anonymous TikTok pages are frequently replaced by a challenge page. Instagram/TikTok links are still returned in `links` and `socials`, but the email cascade focuses on sources that are reliably public.
- **Subscriber counts are rounded** to YouTube's public display value.
- **Countries can be missing** for some brand or very small channels; the field is omitted rather than guessed.
- **Websites that expose contact only through a form** cannot yield an email.

## FAQ

**Does this actor bypass CAPTCHAs or log in to YouTube?**
No. It reads public pages anonymously. When a page is blocked or challenged, that channel gets a clear error record and the run continues.

**Why is `hasHiddenEmail` true but `primaryEmail` missing?**
YouTube only shows the native business address to signed-in users. The flag means the address exists, but it is not public. The actor does not invent or scrape it.

**Are emails validated or checked for deliverability?**
No. The actor reports addresses exactly as published, with provenance. Validate with your own email-verification step before outreach.

**What happens to duplicate channels or emails?**
Duplicate channels (by ID/URL) are processed once. Duplicate emails are merged, keeping the first/highest-priority source.

**Can I restrict results to one domain?**
Yes. Use `emailDomains`, for example `["gmail.com"]` or `["brand.com"]`. Subdomains are included.

**What if a channel has no email?**
The channel record is still returned with metadata (unless `onlyWithEmail` is on). This is useful for spotting channels that have a hidden gate.

**Is this affiliated with YouTube?**
No. This is an independent third-party tool that reads publicly available pages. You are responsible for complying with YouTube's terms and applicable outreach/privacy laws.
