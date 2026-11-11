# Yandex Maps Business Search, Details & Reviews Scraper

Collect business listings, full business cards and customer reviews from [Yandex Maps](https://yandex.com/maps/) — the map service used across Russia, Belarus, Kazakhstan, Uzbekistan and Turkey. The actor reads Yandex Maps' public server-rendered pages and its internal JSON endpoints directly, so it needs no login, no API key, no cookies and no browser.

## What this actor does

- **Three modes:** search by keyword and location (`searchPlaces`), fetch complete business cards (`getDetails`), or collect reviews (`getReviews`).
- **Search precisely:** combine a query with a city, a centre point and radius, or a bounding box. Filter by rating, review count, phone, website, price band, category, current opening status and Yandex's Good Place flag.
- **Full business cards:** contacts, categories, rating breakdown, price range, structured opening hours, features, chain membership, verified-owner flag, popular times, review-aspect sentiment, metro/stops, photos and coordinates.
- **Deep reviews:** up to 2,400 unique reviews per business. Yandex exposes at most 600 reviews per sort order, so the actor walks all four orders (relevance, newest, highest rated, lowest rated) when you ask for more than 600, then removes duplicates.
- **Review filters:** rating range, date range, text phrases and "has an owner reply".
- **Run-wide caps and global deduplication:** `maxItems` counts records across the whole run, not per query. Duplicate businesses and reviews are removed across queries and pages.
- **Omit-empty records:** a field is written only when Yandex has a real value for it. Every record carries `recordType`, `sourceUrl` and `scrapedAt`.
- **International:** six regional domains and eight interface languages.

## Output per record

Each dataset item is either a place (`recordType: "place"`) or a review (`recordType: "review"`).

### Place record

- `placeId`, `name`, `shortName`, `description`, `url` — identity and canonical Yandex Maps page
- `address`, `city`, `country`, `postalCode`, `addressDetails` — location
- `coordinates` — `{ lat, lng }`; `distanceKm` when a centre point was used
- `rating`, `ratingCount`, `reviewCount` — Yandex's rating value, star-rating count and text-review count
- `categories`, `categoryDetails` — category names and Yandex category IDs
- `phone`, `phones`, `website`, `websites`, `socialLinks` — contacts
- `workingHours`, `workingHoursText`, `isOpenNow`, `openStatus` — structured week schedule and current status
- `features`, `featureGroups` — amenities, payment methods and other business attributes
- `priceRange`, `priceCategory`, `priceCategoryName` — price signals when Yandex publishes them
- `chain`, `isChain`, `verifiedOwner`, `isGoodPlace`, `goodPlaceYear`, `businessStatus`
- `popularTimes` — Yandex's 24-hour popularity histogram per weekday
- `aspects` — review-aspect sentiment (staff, drinks, atmosphere, …)
- `photos`, `photoCount`, `logoUrl`
- `metro`, `stops` — nearest transit with distance
- `advertiser` — legal name and TIN when the row is a promoted listing
- `searchQuery`, `searchCity`, `position` — search provenance when applicable
- `sourceUrl`, `scrapedAt`, `recordType`

### Review record

- `reviewId`, `rating`, `text`, `textLanguage`, `translations`
- `date`, `updatedAt` — review date and full timestamp
- `author`, `authorUrl`, `authorPublicId`, `authorAvatarUrl`, `authorLevel`
- `likes`, `dislikes`, `isPinned`
- `ownerReply` — `{ text, date, updatedAt }` when the business replied
- `photos`, `photoCount`
- `placeId`, `placeName`, `placeUrl`, `placeRating`, `placeReviewCount`, `placeAddress`, `placeCity`, `placePhone`, `placeWebsite`
- `sortOrder`, `position`, `sourceUrl`, `scrapedAt`, `recordType`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `searchPlaces` | `searchPlaces`, `getDetails` or `getReviews` |
| `searchQueries` | array of strings | – | Keywords for `searchPlaces`, and for `getReviews` discovery when no IDs/URLs are supplied |
| `city` | string | – | City name in any language; resolved to Yandex's region centre |
| `coordinates` | string | – | Centre point as `lat,lng`, e.g. `55.7558,37.6173` |
| `radiusKm` | integer | – | Keep places within 1–50 km of the centre (strict client-side distance filter) |
| `bbox` | string | – | Rectangle as `west,south,east,north`; results outside it are dropped |
| `businessIds` | array of strings | – | Yandex organization IDs for `getDetails` / `getReviews` |
| `startUrls` | array of strings | – | Organization URLs, short links or Yandex search URLs |
| `maxItems` | integer | `100` | Run-wide record cap (1–5,000) |
| `maxReviewsPerPlace` | integer | `100` | Reviews per business (1–2,400) |
| `reviewSort` | string | `relevance` | `relevance`, `time`, `rating_desc` or `rating_asc` |
| `reviewMinRating` | integer | – | Minimum review stars (1–5) |
| `reviewMaxRating` | integer | – | Maximum review stars (1–5) |
| `reviewDateFrom` | string | – | Earliest review date (`YYYY-MM-DD`) |
| `reviewDateTo` | string | – | Latest review date (`YYYY-MM-DD`) |
| `reviewTextContains` | array of strings | – | Keep reviews containing any phrase (case-insensitive) |
| `reviewRequireOwnerReply` | boolean | `false` | Only reviews with a business reply |
| `minRating` | string | `any` | Minimum place rating: `any`, `3`, `3.5`, `4`, `4.5`, `4.7`, `4.9` |
| `minReviewCount` | integer | `0` | Minimum text reviews for a place |
| `requirePhone` | boolean | `false` | Only places with a phone |
| `requireWebsite` | boolean | `false` | Only places with a website |
| `openNow` | boolean | `false` | Only places Yandex reports as open now |
| `goodPlace` | boolean | `false` | Yandex Good Place filter (server-side in search, verified on every place record) |
| `priceCategories` | array of strings | `[]` | `price_cheap`, `price_reasonable`, `price_expensive`, `price_very_expensive` |
| `categoryIds` | array of strings | – | Yandex category IDs (see `categoryDetails` in the output) |
| `maxPagesPerQuery` | integer | `10` | Search pages per query, 25 businesses each |
| `maxConcurrency` | integer | `5` | Concurrent business/review workers (1–20) |
| `yandexDomain` | string | `yandex.com` | `yandex.com`, `.ru`, `.com.tr`, `.kz`, `.uz`, `.by` |
| `language` | string | `en` | `en`, `ru`, `tr`, `de`, `fr`, `uk`, `kk`, `uz` |
| `proxyConfiguration` | object | – | Optional. The actor works without a proxy; supply one only to pin a country/provider |

### Example: coffee shops in Moscow

```json
{
  "mode": "searchPlaces",
  "searchQueries": ["coffee"],
  "city": "Moscow",
  "maxItems": 3
}
```

### Example: cafés within 3 km of a point

```json
{
  "mode": "searchPlaces",
  "searchQueries": ["coffee"],
  "coordinates": "55.7558,37.6173",
  "radiusKm": 3,
  "maxItems": 100
}
```

### Example: full cards from a search URL

```json
{
  "mode": "getDetails",
  "startUrls": ["https://yandex.com/maps/?text=coffee%20Moscow"],
  "maxItems": 20
}
```

### Example: newest negative reviews with owner replies

```json
{
  "mode": "getReviews",
  "businessIds": ["150968830833"],
  "maxReviewsPerPlace": 300,
  "reviewSort": "time",
  "reviewMaxRating": 3,
  "reviewRequireOwnerReply": true
}
```

### Example: Turkish restaurants in Istanbul

```json
{
  "mode": "searchPlaces",
  "searchQueries": ["restaurant"],
  "city": "Istanbul",
  "yandexDomain": "yandex.com.tr",
  "language": "tr",
  "maxItems": 50
}
```

## Use cases

- **Lead generation** — build lists of local businesses with phones, websites and social links by category and city.
- **Market research** — compare ratings, price bands and feature adoption across a city or district.
- **Reputation monitoring** — pull recent reviews with owner replies and translations on a schedule.
- **Location analysis** — count nearby competitors within a radius or rectangle and read popular-times curves.
- **Data enrichment** — resolve Yandex organization IDs and URLs into structured business cards.

## How it works

1. The actor fetches the normal Yandex Maps search or organization page.
2. It reads the page's `state-view` JSON (`config`, `stack[0].results`) instead of parsing fragile HTML.
3. For additional search pages and reviews it calls Yandex's internal `/maps/api/search` and `/maps/api/business/fetchReviews` endpoints, signing each request with the same `s` parameter the site's frontend computes.
4. If the signature or an endpoint changes, the actor refreshes the page state and retries once, then falls back to the server-rendered page and reports a partial-result warning instead of silently returning wrong data.

## FAQ

**Does this need a Yandex account, API key or cookies?**
No. It uses public pages and the site's own session cookies, which are set automatically. Nothing is sent to Yandex except the normal request parameters.

**Why is `maxItems` applied to the whole run?**
So two queries cannot return more rows than you asked for. The same business found by several queries is emitted once. Use `maxPagesPerQuery` to control search depth.

**How many reviews can I get per business?**
Up to 2,400 unique reviews. Yandex returns at most 600 reviews per sort order; the actor fetches the selected order and, when you request more than 600, the other three orders too, then de-duplicates by review ID.

**Why does a broad search return fewer places than Yandex's result count?**
Yandex's `totalResultCount` is unstable and Yandex repeats businesses across pages. The actor stops after three pages without a new business, at `maxPagesPerQuery`, or at `maxItems`. Narrow the query with a city, radius or category to get more precise coverage.

**Are review texts translated?**
The original text is always in `text`; `translations` holds Yandex's translations when available. Set `language` to change the interface and metadata language, not the review language.

**Does the actor use a proxy?**
It works without one. If Yandex blocks the direct connection, the actor retries with a fresh session and can switch to Apify Proxy automatically. You can also supply your own proxy configuration; it is never required and never prefilled.

**What is missing?**
Yandex does not publish email addresses, a full menu, an official legal-entity block or an AI review summary on these public pages. Promoted rows sometimes expose an advertiser name and TIN. Those gaps are documented in `docs/RESEARCH-yandex-maps.md`.

**Is this affiliated with Yandex?**
No. This is an independent third-party actor that reads publicly available Yandex Maps pages. It is not affiliated with or endorsed by Yandex.
