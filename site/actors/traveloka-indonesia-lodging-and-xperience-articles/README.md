# Traveloka Indonesia Lodging & Xperience Articles

Traveloka is one of Southeast Asia's largest travel booking platforms. This actor reads its public guest-house and hostel listing pages across Indonesia's major cities and resort areas, and its Traveloka Xperience content hub, returning structured records for lodging and travel-guide articles alike. No login or cookies required.

## What this actor does

- **Four modes:** `search`, `browseByCity`, `browseExplore`, `byUrl`
- **Hotel listings:** 21 verified city/area pages (Yogyakarta, Bali, Bandung, Surabaya, Malang, Semarang, Labuan Bajo, Bogor, Tangerang, Bekasi, Medan, Makassar, Palembang, Kuta, Canggu, Legian, Nusa Dua — guest houses and hostels)
- **Search by city:** type `yogyakarta`, `bali`, `bandung`… and get hotels; type any travel keyword and get matching explore articles
- **Explore articles:** 12+ Traveloka Xperience travel guides with titles, descriptions, authors, publication dates, word counts
- **Full article details:** word count, reading time, header images, tags, categories
- **Filters:** min user rating, min star rating, min review count, keyword-in-name
- **Empty fields are omitted**

## Output per hotel

- `hotelId` — Traveloka property id
- `name`, `displayName`, `location` (area, city)
- `starRating`, `userRating` (0-10), `numReviews`, `userRatingInfo` (Very Good / Excellent…)
- `accommodationType`, `travelTheme`, `hotelFeatures[]`
- `price`, `baseFare`, `taxes`, `fees` (site currency)
- `highlightedReview`, `reviewerName`
- `seoPath`, `seoPathType`
- `images[]`, `imageUrl`
- `sourceUrl` — the accommodation listing page
- `recordType: "hotel"`, `scrapedAt`

## Output per article

- `articleId`, `title`, `subtitle`, `description`, `articleUrl`
- `authorName`, `publishedDate`, `imageUrl`, `tags[]`
- On article detail pages additionally: `authorPicture`, `publishedTime`, `wordCount`, `readingTimeSec`, `readDuration`, `headerImage` (first header image), `headerImages[]`, `subCategories[]`, `shareLink`
- `recordType: "article"`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `browseByCity` / `browseExplore` / `byUrl` |
| `searchQuery` | string | `yogyakarta` | City name or travel keyword (mode=search) |
| `citySlug` | string | – | 21-city dropdown of accommodation pages (mode=browseByCity) |
| `startUrls` | array | – | traveloka.com URLs (mode=byUrl) |
| `minRating` | int | – | Min user rating (1-10) |
| `minStarRating` | int | – | Min star rating (1-7) |
| `minReviewCount` | int | – | Min review count |
| `containsKeyword` | string | – | Only hotels whose name contains this text |
| `sortBy` | string | `relevance` | `relevance` / `ratingDesc` / `mostReviewed` / `starDesc` |
| `includeArticles` | boolean | `false` | In search mode, also emit every explore article |
| `maxItems` | int | `50` | Hard cap (1–1000) |
| `proxyConfiguration` | object | – | Optional; only used lazily if Traveloka blocks a request |

## Examples

### Example: search hotels in Yogyakarta

```json
{
  "mode": "search",
  "searchQuery": "yogyakarta",
  "maxItems": 50
}
```

### Example: highly-rated guest houses in Bali

```json
{
  "mode": "browseByCity",
  "citySlug": "guest-house-bali",
  "minRating": 8,
  "sortBy": "ratingDesc",
  "maxItems": 50
}
```

### Example: travel guides about trains

```json
{
  "mode": "search",
  "searchQuery": "train",
  "includeArticles": true,
  "maxItems": 20
}
```

### Example: fetch pages from URLs

```json
{
  "mode": "byUrl",
  "startUrls": [
    "https://www.traveloka.com/en-id/accommodation/find/hostel-bali",
    "https://www.traveloka.com/en-id/explore/activities/luxury-train-journeys-for-senior-couple/1009917"
  ]
}
```

## Data source

This actor reads Traveloka's public accommodation listing pages (`/accommodation/find/<slug>`) and its Explore content hub (`/explore`) — the same pages Traveloka serves to search engines and visitors without logging in. The listing page's own indicative starting rate (`price`, `baseFare`, `taxes`, `fees`) is included when Traveloka shows one; checking real-time room availability for specific dates still requires Traveloka's own booking/checkout flow, which is out of scope. All 21 city/area slugs offered in the `citySlug` dropdown were verified to return hotel listings.

## Use cases

- **Hotel market research** — track guest-house and hostel supply in Indonesian cities
- **Rating analytics** — user ratings and review counts across budget accommodations
- **Travel content mining** — Traveloka Xperience articles for itineraries and destination research
- **Competitor monitoring** — follow how Traveloka presents its hotel inventory
- **Property databases** — hotel names, areas, ratings, and images for enrichment

## FAQ

**Is this affiliated with Traveloka?**
No — this is an independent actor that reads Traveloka's public listing and Explore pages.

**Does a hotel record include a room price?**
When Traveloka shows an indicative starting rate on the listing page (`price`, with `baseFare`/`taxes`/`fees` when broken out), the actor includes it. Checking live availability and a final price for specific dates requires Traveloka's own booking flow, which is out of scope — so a hotel without a listed rate simply has no price fields rather than a guessed value.

**Why are the city options limited to Indonesia?**
The public accommodation-listing pages this actor can reliably read currently exist for Indonesian destinations; each of the 21 `citySlug` options was verified to return hotel listings before shipping.

**How current is the data?**
Every run reads the live page at the time it runs, so results reflect whatever Traveloka is currently showing.

**What does `userRating` mean?**
Traveloka's own guest-satisfaction score on a 0–10 scale; `userRatingInfo` is the matching human-readable label, e.g. "Very Good" or "Excellent".

**Can I get both hotels and travel articles in one run?**
Yes — in `search` mode, set `includeArticles` to `true` to emit every Explore article alongside any city's hotel matches.

**Do I need to configure a proxy?**
No. The actor runs without one by default; the optional `proxyConfiguration` input only kicks in if Traveloka temporarily blocks a direct request.

**Is there a limit on how many records I can get per run?**
Yes, `maxItems` caps a single run at up to 1000 records.
