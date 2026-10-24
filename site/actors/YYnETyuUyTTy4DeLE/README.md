# Yandex Maps Business Search, Details & Reviews Scraper

Pull business data from [Yandex Maps](https://yandex.com/maps/), the map service most used in Russia and widely used across Kazakhstan, Uzbekistan, Belarus and Turkey. Search by keyword, fetch the business card for specific organizations, or collect customer reviews, across six regional domains and eight interface languages.

## What this actor does

- **Three modes:** `searchPlaces` (keyword search), `getDetails` (full business detail by URL), `getReviews` (customer reviews by URL)
- Search results return name, address, rating, review count, categories and photos; detail lookups add coordinates, phone, website and the opening-hours line
- Collects review author, rating, text, date, and likes when scraping reviews
- Filters search results by a minimum star rating, and loads reviews newest first, highest rated first, or in Yandex's default order
- Covers six Yandex domains (`yandex.com`, `.ru`, `.com.tr`, `.kz`, `.uz`, `.by`) and eight UI languages
- Leaves out any field Yandex doesn't show for a business or review, so records only contain fields with values

## Output per record

Every record carries a `recordType` field — `"place"` or `"review"`. If nothing is found for a query or URL, no record is written for it.

### Place record (`recordType: "place"`, modes `searchPlaces` and `getDetails`)

- `placeId` — Yandex Maps organization ID
- `name`, `url` — business name and Yandex Maps page URL
- `address` — street address as shown by Yandex
- `coordinates` — object `{ lat, lng }` (`getDetails` only)
- `phone`, `website` — contact details (`getDetails` only)
- `rating`, `reviewCount` — star rating and total review count
- `categories` — array of business categories (e.g. `"Coffee shop"`, `"Cafe"`)
- `workingHours` — object keyed by day of week (`getDetails` only); filled when the business card's hours line can be read as a schedule, e.g. a 24-hour business
- `openStatus` — the hours line as Yandex shows it, e.g. "Open until 22:00", when it can't be turned into `workingHours` (`getDetails` only)
- `photos` — array of photo URLs (up to 20 on detail pages; search results return the thumbnails shown in the result card)
- `scrapedAt` — ISO 8601 collection timestamp

### Review record (`recordType: "review"`)

- `placeId`, `placeName`, `placeUrl` — the business the review belongs to
- `reviewId` — review key, usually the reviewer's profile ID joined with the review date
- `author`, `authorUrl` — reviewer name and profile link
- `rating` — star rating given
- `text` — review text
- `date` — review date (`YYYY-MM-DD` when Yandex provides a machine-readable date)
- `likes` — like count on the review
- `scrapedAt` — ISO 8601 collection timestamp

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `searchPlaces` | `searchPlaces` / `getDetails` / `getReviews` |
| `searchQueries` | array of strings | – | Search queries combining business type and location (mode=`searchPlaces`) |
| `businessUrls` | array of strings | – | Yandex Maps business page URLs (mode=`getDetails` or `getReviews`) |
| `yandexDomain` | string | `yandex.ru` | Regional domain: `yandex.com`, `yandex.ru`, `yandex.com.tr`, `yandex.kz`, `yandex.uz`, `yandex.by` |
| `language` | string | `en` | UI/results language: `en`, `ru`, `tr`, `de`, `fr`, `uk`, `kk`, `uz` |
| `maxItems` | integer | `20` | Maximum places per search query, or reviews per business URL (1–500); not used by `getDetails` |
| `minRating` | string | `any` | Minimum rating filter for `searchPlaces`: `any`, `3`, `3.5`, `4`, `4.5` |
| `reviewsSortOrder` | string | `by_date_desc` | Review sort order for `getReviews`: `by_date_desc`, `by_rating_desc`, `by_relevance` |
| `proxyConfiguration` | object | – | Recommended (the form is prefilled with a residential proxy); Yandex may show a CAPTCHA to data-center IPs |

### Example: search for coffee shops in Moscow

```json
{
  "mode": "searchPlaces",
  "searchQueries": ["coffee shops Moscow"],
  "minRating": "4",
  "maxItems": 30
}
```

### Example: full details for a specific business

```json
{
  "mode": "getDetails",
  "businessUrls": ["https://yandex.com/maps/org/shokoladnitsa/123456789/"]
}
```

### Example: most recent reviews for a business, in Russian

```json
{
  "mode": "getReviews",
  "businessUrls": ["https://yandex.com/maps/org/shokoladnitsa/123456789/"],
  "language": "ru",
  "reviewsSortOrder": "by_date_desc",
  "maxItems": 100
}
```

### Example: Turkish restaurant search

```json
{
  "mode": "searchPlaces",
  "searchQueries": ["sushi restaurant Istanbul"],
  "yandexDomain": "yandex.com.tr",
  "language": "tr"
}
```

## Use cases

- **Lead generation** — build lists of local businesses with search, then run `getDetails` on them for phone numbers and websites
- **Market research** — survey competitors, ratings, and business density in a city or category
- **Brand monitoring** — find a brand's branches through search and track their customer reviews
- **Site selection** — scan nearby amenities and service density for a potential location
- **Reputation tracking** — pull recent reviews on a schedule to watch sentiment trends

## FAQ

**Can I search any city across Russia and the CIS?**
Yes, as long as Yandex Maps lists businesses there. Include the city name in your search query, e.g. `restaurants Novosibirsk`.

**Does this work for Turkish businesses?**
Yes. Set `yandexDomain` to `yandex.com.tr` and `language` to `tr` for the best results on Turkish locations.

**How many results can one search return?**
Up to `maxItems` (max 500) per query, and each query in `searchQueries` gets its own allowance. The actor keeps loading more results until it reaches that number, Yandex stops returning new businesses, or a scrolling limit is hit, so very broad searches may come back with fewer.

**Can I get reviews in their original language?**
Review text is returned in whatever language the reviewer wrote it. The `language` setting changes the interface language, which affects things like category names and the opening-hours line, not the reviews themselves.

**Is there a cap on reviews per business?**
`maxItems` is applied to each business URL separately, up to 500. The actor stops earlier when a business has fewer reviews or when no new reviews load after scrolling.

**Can I filter search results by rating?**
Yes — use `minRating` to drop businesses below a chosen threshold, e.g. `4.5` for only top-rated places. Businesses without a rating are dropped too whenever a threshold is set. The filter only applies to `searchPlaces`.

**Why does the actor recommend a proxy?**
Yandex Maps may show a CAPTCHA to automated requests from data-center IP addresses; a residential proxy makes that much less likely. In `searchPlaces` mode, if a query hits a CAPTCHA on your chosen domain, the actor tries `yandex.ru`, `yandex.com.tr` and `yandex.uz` before skipping the query.

**Do I need to know a business's URL ahead of time?**
Only for `getDetails` and `getReviews` mode. Use `searchPlaces` first to discover businesses by keyword, then feed their URLs into the other modes.

**Is this affiliated with Yandex?**
No. This is an independent, third-party actor that reads Yandex Maps' public pages; it isn't affiliated with or endorsed by Yandex.
