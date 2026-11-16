# Tiqets Attraction & Ticket Price Finder

Tiqets lists museum, tour and attraction tickets across major cities worldwide. This actor searches that catalog by keyword, browses every venue in a city or category, or fetches specific venue/product URLs and IDs. It returns ratings, review counts, prices in 21 currencies, discount percentages, images, coordinates, categories, inclusions, opening hours and optional availability dates/timeslots. No account, user cookies or API key required.

## What this actor does

- **Five modes:** `search`, `browseByCity`, `browseByCategory`, `byUrl`, `byId`
- **Paged collection** — gathers up to `maxItems` across all result pages
- **81 destination cities** and **66 category tags**, verified against Tiqets' public catalog
- **17 site locales** and **21 supported currencies**
- **Venue, product and package records** with nested venue/city/country metadata
- **Optional availability** — dates and timeslots for products and packages
- **Server-side filters where verified** — `cityIds` and `experienceTagIds` in search; `sortType=popularity|rating` in city/category browse
- **Client-side filters** — min/max rating, min/max price, top-rated only and discount-only in browse modes
- **Empty fields are omitted at every depth** — no `null`, `""`, `[]` or `{}` in output

## Modes

| Mode | What it does |
|---|---|
| `search` | Keyword search; supports one query or several queries |
| `browseByCity` | All venues in a city; supports `city`, `cities[]` and `cityIds[]` |
| `browseByCategory` | Products in a city category; supports `category` and `experienceTagIds[]` |
| `byUrl` | Venue, product, city or category URLs; the URL locale is preserved |
| `byId` | Venue IDs and product/package IDs, resolved to their current Tiqets page |

City and category browse also accept multi-city inputs. Search accepts multiple queries; results are de-duplicated by product/venue ID.

## Output per venue, product or package

One dataset record per venue, ticket product or package. Fields that exist for the record are emitted; empty fields are omitted.

- `recordType` — `venue`, `product` or `package`
- `venueId` / `productId`, `name` / `productTitle`
- `description`, `shortDescription`, `summary`
- `images[]`, `imageUrl`
- `rating`, `reviewCount`, `reviews[]` (up to 3 samples with author, date, rating and text)
- `price`, `priceCurrency`, `priceEur`, `displayPrice`, `discountPercentage`
- `venue` `{id,name,url}`, `city`, `cityId`, `cityInfo` `{id,name,slug}`, `country` `{id,name}`, `countryId`
- `categories[]`, `tags[]`, `category`
- `duration`, `keyDetails`, `whatsIncluded`, `whatsExcluded`, `openingHours`
- `checkoutDisabled`, `offerCount`, `topPrice`, `topPriceEur`
- `latitude`, `longitude`
- `availabilityDates[]`, `availabilityTimeslots` `{date: [times]}` (optional; omitted when none)
- `productUrl`, `sourceUrl`, `slug`, `startDate`, `language`, `recordType`, `scrapedAt`

Detail modes (`byUrl`, `byId`) parse the page's JSON-LD and dataLayer. A product page does not contain coordinates, so the actor fetches its venue page once (cached per run) to add coordinates, country and extra images.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `search` | `search` / `browseByCity` / `browseByCategory` / `byUrl` / `byId` |
| `searchQuery` | string | `eiffel tower` | Free-text query (mode=search) |
| `searchQueries` | array | – | Multiple queries (mode=search); combined and de-duplicated |
| `city` | select | – | One destination city (browse modes) |
| `cities` | array | – | Multiple city slugs (browse modes) |
| `cityIds` | array | – | Numeric city IDs; server-side filter in search, browse targets in browse modes |
| `category` | select | – | One of 66 verified category tags (mode=browseByCategory) |
| `experienceTagIds` | array | – | Numeric category tag IDs; server-side filter in search, category paths in browse |
| `startUrls` | array | – | Venue/product/city/category URLs (mode=byUrl); locale preserved |
| `venueIds` | array | – | Numeric venue IDs (mode=byId) |
| `productIds` | array | – | Numeric product IDs (mode=byId) |
| `language` | select | `en` | 17 locales: `ca,cs,da,de,el,en,es,fr,it,ja,ko,nl,pl,pt,ru,sv,zh` |
| `currency` | select | `EUR` | 21 supported currencies: `EUR,USD,GBP,CHF,CAD,AUD,AED,BRL,CZK,DKK,HKD,HUF,INR,JPY,MXN,NOK,NZD,PLN,SEK,SGD,THB` |
| `minRating` | integer | – | Client-side lower rating bound (1–5); missing ratings pass |
| `maxRating` | integer | – | Client-side upper rating bound (1–5); missing ratings pass |
| `minPrice` | integer | – | Client-side lower price bound in the selected currency; missing prices pass |
| `maxPrice` | integer | – | Client-side upper price bound in the selected currency; missing prices pass |
| `topRatedOnly` | boolean | `false` | Only ratings 4.5+ |
| `hasDiscount` | boolean | `false` | Keeps only records with `discountPercentage > 0` |
| `sortType` | select | `popularity` | `popularity` or `rating` (city/category browse only; search ignores sort) |
| `includeExtraVenues` | boolean | `true` | SSR fallback only: also emit venue links outside the main listing |
| `includeAvailability` | boolean | `false` | Fetch dates and timeslots for product/package records |
| `availabilityDays` | integer | `14` | Days ahead to request (1–30) |
| `maxItems` | integer | `50` | Hard cap on emitted records (1–10,000) |
| `proxyConfiguration` | proxy | – | Optional user-supplied proxy; direct requests are tried first and free Apify Proxy is used only if they are blocked |

### Example: search

```json
{
  "mode": "search",
  "searchQuery": "louvre",
  "language": "en",
  "currency": "EUR",
  "maxItems": 50
}
```

### Example: browse all venues in Paris

```json
{
  "mode": "browseByCity",
  "city": "paris",
  "maxItems": 200
}
```

### Example: museums in Paris (96 products)

```json
{
  "mode": "browseByCategory",
  "city": "paris",
  "category": "museums",
  "maxItems": 100
}
```

### Example: fetch specific pages (locale preserved)

```json
{
  "mode": "byUrl",
  "startUrls": [
    { "url": "https://www.tiqets.com/fr/billets-tour-eiffel-l144586/" },
    { "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/tickets-for-musee-d-orsay-dedicated-entrance-p973980/" },
    { "url": "https://www.tiqets.com/en/things-to-do-in-paris-c66746/museums-t2968/" }
  ]
}
```

### Example: venue and product IDs

```json
{
  "mode": "byId",
  "venueIds": ["144586"],
  "productIds": ["973980"],
  "includeAvailability": true,
  "availabilityDays": 7
}
```

## Use cases

- **Travel product research** — compare attraction and museum ticket prices across cities
- **Itinerary planning** — enrich trip catalogues with live ticket, rating and opening-hours data
- **Price monitoring** — track discount percentages and availability for key attractions
- **Marketplace analytics** — analyse category coverage and venue counts by destination
- **Availability checks** — collect dates and timeslots for ticketed products and packages

## FAQ

**Do I need an API key or account?**
No. It requires no account or user cookies.

**Are prices in my selected currency?**
Yes for search, city and category results. Some detail pages are served in EUR by Tiqets; when availability is enabled, the selected-currency availability price is used for detail records. Price filters on detail modes compare the returned page price, which may be EUR.

**Why does a product record have coordinates when the product page has none?**
The actor fetches the product's venue page once per run and merges coordinates, country and extra images.

**How fresh is the data?**
Every run reads live public pages/endpoints, so values reflect Tiqets at run time.

**Is this actor affiliated with Tiqets?**
No. This is an independent third-party actor using Tiqets' public website.

**How many records can I get in one run?**
Up to 10,000 (`maxItems`). The actor paginates until the cap or the last page.
## Verified counts and limits

- **Paris city browse:** 134 venues; **Rome:** 110; **Paris museums:** 96 products (verified 2026-11).
- **Page size is 20.** The actor paginates automatically until the cap or last page.
- **`maxItems` up to 10,000.** Pagination stops at the cap or the last page. Filtering happens after fetch; if filters drop many rows, the actor continues through all pages.
- **Search sorting is not available.** Price sorting is not offered by the source.
- **City/category sort** supports popularity and rating.
- **Beijing has no current Tiqets city destination.** The old city ID resolves elsewhere, so Beijing is not offered.
- **Discount filtering is applied to emitted records.** This avoids unrelated global discount results.
- **Availability is optional and applies to products and packages.** City browse returns venues, which have no single product ID, so availability is omitted for those records. Timeslots are requested once per available date.
- **Product/package IDs resolve to their current page**, including IDs missing from a locale index.
- **Missing rating/price pass filters** by design; this keeps package cards and sparse listing rows that do not publish those fields.

## Data source and robots

Tiqets (tiqets.com) is an online ticketing platform for attractions, museums and tours. This actor reads Tiqets' public pages and endpoints. No account, user cookies or API key is required. The actor chooses a working connection automatically; no proxy setup is needed.

The actor uses public endpoints also used by Tiqets' own front end. It is not a strict robots-only crawler; use detail-only modes if that constraint is required.
