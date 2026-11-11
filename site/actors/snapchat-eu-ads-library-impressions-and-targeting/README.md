# Snapchat EU + Turkey Ads Library Impressions & Targeting Extractor

Under EU and Turkish digital advertising transparency rules, Snapchat publishes ads delivered in those markets through the public Ads Gallery API. This actor reads that library directly — search by one or more advertisers, browse all publicly disclosed sponsored content, or search by creator — and returns structured records with normalized creative, landing page, impression, targeting, catalog, story, collection and lens data. No login, cookie or OAuth token is required.

## What this actor does

- Searches ads by one or more paying-advertiser names, with country, date-range and status filters
- Paginates advertiser search automatically (Snap serves 10 ads per request; the actor follows `paging.next_link` until the per-advertiser limit or the end)
- Browses the full live sponsored-content library with automatic GET pagination (up to 200 items per page)
- Searches sponsored content by creator with POST cursor pagination and deduplication by `contentUrl`
- Supports partial (`contains`) and case-insensitive `exact` payer matching
- Returns normalized lifetime impressions, flat targeting, landing page/domain, media, DPA products, story snaps, collection and lens data
- Emits coverage rows with the payer names actually seen, plus a `RUN_SUMMARY` key-value record
- Distinguishes `no_ads` from `rationed`, `blocked`, `partial`, `invalid` and `error` instead of writing placeholder error rows
- Throttles requests and retries 429/5xx responses with exponential backoff and `Retry-After` support

## Data scope and freshness

- **Markets:** 27 EU member states plus **Turkey (`tr`)**. `gr` is accepted as an alias for `el` (Greece). The UK (`gb`/`uk`) and US are not in this library.
- **Window:** Snap only publishes ads delivered in the EU and Turkey during the **last 12 months**. Older `startDate` values may return no ads.
- **Freshness:** Snap refreshes Ads Gallery impressions **at most every 24 hours**. Counts are calculated on GMT.
- **Impressions:** `impressionsTotal` and `impressionsByCountry` are **lifetime** counts for the ad, not 24-hour or daily counts.
- **Not published:** spend, budget, reach, frequency, CTR, conversions, exact end date, and UK/US ads. Sponsored creator content is a secondary surface with fewer fields than ad records.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `adSearch` | `adSearch`, `sponsoredContent`, or `creatorSearch` |
| `payingAdvertiserNames` | array | - | One or more paying-advertiser names for `adSearch` |
| `payingAdvertiserName` | string | – | Legacy single-advertiser input; merged with the array |
| `advertiserMatch` | string | `contains` | `contains` uses Snap's partial payer search; `exact` keeps only case-insensitive exact payer matches |
| `countries` | array | `[]` | EU + Turkey codes: `at`, `be`, `bg`, `cy`, `cz`, `de`, `dk`, `ee`, `el`, `es`, `fi`, `fr`, `hr`, `hu`, `ie`, `it`, `lt`, `lu`, `lv`, `mt`, `nl`, `pl`, `pt`, `ro`, `se`, `si`, `sk`, `tr`; `gr` maps to `el` |
| `startDate` | string | – | Ads that ran on or after this date (ISO 8601 or `YYYY-MM-DD`) |
| `endDate` | string | – | Ads that ran on or before this date (ISO 8601 or `YYYY-MM-DD`) |
| `status` | string | `ALL` | `ACTIVE`, `PAUSED`, or `ALL` |
| `creatorName` | string | – | Creator username or name for `creatorSearch` |
| `maxResults` | integer | `200` | Maximum records **per advertiser** in `adSearch`, or total records for the other modes (1–10,000) |
| `includeCoverage` | boolean | `true` | Add one coverage row per advertiser/creator |
| `proxyConfiguration` | object | – | Optional; the public API normally works without a proxy |

### Example: multiple active advertisers in France, Germany and Turkey

```json
{
  "mode": "adSearch",
  "payingAdvertiserNames": ["nike", "adidas"],
  "advertiserMatch": "contains",
  "countries": ["fr", "de", "tr"],
  "status": "ACTIVE",
  "maxResults": 200
}
```

### Example: exact payer match

```json
{
  "mode": "adSearch",
  "payingAdvertiserNames": ["Nike, Inc."],
  "advertiserMatch": "exact",
  "countries": ["fr"]
}
```

### Example: browse all sponsored content

```json
{
  "mode": "sponsoredContent",
  "maxResults": 500
}
```

### Example: sponsored content by a creator

```json
{
  "mode": "creatorSearch",
  "creatorName": "beauty",
  "maxResults": 100
}
```

## Output per ad (`recordType = "ad"`)

### Identity, advertiser and delivery

- `adId`, `adName`, `adAccountName` — ad identifier, internal ad name and ad-account name
- `payingAdvertiserName` — paying entity as disclosed by Snap (whitespace-normalized)
- `brandName`, `profileName`, `profileLogoUrl` — brand (`brand_name` or profile fallback) and Snap public profile
- `status`, `reviewStatus`, `rejectionReasons`, `startDate`, `endDate` (when published)
- `daysActive` — days from `startDate` to `endDate` or now
- `languages`
- `searchAdvertiser`, `matchMode` — which input name/match mode produced the record
- `matchedAdvertisers` — added only when the same ad matched more than one input advertiser

### URLs and media

- `adUrl` — public Ads Gallery detail page (`https://adsgallery.snap.com/?adId=...`), verified to open the ad
- `adDetailApiUrl` — public API detail endpoint (`/v1/ads_library/ads/{adId}`)
- `landingUrl` — web-view, deep-link or story-snap destination
- `domain` — hostname of the HTTP(S) landing URL
- `mediaUrls`, `mediaType` — all top-level and story-snap creative media URLs and their type
- `topSnapMediaDownloadLink`, `mediaDownloadUrl`, `topSnapMediaType`, `topSnapCropPosition`
- `webViewProperties`, `deepLinkProperties`, `compositePreview`, `dpaPreview`, `collectionPreview`, `lensPreview`, `stickers` — raw API objects, retained for completeness

### Impressions

- `impressionsTotal` — lifetime impressions from Snap (falls back to the per-country sum if Snap omits the total)
- `impressionsByCountry` — only countries with a **nonzero** impression count
- `countries` — those countries, largest first
- `topCountry`, `topCountryImpressions`

### Targeting

- `targeting` — flat normalized targeting: `minAge`, `maxAge`, `ageRange`, `genders`, `languages`, `devices`, `regulatedContent`
- `targetingV2` — raw `targeting_v2` object

### Catalog, story, collection and lens

- `products`, `productCount`, `dpaTemplate` — dynamic product-ad items with flattened image URLs
- `story` — composite/story ads: `titleHeadline`, `shouldLoop`, `previewCreativeRenderType`, `snapCount`, and per-snap `snaps` (type, headline, CTA, media, landing URL)
- `collection` — collection ads: `itemCount`, `items` (including app-install properties when present), `landingUrl`
- `appInstall` — app-install properties when Snap publishes them
- `lens` — lens preview (`iconUrl`)
- `recordType` — always `ad`
- `scrapedAt` — ISO-8601 UTC scrape timestamp

## Output per sponsored content item (`recordType = "sponsoredContent"`)

- `contentType`, `contentUrl`, `thumbnailUrl`
- `creatorName`, `creatorUrl`
- `sponsorName`, `sponsorUrl`, `brandName`
- `recordType`, `scrapedAt`

## Coverage rows and run summary

With `includeCoverage` enabled (default), the dataset also contains one row per advertiser/creator:

- `recordType = "coverage"`, `mode`, `target`
- `status` — `ok`, `no_ads`, `partial`, `rationed`, `blocked`, `invalid`, or `error`
- `recordCount`, `rawRecordCount`, `duplicatesRemoved`, `pagesFetched`
- `payerNames` — every payer name actually seen for that search, including non-matching names in `exact` mode
- `countries`, `topCountry`, `impressionsTotal`
- `recordsWithImpressions`, `recordsWithLandingUrl`, `recordsWithMedia`
- `error`, `notes`, `requestIds`
- Sponsored-content coverage also includes `creatorNames`, `sponsorNames`, `contentTypes`

The key-value store record `RUN_SUMMARY` contains the overall run status, counts by status, errors, notes, duration, input echo, source, scope and freshness.

## No-results semantics

Empty results never produce a placeholder `{mode, error}` row. If Snap returns no matching ads, the run finishes with `status = "no_ads"` and writes no ad rows (coverage rows still show the search). If Snap rate-limits, blocks, rejects or partially fails a request, the summary reports `rationed`, `blocked`, `invalid`, `partial` or `error`, and any records already collected are kept.

## Pagination and limits

- **Advertiser search:** Snap serves **10 ads per request**. The actor POSTs the returned `paging.next_link` with the same JSON body; pagination is real and advances page by page.
- **Creator search:** Snap serves up to 200 items per page. The actor POSTs `paging.next_link` with the same body. Pages can overlap; records are deduplicated by `contentUrl`.
- **Sponsored content browse:** GET with `limit=200`, following GET `paging.next_link`.
- **Rate limits:** Snap applies server-side limits (HTTP 429 and occasional 500/E4001 BigQuery rate-limit errors). The actor throttles requests and retries with exponential backoff plus `Retry-After`.
- **Ad detail:** `GET /v1/ads_library/ads/{ad_id}` returns a complete `ad_preview`, verified live.
- **Hard limits:** 12-month window, 24-hour impression refresh, no spend/reach, exact end dates are usually unpublished, no UK/US, and creator content has fewer fields.

## Use cases

- **Competitive ad monitoring** — track competitor creatives, CTAs, landing pages and per-country lifetime impressions
- **Regulatory/transparency research** — study disclosed EU/Turkey ad targeting and impressions
- **Creator partnership discovery** — find brands sponsoring a creator's content
- **Creative benchmarking** — compare formats, CTAs and catalog/story/collection usage
- **Impressions analysis** — use `impressionsByCountry`, `topCountry` and coverage rows

## FAQ

**Is this official Snapchat data?** Yes. It reads Snapchat's public Ads Gallery API, which Snap publishes under transparency rules; no private pages or user data are accessed.

**Why does advertiser search return 10 ads at a time?** Ten is Snap's page size, not a total cap. This actor follows `paging.next_link` until `maxResults` per advertiser or the end of the result set.

**Which countries are supported?** The 27 EU member states and Turkey. `gr` is mapped to `el`; unsupported codes are dropped with a warning instead of filtering out all results.

**How current are impressions?** Snap updates the gallery at most every 24 hours, and the counts are lifetime impressions for each ad.

**Can I download creatives?** Yes — `mediaUrls` and `topSnapMediaDownloadLink` are direct Snap CDN links. CDN URLs can expire, so download soon after scraping.

**What is the difference between `sponsoredContent` and `creatorSearch`?** `sponsoredContent` pages through the whole live sponsored-content library. `creatorSearch` narrows it to one creator's name. Both return the same record shape.

**Is this affiliated with Snapchat?** No. This is an independent third-party actor reading Snap's publicly mandated Ads Gallery API.
