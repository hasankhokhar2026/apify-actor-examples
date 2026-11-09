# Realtor.com Property & Agent Scraper

Turn Realtor.com into structured data. Search active, rental, sold, pending, contingent, coming-soon, off-market or new-construction listings by city, ZIP, street address, map radius or GeoJSON polygon; apply real filters; and pull the full property record â€” MLS number, HOA, mortgage estimate, assigned schools, open houses, tours, photo tags, tax and price history, risk scores and agent contacts. Switch one field to collect real-estate agent directory records, including profile phone numbers.

No account, cookies, API key or proxy setup is required.

## What this actor does

- **Eight listing statuses** â€” `BUY` (for sale), `RENT`, `SOLD`, `PENDING`, `CONTINGENT`, `COMING_SOON`, `OFF_MARKET` and `READY_TO_BUILD`.
- **Five ways to target** â€” free-form location (city, ZIP, neighborhood, county), street address, a map point with a mile radius, a GeoJSON polygon, or Realtor.com URLs.
- **Real server-side filters** â€” beds, baths, price, living area, lot size, year built, property type, keywords, photos-only, coming-soon, open-house dates and listing/sold dates.
- **Full detail records** â€” one detail lookup per property adds the marketing description, HOA fee, mortgage estimate, assigned and nearby schools, open houses, virtual tours, photo tags, categorized features, tax/price history, parcel ids and expanded agent contacts.
- **Agent directory** â€” search agents by name, city/state or ZIP; returns name, office, profile phones, license, bio, languages, designations, avatar and public profile URL.
- **Sorted and paginated deeply** â€” newest, price, size or bedroom ordering, up to 10,000 records per run (the source's addressable search window).
- **Honest output** â€” a field the source does not publish for a listing is omitted, never guessed or filled with a sentinel. Zero placeholder prices from public records are removed rather than emitted.

## Listing statuses

| Mode | What it returns |
|---|---|
| `BUY` | Active for-sale listings |
| `RENT` | Active rental listings |
| `SOLD` | Recently sold properties with sale date and, where published, sale price |
| `PENDING` | For-sale listings with an accepted offer |
| `CONTINGENT` | For-sale listings still subject to a contingency |
| `COMING_SOON` | Not-yet-active listings announced ahead of the market |
| `OFF_MARKET` | Delisted / off-market listings |
| `READY_TO_BUILD` | New-construction and build-ready listings |

`PENDING`, `CONTINGENT` and `COMING_SOON` come back with `status: for_sale` and the matching `flags.isPending` / `flags.isContingent` / `flags.isComingSoon` set, because that is how the source models them. The same coming-soon filter is available as `comingSoonOnly` on the other for-sale modes.

## Filters

| Filter | Applies to |
|---|---|
| `bedsMin` / `bedsMax` | Bedroom range |
| `bathsMin` / `bathsMax` | Bathroom range |
| `priceMin` / `priceMax` | List price range (USD) |
| `sqftMin` / `sqftMax` | Living area range |
| `lotSqftMin` / `lotSqftMax` | Lot size range |
| `yearBuiltMin` / `yearBuiltMax` | Construction year range |
| `propertyTypes` | One or more of Realtor.com's 20 property types |
| `keywords` | Free-text terms such as `pool`, `waterfront`, `garage` |
| `hasPhotos` | Exclude listings without photos |
| `comingSoonOnly` | Only coming-soon listings in the for-sale modes |
| `openHouseFrom` / `openHouseTo` | Listings with an open house in the date window |
| `listedSince` | Listings added on or after a date (delta monitoring) |
| `soldSince` | In `SOLD` mode, sales on or after a date |
| `latitude` + `longitude` + `radiusMiles` | Radius search around a map point |
| `boundary` | GeoJSON Polygon search area (longitude/latitude rings) |
| `sortBy` | Relevance, newest, price low/high, largest living area or most bedrooms |

Filters are sent to Realtor.com and then verified on every returned record, so a filter cannot silently pass through unfiltered rows.

## Output per property

Identity
- `recordType` â€” always `property`
- `url`, `id`, `listingId`, `permalink`
- `mlsId`, `mlsSource`, `mlsType`, `mlsStatus`
- `parcelId` plus `taxRecord.clId`, `.publicRecordId`, `.lastUpdateDate`, `.apn`, `.taxParcelId`
- `status`

Pricing
- `listPrice`, `listPriceMin`, `listPriceMax` (range-priced new builds have no single price)
- `pricePerSqft` â€” from the source, or computed from list price and living area
- `priceReduced` â€” reduction amount
- `lastSoldPrice`, `soldOn`
- `estimatedValue`, and `estimates[]` with `.estimate`, `.estimateLow`, `.estimateHigh`, `.date`, `.source`, `.sourceType` (multiple valuation providers when available)
- `mortgage.monthlyPayment`, `.downPayment`, `.loanAmount`
- `hoaFee`

Property facts
- `beds`, `baths`, `bathsFull`, `bathsHalf`
- `sqft`, `lotSqft`, `yearBuilt`, `yearRenovated`
- `garage`, `garageType`, `stories`, `rooms`, `units`
- `type`, `subType`, `name` (community/building name)
- `listDate`, `pendingDate`, `lastStatusChangeDate`, `lastUpdateDate`
- `daysOnMarket` â€” source value, or derived from the list date (and the sale date for sold records)

Location
- `address.street`, `.city`, `.state`, `.postalCode`, `.county`, `.countyFips`, `.neighborhoods`
- `coordinates.lat`, `.lng`

Media
- `photos` â€” photo URLs
- `photoTags` â€” `[{ url, tags: ["kitchen", "exterior", â€¦] }]`
- `virtualTours` â€” `[{ href, type }]`

Flags
- `flags.isNewListing`, `.isPriceReduced`, `.isForeclosure`, `.isNewConstruction`, `.isPending`, `.isContingent`, `.isComingSoon`

Detail sections (when `scrapeDetails` is on and the source publishes them)
- `text` â€” full marketing description
- `features` â€” cooling, heating, exterior, roofing, construction, fireplace, pool, zoning, styles, garage type
- `tags` â€” source amenity tags
- `details` â€” categorized feature lists, `[{ category, parentCategory, items }]`
- `petPolicy`, `unitDetails`
- `nearbySchools` â€” name, rating, distance, grades, type, levels, student count, `assigned`
- `assignedSchools` â€” the assigned public schools for the address
- `openHouses` â€” start, end, description, methods, time zone, DST
- `local.flood`, `.noise`, `.wildfire` â€” risk scores, severity, FEMA zone, noise categories
- `history` â€” listing/sale events with date, event, price and price per sqft; zero placeholder prices are omitted per row
- `taxHistory` â€” year, tax, assessed and market values (total/land/building); zero placeholders are omitted
- `agents` â€” name, email, phone, office, office phone, office email, type, license, NRDS id, fulfillment id, broker
- `branding`, `products`, `leadAttributes`, `otherListings`

Every record ends with `scrapedAt` (ISO timestamp).

## Output per agent

- `recordType` â€” always `agent`
- `agentId`, `fulfillmentId`
- `name`, `profileUrl`, `website`
- `officeName`, `licenseNumber`
- `phone`, `phones[]` â€” profile phone numbers with their `type` (when Realtor.com publishes them and `scrapeDetails` is on)
- `officePhone`, `officePhones[]` â€” office phone numbers from the same profile
- `bio`, `languages`, `designations`
- `avatarUrl`
- `searchLocation` â€” the agent-name/city/ZIP query that produced the record
- `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | Select | `BUY` | Listing status: `BUY`, `RENT`, `SOLD`, `PENDING`, `CONTINGENT`, `OFF_MARKET`, `READY_TO_BUILD` |
| `recordType` | Select | `PROPERTIES` | Collect property listings or agent directory records |
| `search` | String | - | City/state, ZIP, neighborhood, county or street address. In agent mode: city/state or ZIP |
| `agentName` | String | - | Agent or team name (agent mode) |
| `startUrls` | Array | `[]` | Realtor.com detail or search-result URLs |
| `maxItems` | Integer | `100` | Maximum records to emit (1-10,000) |
| `endPage` | Integer | `50` | Maximum result pages per search (200 properties per page; 50 reaches 10,000) |
| `scrapeDetails` | Boolean | `true` | Fetch each property's full detail record; in agent mode, fetch profile phones |
| `bedsMin`, `bedsMax` | Integer | - | Bedroom range |
| `bathsMin`, `bathsMax` | Integer | - | Bathroom range |
| `priceMin`, `priceMax` | Integer | - | List price range |
| `sqftMin`, `sqftMax` | Integer | - | Living area range |
| `lotSqftMin`, `lotSqftMax` | Integer | - | Lot size range |
| `yearBuiltMin`, `yearBuiltMax` | Integer | - | Construction year range |
| `propertyTypes` | Multi-select | `[]` | One or more property types |
| `keywords` | String list | `[]` | Free-text keywords |
| `hasPhotos` | Boolean | `false` | Only listings with photos |
| `comingSoonOnly` | Boolean | `false` | Only coming-soon listings in for-sale modes |
| `sortBy` | Select | `relevant` | `relevant`, `newest`, `price_low`, `price_high`, `sqft_high`, `beds_high` |
| `listedSince` | Date | - | Listings added on/after `YYYY-MM-DD` |
| `soldSince` | Date | - | Sales on/after `YYYY-MM-DD` (`SOLD` mode) |
| `openHouseFrom`, `openHouseTo` | Date | - | Open-house date window |
| `latitude`, `longitude` | Number | - | Map point for a radius search |
| `radiusMiles` | Integer | - | Radius around the map point (1-100 miles) |
| `boundary` | Object | - | GeoJSON Polygon: `{"type":"Polygon","coordinates":[[[lon,lat],...]]}` |

At least one of `search`, `startUrls`, a complete latitude/longitude/radius point, or a `boundary` polygon is required for property mode. Agent mode needs `agentName` or `search`.

### Example: active listings in a city

```json
{
    "mode": "BUY",
    "search": "Houston, TX",
    "maxItems": 100,
    "scrapeDetails": true
}
```

### Example: comparable sales

```json
{
    "mode": "SOLD",
    "search": "Denver, CO",
    "soldSince": "2026-01-01",
    "maxItems": 50,
    "scrapeDetails": true
}
```

### Example: filtered search with open houses

```json
{
    "mode": "BUY",
    "search": "Austin, TX",
    "bedsMin": 3,
    "priceMax": 750000,
    "propertyTypes": ["single_family"],
    "openHouseFrom": "2026-11-01",
    "openHouseTo": "2026-11-30",
    "sortBy": "newest",
    "maxItems": 25
}
```

### Example: radius search around coordinates

```json
{
    "mode": "BUY",
    "latitude": 29.76,
    "longitude": -95.36,
    "radiusMiles": 5,
    "sqftMin": 1500,
    "maxItems": 50
}
```

### Example: coming-soon listings

```json
{
    "mode": "COMING_SOON",
    "search": "Atlanta, GA",
    "maxItems": 50,
    "scrapeDetails": false
}
```

`comingSoonOnly: true` applies the same filter inside `BUY`, `PENDING` or `CONTINGENT` mode.

### Example: polygon search area

```json
{
    "mode": "BUY",
    "boundary": {
        "type": "Polygon",
        "coordinates": [
            [[-95.6, 29.6], [-95.0, 29.6], [-95.0, 30.1], [-95.6, 30.1], [-95.6, 29.6]]
        ]
    },
    "maxItems": 50,
    "scrapeDetails": false
}
```

Rings may be open; the actor closes them automatically. Coordinates are `[longitude, latitude]`.

### Example: agent directory by city or ZIP

```json
{
    "recordType": "AGENTS",
    "search": "Houston, TX",
    "maxItems": 100
}
```

```json
{
    "recordType": "AGENTS",
    "agentName": "Pedro Casanova",
    "maxItems": 25
}
```

### Example: direct property URLs

```json
{
    "startUrls": [
        { "url": "https://www.realtor.com/realestateandhomes-detail/1802-Hamlin-Valley-Dr_Houston_TX_77090_M80144-71467" }
    ],
    "scrapeDetails": true
}
```

Search-result URLs work too; their location, status and page are reused:

```json
{
    "startUrls": [
        { "url": "https://www.realtor.com/realestateandhomes-search/Houston_TX/pg-2" }
    ],
    "maxItems": 20
}
```

## Use cases

- **Comparable-sales research** â€” pull `SOLD` records by ZIP or neighborhood with sale dates, assessed values and price per sqft.
- **Buyer shortlists** â€” check flood, wildfire and noise scores, assigned schools, HOA and monthly mortgage estimates before a showing.
- **Open-house planning** â€” filter by open-house dates and get start/end times, methods and time zone in one dataset.
- **Investor screening** â€” compare list price, tax history and automated valuations to spot under- or over-assessed properties.
- **Rental tracking** â€” run `RENT` on a schedule and use `listedSince` or `sortBy: newest` for deltas.
- **Agent and brokerage mapping** â€” collect agent names, offices, licenses, languages and profile links for a market.
- **Listing monitoring** â€” schedule a run with `listedSince` to pick up new inventory without re-scraping everything.

## Data source and reliability

The actor reads Realtor.com's public web endpoints. It does not log in, and it does not need cookies, browser automation or a paid proxy. Detail enrichment costs one request per property (and one per agent in agent mode); turn `scrapeDetails` off when search-level fields are enough.

## Limits and FAQ

**How many results can one search return?**
Up to 10,000 per run, which is Realtor.com's own addressable search window (200 per request, offset up to 10,000). The result total can be larger, but only the first 10,000 rows of one search are reachable. To go deeper, split the market with filters (price bands, property type, ZIP codes or smaller map radii) and run each slice.

**Do I need a Realtor.com account or API key?**
No. Both property and agent searches use public data and run without credentials.

**Why is `lastSoldPrice` empty for some sold properties?**
Some US states do not disclose sale prices. The sale date and history events are still returned when published; price fields are omitted rather than guessed or filled with the `0` placeholder that public records sometimes carry. The same rule applies inside `history` and `taxHistory` rows.

**Why are some detail fields missing on a property?**
Sections such as HOA, tax history, assigned schools, open houses, tours, risk scores and mortgage estimates exist only when Realtor.com publishes them for that listing. New construction and off-market properties often have fewer sections.

**What is the difference between `PENDING` and `CONTINGENT`?**
Both are for-sale listings under contract; the source marks them with separate flags, which the actor filters on and exposes as `flags.isPending` and `flags.isContingent`.

**Can I scrape coming-soon listings?**
Yes. Use `mode: COMING_SOON` or set `comingSoonOnly: true` in a for-sale mode. The actor applies Realtor.com's coming-soon filter, verifies `flags.isComingSoon` on each record and exposes the flag in the output.

**How is `daysOnMarket` calculated?**
It uses the source value when present. Otherwise it is the number of days between the list date and today, or between the list date and the sale date for sold records. It is always non-negative.

**Why did I get fewer records than `maxItems`?**
The location or filter combination may have fewer matches, the result set may have hit the source's 10,000-listing ceiling, or the pages ran out. Narrow or broaden the search accordingly.

**Can I mix a location search and direct URLs?**
Yes. Direct detail URLs are resolved individually and de-duplicated against the search results by property id.

**Does agent mode return phone numbers and email addresses?**
Profile phone numbers are returned when Realtor.com publishes them and `scrapeDetails` is on, together with the office phone when available. Agent emails are not exposed by the public agent profile endpoint, so they are never fabricated; property advertiser emails are returned when the listing publishes them. Agent records always include a public profile URL so missing contact details can be checked at the source.

**Is this affiliated with Realtor.com?**
No. It is an independent tool that reads publicly available Realtor.com pages and endpoints; it is not operated or endorsed by Realtor.com.
