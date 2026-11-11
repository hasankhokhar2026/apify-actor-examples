# Redfin Sale, Rental & Sold Listings Scraper

Collect property listings from [Redfin.com](https://www.redfin.com) for any supported US location — homes for sale, recently sold homes, rentals, keyword matches, or a single listing from its Redfin URL. No login, API key, or proxy setup is required.

## What this actor does

- Searches active for-sale listings by city, ZIP, neighborhood, US state, Redfin search URL, or explicit region ID
- Searches recently sold homes with a configurable 30-day to 5-year window
- Searches rental listings, including rent ranges, unit ranges, and availability
- Filters listings by keyword across address, description, tags, key facts, subdivision, and building name
- Fetches one specific listing from its Redfin URL
- Sorts by recommended, newest, oldest, price ascending, or price descending
- Pages through Redfin results for large pulls (up to 20,000 records)
- Filters by property type, price, bedrooms, bathrooms, and square footage
- Verifies that returned homes actually belong to the requested location, so a bad region ID cannot silently return another city
- Optionally enriches each listing with price history, tax history, public records, and amenities
- Emits clean records with empty fields omitted

## Location input

`location` accepts any of these forms:

| Form | Example |
|---|---|
| City and state | `Austin, TX` |
| US state | `Texas`, `TX` |
| ZIP code | `90210`, `10001`, `78701` |
| Neighborhood | `South Congress, Austin, TX` |
| Redfin search URL | `https://www.redfin.com/city/30818/TX/Austin` |
| Region token | `6_30818` (`<region_type>_<region_id>`) |

Redfin's own autocomplete is tried first. When it is unavailable from the current network, the actor falls back to verified region IDs for major cities, common ZIPs, neighborhoods, and all 50 states plus DC. A city that is not in the offline seed is handled in two steps: the actor scans the state-level GIS region and keeps only records whose city matches, and reports the fallback in the run status. Very large states can return a Redfin GIS service timeout at state level; in that case the status message recommends a ZIP, city URL, or region ID. This is a state-level fallback, not a fix for Redfin autocomplete.

## Output per listing

Core fields:

- `recordType` — always `listing`
- `url` — direct Redfin listing URL
- `propertyId` — Redfin's internal property ID
- `listingId` — Redfin listing ID
- `mlsId` — MLS number, when the listing carries one
- `price` — sale price, or starting monthly rent in `forRent` mode
- `listingType` — `sale`, `sold`, or `rent`
- `status` — `Active`, `Pending`, `Sold`, `For Rent`, etc.
- `propertyType` — `House`, `Condo`, `Townhouse`, `Multi-family`, `Land`, etc.
- `beds`, `baths`, `fullBaths`, `partialBaths` — bedrooms and bathroom counts
- `sqft` — interior square footage
- `lotSize` — lot size in square feet
- `yearBuilt`, `yearRenovated`, `stories`
- `pricePerSqft` — for sale and sold listings
- `daysOnMarket`, `timeOnRedfinDays`, `originalTimeOnRedfinDays`
- `address`, `unit`, `city`, `state`, `zip`
- `latitude`, `longitude`
- `subdivision`
- `hoaFee` — monthly HOA fee, when the property has one
- `listingAgent`, `listingAgentId`, `brokerName`, `listingCoBroker`
- `description`, `listingTags`, `keyFacts`, `badges`
- `hasVirtualTour`, `hasVideoTour`, `has3DTour`, `scanUrl`, `posterFrameUrl`
- `isNewConstruction`, `isHot`, `hotnessMessage`, `hotnessAction`, `hasInsight`
- `poolTypeCode` — Redfin's raw `skPoolType` code; Redfin does not document the label mapping
- `openHouseStart`, `openHouseEnd`, `openHouseEventName`
- `imageUrls` — up to 10 property photo URLs
- `photoCount`
- `garageSpaces`, `parkingSpaces`
- `scrapedAt` — ISO 8601 timestamp of the scrape

Sold listings also carry:

- `soldPrice` — final sale price
- `soldDate` — sale date in ISO format
- `sellingAgent`, `sellingAgentId`, `sellingBroker` — when Redfin exposes them

Rental listings also carry:

- `rentPrice` — starting monthly rent
- `rentPriceMin`, `rentPriceMax`
- `bedsMin`, `bedsMax`, `bathsMin`, `bathsMax`, `sqftMin`, `sqftMax`
- `propertyName` — building or community name
- `availableUnits` — number of available units
- `lastUpdated` — feed update timestamp

When `includeDetails` is enabled, each listing also carries:

- `priceHistory` — dated price events (listed, pending, contingent, sold) with source and MLS status
- `taxHistory` — yearly tax rows with taxes due, land value, and improvement value
- `taxAnnualAmount`, `taxYear` — latest tax row
- `apn`, `county`, `countyUrl` — public-record identifiers
- `publicRecordUpdatedDate`
- `amenities` — grouped public-record and listing amenities such as bathroom counts, heating, fireplace, parking, lot information, and subdivision
- `priceEstimateUrl` — Redfin's estimate page for the property

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `forSale` | `forSale` / `recentlySold` / `forRent` / `search` / `byUrl` |
| `location` | string | `Austin, TX` | City/state, US state, ZIP, neighborhood, Redfin URL, or region token (ignored for mode=byUrl) |
| `listingUrl` | string | – | Full Redfin listing URL (mode=byUrl) |
| `keyword` | string | – | Case-insensitive keyword filter; required in `search` mode |
| `propertyType` | string | `all` | `all` / `house` / `condo` / `townhouse` / `multifamily` / `land` / `other` |
| `minPrice` | integer | – | Minimum sale price, or minimum monthly rent |
| `maxPrice` | integer | – | Maximum sale price, or maximum monthly rent |
| `minBeds` | integer | – | Minimum bedrooms |
| `minBaths` | integer | – | Minimum bathrooms |
| `minSqft` | integer | – | Minimum interior square footage |
| `maxSqft` | integer | – | Maximum interior square footage |
| `soldWithinDays` | integer | `180` | Sold window in `recentlySold` mode: 30 / 90 / 180 / 365 / 1095 / 1825 days |
| `sort` | string | `recommended` | `recommended` / `newest` / `oldest` / `priceLowToHigh` / `priceHighToLow` |
| `maxItems` | integer | `20` | Maximum records to return (1–20,000) |
| `includeDetails` | boolean | `false` | Add price history, tax history, public records, and amenities |

### Example: 3-bed homes under $600K in Austin

```json
{
  "mode": "forSale",
  "location": "Austin, TX",
  "minBeds": 3,
  "maxPrice": 600000,
  "maxItems": 50
}
```

### Example: homes sold in the last 90 days in 90210

```json
{
  "mode": "recentlySold",
  "location": "90210",
  "soldWithinDays": 90,
  "maxItems": 30
}
```

### Example: rentals in South Congress

```json
{
  "mode": "forRent",
  "location": "South Congress, Austin, TX",
  "maxItems": 25
}
```

### Example: keyword search inside a city

```json
{
  "mode": "search",
  "location": "Austin, TX",
  "keyword": "pool",
  "sort": "priceHighToLow",
  "maxItems": 20
}
```

### Example: fetch one listing with detail enrichment

```json
{
  "mode": "byUrl",
  "listingUrl": "https://www.redfin.com/TX/Austin/11307-Jack-Rabbit-Trl-78750/home/32784952",
  "includeDetails": true
}
```

## How location resolution works

1. **Direct request** — Redfin's location autocomplete, with no proxy.
2. **Automatic connection fallback** — if the direct request is blocked, the actor retries through Apify's datacenter proxy pool. No user proxy configuration is needed.
3. **Deterministic fallback** — if autocomplete is unavailable from both paths, the actor parses the ZIP, city/state, neighborhood, state, Redfin URL, or region ID from your input and resolves a verified Redfin region.
4. **State-level fallback** — an unknown city with a known state uses the verified state region and keeps only records whose city matches. Large states can return a Redfin GIS timeout at state scope; the run status reports it.
5. **Location verification** — every returned home is checked against the requested city/state or ZIP. Homes from another area are dropped and reported in the run status instead of being emitted as wrong-city data.

## Use cases

- **Home search** — filter active listings by price, size, and bedroom count across a city
- **Comparable sales** — pull recently sold homes with sold price and sold date
- **Rental market tracking** — monitor asking rents and available units by building
- **Lead generation** — collect listing agents, brokerages, and property details
- **Investment screening** — scan price-per-square-foot, days on market, lot size, tax history, and price history

## FAQ

**Does this require an account or API key?** No. It reads Redfin's public listing data with no login. Connections are handled automatically.

**Which locations are supported?** Any US city, ZIP, neighborhood, or state that Redfin covers. Major metros, common ZIPs, neighborhoods, and states also work when Redfin's autocomplete is blocked. For a city outside the offline seed, the actor scans the state and keeps matching-city records; large states may return a source timeout. A Redfin URL or region ID always avoids that lookup.

**How does `search` differ from `forSale`?** `search` requires a `keyword` and keeps only active listings whose address, description, tags, key facts, subdivision, or building name contains that keyword. `forSale` returns every active listing in the location.

**What does `price` mean for rentals?** It is the starting monthly rent for that building. The full range is in `rentPriceMin` / `rentPriceMax`, and unit-size ranges are in the `*Min` / `*Max` fields.

**Are sold prices the same as list prices?** No. `soldPrice` and `soldDate` are populated only for listings Redfin reports as sold. Active listings never carry a sold price.

**Why are some fields missing?** Redfin does not expose every detail for every property. Empty fields are omitted, not filled with placeholders.

**Can I get tax history, price history, and amenities?** Yes. Set `includeDetails: true` to call Redfin's cookieless below-the-fold detail API for each emitted listing. This adds one request per listing and returns price history, tax history, public-record fields, and grouped amenities. School ratings, climate scores, and buyer-agent contact details are not part of that payload and are not included.

**How many listings can I get per run?** Up to 20,000, which is a self-imposed cap. Redfin returned homes at a start offset of 19,950 in verification; deeper offsets in very large regions can return an empty page. The actor de-duplicates by property ID.

**Is this affiliated with Redfin?** No. This actor reads publicly available Redfin listing data and is not affiliated with or endorsed by Redfin.

## Verification status

The local build was verified with `pytest` and local actor runs (sale, sold, rent, ZIP, neighborhood, state fallback, sort, keyword, detail enrichment, and by-URL). Cloud runs from an earlier build are recorded in `docs/FINAL-AUDIT.md`; this build has not been pushed to the test slug, and production was not promoted. Redfin HTML property pages return a 202 AWS WAF challenge to cookieless clients, while the GIS, rental, below-the-fold detail, region, sitemap, and CDN media endpoints used by this actor return 200.
