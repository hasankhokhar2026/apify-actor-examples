# Booksy Beauty & Wellness Business Profile Scraper

Booksy lists hundreds of thousands of salons, barbershops, nail studios, spas, and independent beauty professionals, but the site gives you one page at a time and no export button. This actor turns that public marketplace into structured business and review records: full service menus with prices and durations, staff, opening hours, amenities, photos, ratings, written reviews, and contact links. It works by keyword, category, business ID, or a pasted Booksy URL, across 17 Booksy markets.

## What this actor does

- **Five modes:** search by keyword, browse a service category, look up business IDs or profile URLs, export written reviews, or paste Booksy search/profile URLs.
- **Real pagination:** reads every result page Booksy exposes for a query, up to the marketplace's 10,000-result ceiling, with duplicate removal across promoted listings.
- **Rich profiles:** service menus with prices, durations, variants, deposits, and discounts; staff with positions and bios; weekly hours; amenities; photo galleries; booking and cancellation policy.
- **17 markets:** United States, United Kingdom, Ireland, Australia, Canada, South Africa, Poland, Spain, Mexico, Argentina, Chile, Colombia, France, Brazil, Portugal, Netherlands, and Germany, with the market's local currency.
- **Filters that match how buyers search:** rating range, minimum review count, primary category, recommended badge, open now, online/traveling services, special offers, gift cards, Booksy Pay, availability date, and sort order.
- **Clean records:** fields the source did not publish for a business are left out instead of being sent as null, empty text, or a sentinel.
- **Honest run status:** distinguishes a genuine zero-result query from HTTP or transport failures after retries, including partial results.
- **Local-language URLs:** `byUrl` recognizes translated category URLs such as `/pl-pl/s/fryzjer` and `/pt-br/s/spa-massagem`.

## Output per business

- `businessId` — Booksy's business identifier
- `name`, `slug`, `profileUrl`, `country`, `currency` (market currency, even without service details)
- `address`, `city`, `state`, `zipCode`, `latitude`, `longitude`, `distanceKm`
- `rating` — exact average, 0–5
- `reviewCount`, `starRating`
- `category` — primary category slug; `categoryId` — Booksy's local category ID
- `serviceCategories` — every category the business is listed under
- `services[]` — category, name, description, serviceId, treatmentId, treatmentName, price, priceText, durationMinutes, variantCount, bookable, onlineService, travelingService, stafferIds, photoUrls, variants[]
- `serviceCount`, `priceFrom`, `priceTo`, `topServices`
- `staff` — staff names; `staffMembers[]` — staffId, name, position, description, photoUrl, reviewsRankScore, active, visible; `staffCount`
- `description`, `website`, `facebookUrl`, `instagramUrl`, `ecommerceUrl`, `contactName`
- `bookingEnabled`, `bookingMode`, `bookingConfirmation`, `bookingPolicy`, `bookingLeadTimeDays`, `bookingChangeWindowHours`
- `depositPolicy`, `depositCancelTimeHours`, `serviceFee`
- `openHours[]` — day_of_week, dayName, open_from, open_till; `openHoursNote`
- `amenities` — human-readable labels; `amenityDetails[]` — key and label
- `hasParking`, `hasWheelchairAccess`, `acceptsCreditCards`
- `imageUrl`, `imageUrls[]`, `logoUrl`
- `isRecommended`, `bestOfBooksyBadge`, `isMobileService`, `isPromoted`, `maxDiscountRate`, `hasLowAvailability`
- `offersVirtualServices`, `offersOnlineVouchers`, `acceptsBooksyGiftCards`, `acceptsBooksyPay`, `pricingLevel` (when Booksy returns it)
- `profileType`, `newOnMarketplace`, `isBListListing`, `isRentingVenue`, `umbrellaVenueName`, `salonNetwork`, `hasSafetyRules`, `donationsEnabled`, `waitlistDisabled`
- `topReviews[]` — text, rating, reviewerName, date, appointmentDate, verified, replyText, serviceNames, staffNames, photoUrls
- `sourceUrl`, `scrapedAt`, `recordType` (`"business"`)

## Output per review (mode = `reviews`)

- `reviewId`, `rating`, `title`, `text`
- `authorName`, `authorId`, `authorAvatarUrl`
- `createdAt`, `updatedAt`, `appointmentDate`, `verified`, `anonymized`
- `replyText`, `replyUpdatedAt`
- `serviceNames[]`, `serviceIds[]`, `staffNames[]`, `staffIds[]`, `photoUrls[]`
- `businessId`, `businessName`, `businessProfileUrl`, `businessRating`, `businessReviewCount`
- `country`, `sourceUrl`, `scrapedAt`, `recordType` (`"review"`)

Review records are written without invented text: if a customer left only a star rating, `text` is omitted.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search`, `byCategory`, `byBusinessId`, `reviews`, or `byUrl`. |
| `searchQuery` | string | `hair salon` | Keyword for `search` mode. Required in search mode; an empty or missing value is rejected. Use the market's language outside English markets. |
| `location` | string | `New York` | City or area for `search` / `byCategory`; local-language names work (e.g. `Warszawa`, `Kraków`). Leave empty to search the whole country. |
| `country` | string | `us` | Booksy market code: `us`, `gb`, `ie`, `au`, `ca`, `za`, `pl`, `es`, `mx`, `ar`, `cl`, `co`, `fr`, `br`, `pt`, `nl`, `de`. |
| `businessIds` | array | `[]` | Business IDs or profile URLs for `byBusinessId` / `reviews`. URLs select their own country. |
| `startUrls` | array | `[]` | Booksy search and/or profile URLs for `byUrl` mode. Local-language category URLs are recognized as category searches. |
| `latitude` | number | - | GPS latitude; overrides `location` when longitude is also set. |
| `longitude` | number | - | GPS longitude; overrides `location` when latitude is also set. |
| `radiusKm` | integer | `10` | Search radius hint in kilometres, 1–100. |
| `category` | string | `hair` | Category for `byCategory`: `hair`, `barber`, `nails`, `skin-care`, `brows-and-lashes`, `massage`, `makeup`, `wellness-and-spa`, `braids-and-locs`, `tattoos`, `medical-aesthetics`, `hair-removal`, `home-services`, `piercing`, `pet-services`, `dental`, `health-and-fitness`, `professional-services`, `other`. |
| `sortBy` | string | `score` | `score`, `distance`, `rating`, `price`, or `name`. |
| `availableOn` | string | - | Optional availability date in `YYYY-MM-DD` format. |
| `openNow` | boolean | `false` | Keep only businesses open at the time of the run. |
| `hasOnlineServices` | boolean | `false` | Keep only businesses offering virtual/online services. |
| `hasTravelingServices` | boolean | `false` | Keep only mobile/traveling service businesses. |
| `hasSpecialOffers` | boolean | `false` | Keep only businesses with an active special offer. |
| `acceptsGiftCards` | boolean | `false` | Keep only businesses accepting Booksy gift cards. |
| `acceptsBooksyPay` | boolean | `false` | Keep only businesses accepting Booksy Pay. |
| `minRating` | number | - | Minimum average rating, 0–5 (business modes). |
| `maxRating` | number | - | Maximum average rating, 0–5 (business modes). |
| `minReviewCount` | integer | - | Minimum number of reviews (business modes). |
| `filterCategory` | string | `Any` | Keep only business records in one primary category, or `Any`. |
| `isRecommended` | boolean | `false` | Keep only businesses with the Booksy Recommended badge (business modes). |
| `includeDetails` | boolean | `true` | Fetch the full profile (services, staff, hours, amenities, contacts, booking policy) for each result. |
| `includeReviews` | boolean | `false` | Fetch additional written reviews per business into `topReviews` (business modes). |
| `maxReviewsPerBusiness` | integer | `20` | Maximum reviews per business for `includeReviews` or `reviews` mode, 1–1000. |
| `maxItems` | integer | `50` | Maximum records to return, 1–10000. |

### Example: hair salons in New York with full details

```json
{
  "mode": "search",
  "searchQuery": "hair salon",
  "location": "New York",
  "country": "us",
  "minRating": 4.5,
  "minReviewCount": 25,
  "sortBy": "rating",
  "includeDetails": true,
  "maxItems": 100
}
```

### Example: browse barbers in Chicago, several pages

```json
{
  "mode": "byCategory",
  "category": "barber",
  "location": "Chicago",
  "country": "us",
  "radiusKm": 15,
  "maxItems": 300
}
```

### Example: full profiles and reviews for specific businesses

```json
{
  "mode": "reviews",
  "businessIds": ["688238", "https://booksy.com/pl-pl/694_hullhair_fryzjer_3_warszawa"],
  "maxReviewsPerBusiness": 100,
  "maxItems": 500
}
```

### Example: paste Booksy URLs

```json
{
  "mode": "byUrl",
  "startUrls": [
    { "url": "https://booksy.com/en-us/s/hair-salon/18229_chicago" },
    { "url": "https://booksy.com/en-gb/s/barber/1033813_bristol" }
  ],
  "maxItems": 200
}
```

### Example: local-language search in Spain

```json
{
  "mode": "search",
  "searchQuery": "peluqueria",
  "location": "Madrid",
  "country": "es",
  "maxItems": 50
}
```

## Use cases

- **Beauty-supply and distributor sales** — build city-level lead lists of salons, barbers, and spas with contact links, service mix, and size signals.
- **Price benchmarking** — compare haircut, manicure, massage, and spa menus across competitors, including durations, deposits, and discounts.
- **Franchise and site selection** — measure category density and ratings by neighbourhood before opening or expanding.
- **Reputation monitoring** — export new reviews with rating, service, staff, and owner replies on a schedule.
- **Directory and marketplace builders** — seed a local beauty directory with structured profiles, photos, and hours.
- **Market research across countries** — compare service menus and price points between Booksy markets in local currency.

## FAQ

### Do I need a Booksy account or an API key?

No. The actor reads the public Booksy marketplace that any visitor can see. There is no login, cookie, token, or proxy setup.

### What is the difference between search and byCategory?

`search` matches a keyword near a location (for example "balayage" in London). `byCategory` browses Booksy's own category taxonomy (hair, barber, nails, massage, and so on) and is usually the better way to enumerate every business in a category and city.

### Why are some fields or whole records missing?

Booksy lets each business publish only what it wants. A business without a website, staff list, services, or written reviews simply has no value for those fields, so the field is omitted. The record itself is still returned.

### Are phone numbers and emails included?

No. Booksy does not publish business phone numbers or emails on the public profile; the contact channels are the website, Instagram/Facebook links, address, and Booksy profile URL.

### How many businesses can I get from one query?

Booksy caps a single search at 10,000 results. The actor reads every page up to that ceiling and removes promoted duplicates. To go beyond 10,000, split the run by category, location, or a smaller radius.

### Why did I get fewer results than `maxItems`?

The source ran out of unique businesses for that query, or the selected category is not offered in that country. The run status message reports the source count and the reason. Try a broader keyword, a larger radius, a different city, or another category.

### What happens if Booksy returns an error?

The actor retries transient HTTP and network failures with backoff. If a request still fails, the final status message reports the failed request count instead of pretending the source returned zero results. A partial run also says that results may be incomplete.

### Does `maxReviewsPerBusiness` return the full requested count?

Yes, when the business has enough reviews. Review pagination uses a fixed page size and reads the next offset, including values such as 101, 130, 199, and 250.

### Does search work in local languages?

Yes, and it usually must. Booksy search is language-sensitive: "hair" works in the US and UK, but "fryzjer" works in Poland, "peluqueria" in Spain, and "cabelo" in Brazil. Category browsing avoids the keyword entirely where the category exists.

### Are reviews always included?

`byBusinessId` profiles include a small sample of recent reviews. Use `includeReviews` for more per business, or `reviews` mode to export review records with text, rating, author, date, service, staff, and owner reply.

### Do I need to configure a proxy?

No. The actor chooses a working connection to Booksy automatically. Just fill in the input and run it.

### Is this affiliated with Booksy?

No. This is a third-party actor that reads public Booksy marketplace pages and is not affiliated with, endorsed by, or connected to Booksy.
