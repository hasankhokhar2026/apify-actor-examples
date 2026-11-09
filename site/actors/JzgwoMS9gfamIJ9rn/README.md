# Vrbo Destination Rental Listings Extractor

Search [Vrbo](https://www.vrbo.com/) by destination and travel dates and get back the same vacation-rental cards shown in its search results — property details, nightly/total pricing, guest ratings, review counts, bedrooms/bathrooms, amenities, host signals, and photos. A residential proxy is required (see Input below) since Vrbo blocks non-residential traffic outright.

## What this actor does

- **Destination search** — enter any city, region, or area and get back the listings Vrbo's own search shows for your dates and guest count
- **Full pricing breakdown** — nightly price, total stay price, strikethrough original price, discount percentage, and whether taxes/fees are already included
- **Guest and host signals** — rating, review count, Premier Host/Guest Favorite/Rare Find flags, instant-book flag, and scarcity messages like "Only 1 left"
- **Property specifics** — bedrooms, bathrooms, sleeps count, property type, neighborhood, amenities, and up to 20 photo URLs
- **Honest gaps** — fields a listing card doesn't show (for example, a distance string Vrbo omits on some cards) are left out of that record rather than filled with a placeholder

## Output per property

- `propertyId`, `name`, `url` — listing identity and link
- `price`, `totalPrice`, `originalPrice`, `currency` — nightly, total-stay, and pre-discount pricing with inferred currency
- `nights`, `totalIncludesTaxes` — stay length and whether the total already includes taxes/fees
- `discountPercent`, `distance` — discount percentage and distance-from-landmark text, when Vrbo shows them on the card
- `rating`, `reviewCount` — guest rating (0–10 scale) and number of reviews
- `bedrooms`, `bathrooms`, `sleeps` — bathrooms may be fractional (e.g. `2.5`)
- `propertyType` — e.g. Condo, Villa, House, Cabin
- `location.neighborhood` — neighborhood/area breakdown
- `latitude`, `longitude` — only populated for a subset of listings
- `images` — up to 20 photo URLs per property
- `amenities`, `propertyFeatures` — amenity badges and detected feature keywords (Pool, Wifi, Kitchen, etc.)
- `listingFlags` — e.g. Premier Host, Guest Favorite, Rare Find, Free Cancellation
- `hostIsSuperhost`, `isInstantBook` — host and booking-flow flags
- `urgencyMessage` — scarcity text such as "In high demand" or "Only 1 left"
- `cancellationPolicy` — cancellation policy label shown on the card
- `hostName` — only populated for a subset of listings
- `destination`, `checkIn`, `checkOut` — the search parameters that produced this record
- `scrapedAt` — timestamp the record was collected

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `destination` | string | `Orlando, FL` | City, region, or area to search, e.g. `Paris, France` |
| `checkIn` | string | – | Check-in date `YYYY-MM-DD`. Blank or past dates auto-roll to today + 30 days |
| `checkOut` | string | – | Check-out date `YYYY-MM-DD`. Defaults to check-in + 2 days |
| `adults` | integer | `2` | Number of adult guests (1–16); affects pricing and availability |
| `children` | integer | `0` | Number of child guests (0–20); affects pricing and availability |
| `maxItems` | integer | `3` | Maximum number of properties to return (1–500) |
| `proxyConfiguration` | object | Apify `RESIDENTIAL` proxy, country `US` | Required. Vrbo blocks non-residential traffic, so this must stay set to a US residential proxy |

### Example input

```json
{
    "destination": "Orlando, FL",
    "checkIn": "2026-06-15",
    "checkOut": "2026-06-17",
    "adults": 2,
    "children": 0,
    "maxItems": 10
}
```

### Sample output record

```json
{
    "type": "vrbo_property",
    "propertyId": "1234567",
    "name": "3BR Disney Villa with Pool",
    "url": "https://www.vrbo.com/1234567",
    "price": "$189",
    "totalPrice": "$452 for 2 nights",
    "originalPrice": "$229",
    "currency": "USD",
    "nights": 2,
    "totalIncludesTaxes": true,
    "discountPercent": 17,
    "distance": "19.93 mi from Orlando",
    "rating": "9.4",
    "reviewCount": "312",
    "bedrooms": 3,
    "bathrooms": 2.0,
    "sleeps": 8,
    "propertyType": "Villa",
    "location": {"neighborhood": "Kissimmee"},
    "images": ["https://odis.homeaway.com/odis/listing/..."],
    "amenities": ["Pool", "Free cancellation"],
    "propertyFeatures": ["Pool", "Kitchen", "Wifi"],
    "listingFlags": ["Premier Host", "Guest Favorite", "Free Cancellation"],
    "hostIsSuperhost": true,
    "isInstantBook": true,
    "urgencyMessage": "In high demand",
    "cancellationPolicy": "Free cancellation before May 30",
    "destination": "Orlando, FL",
    "checkIn": "2026-06-15",
    "checkOut": "2026-06-17",
    "scrapedAt": "2026-04-20T12:34:56Z"
}
```

`hostName`, `latitude`, and `longitude` are only populated for a subset of listings; most records omit them rather than return a guessed value.

If Vrbo returns no listings for the search (for example, a destination with no availability for the chosen dates), the dataset contains a single diagnostic item instead of a hard failure:

```json
{
    "type": "vrbo_blocked",
    "reason": "upstream_error",
    "message": "Vrbo returned no listings.",
    "destination": "...",
    "checkIn": "...",
    "checkOut": "...",
    "scrapedAt": "..."
}
```

`reason` is one of `invalid_input`, `upstream_error`, or `empty_result`.

## Use cases

- **Vacation budgeting** — compare nightly and total prices across a destination before booking
- **Property sourcing** — shortlist rentals by bedroom/bathroom count, sleeps capacity, and amenities for a group trip
- **Rate-watching** — re-run the same destination and dates over time to track how pricing and availability shift
- **Competitive research** — see how rental managers in a market price, badge, and photograph their listings
- **Travel content** — pull real listing data and photos for a destination guide or comparison article

## FAQ

**Do I need a proxy?**
Yes. Vrbo blocks requests from standard datacenter IP ranges outright, so a US residential proxy is required for this actor to return data. The `proxyConfiguration` input is pre-filled with Apify's `RESIDENTIAL` group and country `US` — leave the default as-is. Residential proxy groups require a paid Apify plan.

**Does it need login or cookies?**
No. Vrbo search results are publicly accessible without authentication.

**How fresh is the pricing?**
Pricing is rendered live by Vrbo's website at the time of the request, reflecting the same availability and totals shown to a logged-out visitor.

**Can I scrape a single property's detail page instead of a search?**
Not currently — this actor reads destination search results, not individual property detail pages.

**Can I filter by property type, price range, or amenities?**
Not as dedicated inputs today; set `adults`/`children` to influence pricing and availability, then filter the returned dataset on fields like `propertyType`, `price`, or `amenities` downstream.

**Why did my check-in/check-out dates change from what I entered?**
Vrbo rejects searches with a check-in date in the past. If `checkIn` is left blank or already in the past, the actor substitutes today + 30 days (and `checkOut` defaults to check-in + 2 days) so the search still runs.

**Is this affiliated with Vrbo or Expedia Group?**
No. This is an independent actor that reads Vrbo's publicly accessible search results; it is not operated by or affiliated with Vrbo or Expedia Group.
