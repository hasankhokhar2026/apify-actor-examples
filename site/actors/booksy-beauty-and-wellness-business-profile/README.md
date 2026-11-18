# Booksy Beauty & Wellness Business Profile Scraper

Booksy hosts the booking pages for salons, barbers, spas, and other beauty and wellness businesses, but its site only lets you browse one search or category at a time with no export option. This actor pulls those listings into structured records — ratings, services, staff, amenities, and contact details — by keyword search, by service category, or by a list of specific business IDs.

## What this actor does

- Searches Booksy by keyword and location (city name or GPS coordinates) and returns matching businesses with distance from the search point.
- Browses an entire Booksy service category — hair, barber, nails, massage, tattoos, and 14 others — near a location without needing a keyword.
- Looks up specific businesses by their Booksy ID to pull the richest profile available: staff list, top services, amenities, booking policy, state/ZIP, and written reviews.
- Filters results post-search by minimum/maximum rating, minimum review count, category, and recommended-badge status.
- Only includes fields Booksy actually published for that business; fields with no data (no Instagram link, no listed staff, etc.) are left out of the record rather than sent as empty values.

## Output per business

| Field | Description |
|---|---|
| `businessId` | Booksy's business identifier |
| `name` | Business name |
| `slug` | URL slug used in the profile link |
| `profileUrl` | Full Booksy profile URL |
| `address` | Street address |
| `city` | City |
| `latitude` / `longitude` | GPS coordinates |
| `rating` | Average rating, 0–5 scale |
| `reviewCount` | Total number of reviews |
| `starRating` | Rounded star rating |
| `category` / `categoryId` | Primary service category name and Booksy's category ID |
| `serviceCategories` | All service categories this business offers |
| `staff` | Staff member names (business-ID lookups) |
| `description` | Business bio text (business-ID lookups) |
| `website` | Business's own website URL |
| `facebookUrl` / `instagramUrl` | Social profile links |
| `ecommerceUrl` | Business's online shop link, when it has one |
| `bookingEnabled` | Whether online booking is turned on |
| `isRecommended` | Booksy "recommended" badge |
| `bestOfBooksyBadge` | "Best of Booksy" award badge |
| `isMobileService` | True for traveling/mobile-only services |
| `pricingLevel` | Price tier, 1 (budget) to 4 (luxury) |
| `distanceKm` | Distance from the search point, for keyword and category searches |
| `amenities` | Listed amenities, e.g. parking, Wi-Fi |
| `topServices` | Names of the business's most booked services |
| `imageUrl` | Cover photo URL |
| `logoUrl` | Logo image URL |
| `openHours` | Opening hours by day |
| `isPromoted` | Whether the listing is a paid "Promoted" placement |
| `maxDiscountRate` | Largest active discount percentage across its services |
| `hasLowAvailability` | Booksy's own "low availability" flag |
| `offersVirtualServices` | Whether virtual/online services are offered |
| `offersOnlineVouchers` | Whether online vouchers are sold |
| `acceptsBooksyGiftCards` / `acceptsBooksyPay` | Accepted payment/gift options |
| `state` / `zipCode` | State and postal code (business-ID lookups only) |
| `bookingPolicy` | Cancellation/change policy text (business-ID lookups only) |
| `bookingLeadTimeDays` | How far in advance bookings can be made (business-ID lookups only) |
| `topReviews` | Up to a few written reviews with text, rating, reviewer name, date, and service (business-ID lookups only) |
| `sourceUrl` | The Booksy URL the record came from |
| `scrapedAt` | UTC timestamp of the scrape |
| `recordType` | Always `"business"` |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` (keyword + location), `byCategory` (browse a category), or `byBusinessId` (specific IDs). Required. |
| `searchQuery` | string | `hair salon` | Keyword to search for in `search` mode. |
| `location` | string | `New York` | City name to search near, used when latitude/longitude aren't set. |
| `latitude` | number | – | GPS latitude; overrides `location` when set. |
| `longitude` | number | – | GPS longitude; overrides `location` when set. |
| `radiusKm` | integer | `10` | Search radius hint sent to Booksy. Booksy may still return businesses outside this radius when nearby matches are thin — use `distanceKm` on each record to filter strictly. |
| `category` | string | `hair` | Service category slug to browse in `byCategory` mode. |
| `businessIds` | array | `[]` | Booksy business IDs to fetch in `byBusinessId` mode, e.g. `688238` from `https://booksy.com/en-us/688238_name`. |
| `minRating` | number | – | Keep only businesses rated at or above this value (0–5). |
| `maxRating` | number | – | Keep only businesses rated at or below this value (0–5). |
| `minReviewCount` | integer | – | Keep only businesses with at least this many reviews. |
| `filterCategory` | string | – | Narrow results to one category slug, e.g. `nails`. |
| `isRecommended` | boolean | `false` | When true, keep only businesses with Booksy's "recommended" badge. |
| `maxItems` | integer | `50` | Maximum number of businesses to return. |

### Example: keyword search near a city

```json
{
  "mode": "search",
  "searchQuery": "barber",
  "location": "Chicago",
  "maxItems": 40
}
```

### Example: browse a category with rating filters

```json
{
  "mode": "byCategory",
  "category": "nails",
  "location": "Los Angeles",
  "minRating": 4.5,
  "minReviewCount": 20,
  "maxItems": 100
}
```

### Example: specific business profiles

```json
{
  "mode": "byBusinessId",
  "businessIds": ["688238", "1439833"]
}
```

## Use cases

- **Lead generation for beauty-industry vendors** — build contact lists of salons and spas by city, category, and rating threshold.
- **Competitive benchmarking** — compare ratings, pricing tiers, and amenities across businesses in the same category and area.
- **Franchise or site-selection research** — see how many businesses in a category already serve a location before entering a market.
- **Reputation tracking** — pull review counts, star ratings, and recent written reviews for specific businesses over time.
- **Directory and city-guide building** — gather structured profiles (hours, services, contact links) for a curated listing site.

## FAQ

**Do I need a Booksy account to run this?**
No. All three modes read Booksy's public search and profile pages, which don't require logging in.

**What's the difference between the three modes?**
`search` matches a keyword near a location; `byCategory` browses everything Booksy lists under one service category near a location; `byBusinessId` skips search entirely and fetches named businesses directly, which also unlocks extra fields like staff, amenities, booking policy, and written reviews that search results don't carry.

**Why do some records have more fields than others?**
Search and category results only carry what Booksy's listing view exposes. Looking the same business up by ID pulls its full profile, which adds fields such as `staff`, `topServices`, `amenities`, `bookingPolicy`, `state`, `zipCode`, and `topReviews`.

**Will I always get results within `radiusKm`?**
Not strictly — `radiusKm` is a hint Booksy's own search uses, and it can widen the radius when there aren't enough nearby matches, the same way booksy.com behaves for a visitor. Use the `distanceKm` field on each record to filter to an exact radius afterward.

**Why is a field like `ecommerceUrl` or `staff` missing from a record?**
That business hasn't published that information on Booksy, or you're in a mode that doesn't fetch it. Fields with no value are left out of the record instead of being sent empty.

**Can I combine a keyword search with a category filter?**
Yes — set `mode` to `search` and also set `filterCategory` to a category slug to keep only matching results from the search.

**Are written reviews included for every business?**
Only in `byBusinessId` mode, and only up to the handful of recent reviews Booksy exposes on the profile page itself — `search` and `byCategory` modes return rating and review count but no review text.

**Is this affiliated with Booksy?**
No. This actor reads Booksy's public pages and is not affiliated with, endorsed by, or connected to Booksy in any way.
