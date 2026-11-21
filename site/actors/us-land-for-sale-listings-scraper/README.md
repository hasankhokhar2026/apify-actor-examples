# US Land for Sale Listings Scraper

Rural and recreational land listings — ranches, farms, hunting ground, timberland and waterfront parcels across the US — pulled from LandWatch.com and its Land.com network sister sites. If LandWatch blocks a request, the actor automatically retries the equivalent search on LandFlip or LotFlip so you still get a dataset instead of an empty run.

## What this actor does

- Accepts LandWatch category pages, state/county/city filter pages, or direct listing URLs as search input
- Follows listing links from search pages and visits each one for full detail
- Falls back to LandFlip (larger tracts) or LotFlip (smaller parcels) automatically when LandWatch can't be reached, mapping the same state/region filter across sites
- Derives boolean land-feature flags (waterfront, utilities, road access, surveyed, mineral rights, timber, fenced, wooded) from the listing's stated features and description text
- Omits any field the source listing didn't provide — no empty strings or nulls
- If every attempt is blocked, the run still finishes with a single sentinel record explaining why, instead of failing silently

## Output per land listing

- `type` — `land_listing` (or `land_blocked` for the no-data sentinel record)
- `id`, `url`, `title`
- `price` — asking price in USD
- `acres`
- `state`, `county`, `city`, `zip`
- `latitude`, `longitude`
- `features` — list of amenities/attributes as shown on the listing
- `images` — gallery image URLs
- `descriptionText` — full listing description
- `broker`, `brokerName`, `brokerPhone` — basic broker contact fields
- `brokerageName`, `brokeragePhone`, `brokerageWebsite` — fuller brokerage block when the source provides one
- `listingType`, `listingStatus`, `mls` — listing classification and MLS number, when disclosed
- `landType`, `propertyCategory`, `zoning`
- `taxes` — annual property tax, when stated
- `waterfront`, `hasUtilities`, `hasRoadAccess`, `surveyed`, `mineral`, `timber`, `fenced`, `wooded` — boolean flags, present only when true
- `publishedAt` — original listing date
- `source` — hostname the record was fetched from (`landwatch.com`, `landflip.com` or `lotflip.com`)
- `scrapedAt`

The `land_blocked` sentinel record (when every source is unreachable) instead has `type: "land_blocked"`, `reason`, `url`, `message`, and `scrapedAt`; it may also include `requestedUrls` and `blockedUrls`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchUrls` | array | `["https://www.landwatch.com/all-land-for-sale"]` | LandWatch category, state/county/city filter, or direct listing URLs |
| `maxItems` | integer | `3` | Maximum number of land listings to return (1–500) |
| `proxyConfiguration` | object | Apify RESIDENTIAL (US) | Required proxy configuration; LandWatch blocks non-residential IPs at the network edge |

### Example: all current land-for-sale listings

```json
{
  "searchUrls": ["https://www.landwatch.com/all-land-for-sale"],
  "maxItems": 20
}
```

### Example: Texas land listings

```json
{
  "searchUrls": ["https://www.landwatch.com/texas-land-for-sale"],
  "maxItems": 50
}
```

### Example: specific listing URLs

```json
{
  "searchUrls": [
    "https://www.landwatch.com/property/40-acres-in-llano-county-texas/12345678"
  ],
  "maxItems": 1
}
```

## Use cases

- **Land investors** scan current acreage, price-per-acre and broker contact across a state or county
- **Hunting and recreational buyers** filter by waterfront, road access or timber flags to shortlist parcels
- **Rural brokers** monitor competing listings and pricing in their market
- **Agricultural researchers** track farmland and ranch listing volume and pricing trends by region
- **Market comparison tools** merge LandWatch, LandFlip and LotFlip coverage into one dataset

## FAQ

**Is this affiliated with LandWatch?**
No. This is an independent actor that reads publicly available listing pages from LandWatch and the Land.com network; it has no affiliation with LandWatch or Land.com.

**Why does the actor sometimes use LandFlip or LotFlip instead of LandWatch?**
LandWatch occasionally blocks automated requests. When that happens, the actor maps your search to the equivalent LandFlip (larger tracts) or LotFlip (smaller parcels) search instead, so the run still returns data. The `source` field shows which site a given record came from.

**Why do I get a single `land_blocked` record instead of listings?**
That sentinel only appears when every source — LandWatch, LandFlip and LotFlip — was unreachable for your search during the run. It lets the run finish cleanly rather than failing with no output.

**Do I need to configure the proxy myself?**
The required proxy configuration is pre-set to Apify's residential US pool, which LandWatch requires to avoid being blocked at the network edge; you don't need to change it.

**Why are feature flags like `waterfront` or `timber` sometimes absent instead of `false`?**
Flags are only included when the listing's features or description actually indicate that attribute is present — absence means "not stated," not necessarily "false."

**Can I pass a direct listing URL instead of a search page?**
Yes — `searchUrls` accepts direct LandWatch listing URLs alongside category and location filter pages.
