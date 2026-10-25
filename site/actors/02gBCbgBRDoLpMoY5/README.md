# Airbnb Stay Finder: Nightly Rates, Fees & Availability

Collect Airbnb stays with the numbers that matter: the **nightly rate**, the **stay total for your dates**, the fee lines Airbnb shows, the host, amenities, coordinates, availability and optional guest reviews — for a whole city or for one listing you already have the link to.

Unlike search-card-only scrapers, this actor can follow every listing into its detail page, request the exact stay quote for your dates and guests, and return a 12-month day-by-day availability calendar. No Airbnb account, login or cookie is needed.

## What this actor does

- **Two modes:** `search` for a location, place ID or map rectangle; `details` for listing URLs and IDs you supply
- **Real price model:** separate `nightlyPrice`, `totalPrice`, `nights`, `currency`, `priceQualifier`, fee lines and whether Airbnb says fees are included
- **Cursor pagination:** 40 Airbnb cards per page, de-duplicated by listing ID, up to 300 records
- **Filters:** dates, guests, nightly price range, room type, property type, bedrooms, beds and bathrooms
- **Optional enrichment:** full detail page (host, amenities, photos, description), stay quote, reviews and a 12-month calendar
- **Global pricing:** 56 currencies and 35 locales, so prices are not forced into USD or GBP
- **Empty fields are omitted** — records never contain `null`, empty strings or empty arrays

## Output per listing

- `id` — numeric Airbnb listing ID
- `url` — direct listing page URL
- `name` — listing or room name
- `type` — the category line Airbnb shows, e.g. `Apartment in North Bergen`
- `roomType` — `Entire home/apt`, `Private room`, `Shared room` or `Hotel room`
- `propertyType` — apartment, house, hotel, villa, etc. (detail mode)
- `location` — city or neighborhood
- `lat`, `lng` — public, approximate coordinates (never the exact address)
- `nightlyPrice`, `totalPrice`, `currency`, `nights` — nightly rate and stay total for the selected dates
- `priceQualifier` — what the displayed quote covers, e.g. `for 5 nights`
- `priceBreakdown` — the price lines Airbnb exposes (nightly line, cleaning/resort fees, discounts)
- `priceIncludesFees` — `true` when Airbnb marks the quote as including all fees
- `totalBeforeTaxes` — when Airbnb exposes a “total before taxes” line
- `originalPrice`, `discount` — pre-discount quote and saving, when Airbnb shows one
- `rating`, `reviewCount` — overall guest rating and number of reviews
- `images`, `thumbnail` — listing photo URLs
- `host`, `hostId`, `hostPhoto`, `hostRating`, `hostReviewCount` — host details (detail mode)
- `isSuperhost`, `isVerified` — host status
- `badges`, `isGuestFavorite` — Airbnb badges shown on the search card
- `amenities`, `amenitiesUnavailable` — included and explicitly unavailable amenities (detail mode)
- `description` — listing description with HTML removed (detail mode)
- `personCapacity` — maximum guests
- `availability` — `isAvailable`, `canInstantBook` and any unavailability reason for the requested dates
- `minNights`, `maxNights` — available inside each calendar day
- `reviews` — optional recent reviews with rating, text, date, reviewer and host response
- `calendar` — optional day-by-day availability for up to 12 months
- `checkIn`, `checkOut` — the stay dates used for the quote
- `sourceUrl` — the search page or listing page that produced the record
- `scrapedAt`, `recordType: "listing"`

Compatibility aliases are also kept for older integrations: `price`, `photos`, `latitude`, `longitude` and `searchUrl`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` or `details` |
| `location` | string | `New York` | City, region, country or neighborhood (mode=search) |
| `placeId` | string | – | Airbnb/Google place ID; skips text matching (mode=search) |
| `neighborhood` | string | – | Optional neighborhood combined with `location` (mode=search) |
| `bbox` | object | – | Map rectangle: `swLat`, `swLng`, `neLat`, `neLng`, optional `zoom` (mode=search) |
| `listingUrls` | array | – | Airbnb room URLs (mode=details) |
| `listingIds` | array | – | Numeric listing IDs (mode=details) |
| `checkIn`, `checkOut` | string | – | Stay dates in `YYYY-MM-DD`; both or neither |
| `adults` | integer | `1` | Adults, 1–16 |
| `children` | integer | `0` | Children, 0–15 |
| `infants` | integer | `0` | Infants, 0–5 |
| `pets` | integer | `0` | Pets, 0–5 |
| `minPrice`, `maxPrice` | integer | `0` | Nightly price range; `0` means no limit |
| `roomType` | string | `Any` | `Any`, `Entire home/apt`, `Private room`, `Shared room`, `Hotel room` |
| `propertyType` | string | `Any` | Airbnb property type, e.g. `Apartment`, `House`, `Hotel` |
| `minBedrooms`, `minBeds`, `minBathrooms` | integer | `0` | Minimum counts; `0` means no minimum |
| `maxListings` | integer | `20` | Hard cap, 1–300 (prefill: `5`) |
| `includeDetails` | boolean | `false` | Fetch each listing page and exact stay quote |
| `includeReviews` | boolean | `false` | Add recent guest reviews |
| `maxReviews` | integer | `12` | Reviews per listing, 1–24 |
| `includeCalendar` | boolean | `false` | Add the availability calendar |
| `calendarMonths` | integer | `12` | Calendar length, 1–12 months |
| `currency` | string | `USD` | One of 56 supported currencies |
| `locale` | string | `en` | Language/region for labels and dates |
| `proxyConfiguration` | object | – | Optional; normally leave empty |

## Example: cheapest useful run

```json
{
  "location": "New York",
  "maxListings": 5
}
```

## Example: a full city scan with filters

```json
{
  "location": "Lisbon, Portugal",
  "checkIn": "2027-05-10",
  "checkOut": "2027-05-17",
  "adults": 2,
  "minPrice": 80,
  "maxPrice": 250,
  "roomType": "Entire home/apt",
  "minBedrooms": 1,
  "maxListings": 120,
  "currency": "EUR",
  "locale": "pt-PT"
}
```

## Example: exact detail, quote, reviews and calendar

```json
{
  "mode": "details",
  "listingUrls": ["https://www.airbnb.com/rooms/23222680"],
  "checkIn": "2027-03-04",
  "checkOut": "2027-03-09",
  "adults": 2,
  "includeReviews": true,
  "maxReviews": 24,
  "includeCalendar": true,
  "calendarMonths": 6,
  "currency": "USD"
}
```

## Example: map rectangle instead of a city name

```json
{
  "bbox": {
    "swLat": 40.7075,
    "swLng": -74.0135,
    "neLat": 40.7904,
    "neLng": -73.9591,
    "zoom": 13
  },
  "checkIn": "2027-04-01",
  "checkOut": "2027-04-04",
  "adults": 2,
  "maxListings": 80,
  "includeDetails": true
}
```

## Use cases

- **Short-term rental pricing** — compare nightly rates and stay totals across a neighborhood before setting your own calendar
- **Travel research** — export a city's stays with ratings, room type and amenities into a spreadsheet or BI tool
- **Market monitoring** — re-run the same dates monthly to track rate and availability changes
- **Host competitive analysis** — benchmark your listing against nearby Superhosts with similar capacity
- **Investment screening** — map approximate coordinates to study short-term rental density by area
- **Review mining** — pull recent guest feedback for a shortlist of properties

## FAQ

### Is `nightlyPrice` the same as the number on the search card?

Usually not. Airbnb's search card shows the **stay total** for the selected dates. `totalPrice` is that quote; `nightlyPrice` is parsed from Airbnb's own nightly line (for example, `5 nights x $335.80`). When you provide dates, both refer to those exact dates. Without dates, Airbnb still returns a five-night display quote, which the actor labels with `nights: 5`.

### Are all fees included in `totalPrice`?

Airbnb's quote can include cleaning, service and resort fees, and sometimes a “Prices include all fees” notice. The actor exposes `priceBreakdown` and `priceIncludesFees` so you can see what Airbnb included. Taxes and local charges can still vary by destination and are not always part of the displayed quote; treat `totalPrice` as Airbnb's quoted stay price, not a guaranteed checkout total.

### Why is the price missing on some records?

In `details` mode without dates, Airbnb does not show a stay price. Those records still include the listing data. Add `checkIn` and `checkOut` to get a quote. In `search` mode, a small number of cards legitimately omit the primary price line; the actor falls back to Airbnb's nightly explanation when available.

### How many listings can I get?

`maxListings` is capped at 300. Airbnb returns 40 cards per page and de-duplicates/reorders between pages, so a deep search typically yields around 230–240 unique listings per query. Use different neighborhoods, map rectangles or price ranges to cover more of a market. The actor never claims “all listings”.

### Why did my location fail?

Airbnb returns a generic feed for gibberish queries instead of zero results. The actor validates the location through Airbnb's own autocomplete and fails with a clear message when nothing matches, so you never receive unrelated rows. Neighborhoods, cities, regions and countries all work; you can also supply a `placeId` or a `bbox`.

### Do I need a proxy or an Airbnb account?

No. The actor reads Airbnb's public pages and GraphQL responses without cookies or login. It connects directly first; if Airbnb blocks a request, it automatically retries through an Apify proxy and then a browser. Nothing needs to be configured.

### Why are coordinates approximate?

Airbnb publishes approximate map coordinates before booking to protect host privacy. Use them for area analysis, not for deriving a street address.

### Can I get per-day prices in the calendar?

The availability calendar reports whether each date is available, check-in/check-out eligibility and min/max nights. Airbnb does not expose a per-day price in that endpoint. For a price on specific dates, set `checkIn`/`checkOut` and use the stay quote.

### Is this affiliated with Airbnb?

No. This is an independent, third-party actor that reads publicly accessible Airbnb pages and responses. It is not affiliated with or endorsed by Airbnb.
