# Redfin Sale, Rental & Sold Listings Scraper

Pull property listings from [Redfin.com](https://www.redfin.com) for any US location — homes currently for sale, recently sold properties, rentals, or a keyword/address search — plus full detail for a single listing URL. No login required.

## What this actor does

- Searches active for-sale listings by city, ZIP code, neighborhood, or address
- Searches homes sold within the past 180 days for the same location types
- Searches rental listings
- Runs a keyword/address search when you don't have a precise city or ZIP
- Fetches a single listing directly from its Redfin URL
- Filters by property type, price range, bedrooms, bathrooms, and square footage
- Empty fields are omitted from records

## Output per listing

- `recordType` — always `listing`
- `url` — direct Redfin listing URL
- `propertyId` — Redfin's internal property ID
- `mlsId` — MLS listing ID, when the listing carries one
- `price` — listing price in USD
- `propertyType` — `House`, `Condo`, `Townhouse`, `Multi-family`, `Land`, etc.
- `status` — `Active`, `Pending`, `Sold`, `For Rent`, etc.
- `beds`, `baths`, `sqft` — bedrooms, bathrooms, interior square footage
- `lotSize` — lot size in square feet
- `yearBuilt`
- `pricePerSqft`
- `daysOnMarket`
- `address`, `city`, `state`, `zip`
- `latitude`, `longitude`
- `hoaFee` — monthly HOA fee, when the property has one
- `listingAgent`, `brokerName`
- `imageUrls` — array of property photo URLs
- `scrapedAt` — ISO 8601 timestamp of the scrape

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `forSale` | `forSale` / `recentlySold` / `forRent` / `search` / `byUrl` |
| `location` | string | `Austin, TX` | City, ZIP code, neighborhood, or address (ignored for mode=byUrl) |
| `listingUrl` | string | – | Full Redfin listing URL (mode=byUrl) |
| `propertyType` | string | `all` | `all` / `house` / `condo` / `townhouse` / `multifamily` / `land` / `other` |
| `minPrice` | integer | – | Minimum price in USD |
| `maxPrice` | integer | – | Maximum price in USD |
| `minBeds` | integer | – | Minimum bedrooms |
| `minBaths` | integer | – | Minimum bathrooms |
| `minSqft` | integer | – | Minimum interior square footage |
| `maxSqft` | integer | – | Maximum interior square footage |
| `maxItems` | integer | `20` | Maximum records to return (1–500) |

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

### Example: recently sold condos in Brooklyn

```json
{
  "mode": "recentlySold",
  "location": "Brooklyn, NY",
  "propertyType": "condo",
  "maxItems": 30
}
```

### Example: rental listings in Miami

```json
{
  "mode": "forRent",
  "location": "Miami, FL",
  "maxItems": 25
}
```

### Example: fetch one specific listing

```json
{
  "mode": "byUrl",
  "listingUrl": "https://www.redfin.com/TX/Austin/123-Main-St-78701/home/12345678"
}
```

## Use cases

- **Home search** — filter active listings by price, size, and bedroom count across a city
- **Comparable-sales research** — pull recently sold homes to gauge a neighborhood's real selling prices
- **Rental market tracking** — monitor asking rents for a location over time
- **Lead generation** — collect listing agent and brokerage details from active listings
- **Investment screening** — scan price-per-square-foot and days-on-market across a region

## FAQ

**Does this require an account or API key?**  No — the data comes from Redfin's public listing pages, with no login required.

**Which markets are covered?**  Any US location where Redfin operates — most major metros and many smaller cities. Coverage outside the US is limited.

**How many listings can I get per run?**  Up to `maxItems`, capped at 500. Redfin's own results for a single search are limited per region, so very large pulls may need multiple runs across narrower locations.

**How fresh is the data?**  It reflects Redfin's current listing database at the time of the run, which Redfin itself updates multiple times daily.

**Can I search a specific neighborhood instead of a whole city?**  Yes — put the neighborhood in `location`, e.g. `South Congress, Austin, TX`.

**What's the difference between `search` and `forSale`?**  None currently — both resolve `location` the same way and return active listings. `search` exists as a clearer label when you're passing a loose keyword or address rather than a known city/ZIP.

**Why do some listings have no `hoaFee` or `mlsId`?**  Those only appear when Redfin's own listing data includes them — not every property has an HOA or an MLS number.

**Is this affiliated with Redfin?**  No. This actor reads Redfin's publicly available listing pages and is not affiliated with or endorsed by Redfin.
