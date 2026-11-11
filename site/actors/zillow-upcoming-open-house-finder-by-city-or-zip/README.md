# Zillow Upcoming Open House Finder by City or ZIP

Find upcoming open houses on Zillow for a city, ZIP code, or neighborhood and get one row per scheduled showing. Each row carries the showing date, start and end time, showing type and status together with the property's price, beds, baths, square footage, lot, year built, tax value, HOA, agent/broker, MLS, photos, and a direct link to the listing.

The actor is built for the real buyer question: **what can I visit this weekend, and when?** Pick a date preset such as This weekend or Next weekend, add price/bed/bath/home-type limits, and the dataset becomes a viewing itinerary you can sort by start time.

## What it returns

- One dataset row per open-house showing, not one row per property
- Exact showing `eventDate`, `startDateTime`, `endDateTime`, `openHouseType`, and `openHouseStatus`
- Listing facts: address, city, state, ZIP, latitude/longitude, price, Zestimate, beds, baths, sqft, lot area, year built, home type, status, days on Zillow, tax-assessed value, HOA fee, price per sqft
- Listing contact and MLS data from the property page: broker, agent, MLS ID/source, description, photo URLs
- `nextOpenHouse` — the earliest matching showing for that property, repeated on each of its rows
- `recordType: "open_house"`, `sourceUrl`, `scrapedAt`, `detailStatus`, and `dataSource` for traceability

Fields that Zillow does not publish or that a detail page did not return are omitted rather than emitted as null or blank. Agent/broker phone numbers and any published agent email are only included when **Include agent contact details** is enabled.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `locations` | array | `["Austin, TX"]` | City (`Austin, TX`), ZIP (`78704`), neighborhood (`Hyde Park, Austin, TX`), borough (`Brooklyn, NY`), or county (`Travis County, TX`). Each is resolved through Zillow's free autocomplete. |
| `startUrls` | array | – | Zillow search or open-house URLs. Legacy open-house paths are converted to the filtered path and the open-house filter is applied automatically. |
| `minPrice` / `maxPrice` | integer | – | Price bounds in dollars. |
| `bedsMin` / `bedsMax` | number | – | Bedroom bounds. |
| `bathsMin` | number | – | Minimum bathrooms; decimals allowed. |
| `homeTypes` | array | all | Houses, condos, townhouses, multi-family, apartments, manufactured homes, or lots/land. |
| `dateFilter` | enum | `any` | `any`, `today`, `this_weekend`, `next_weekend`, `next_7_days`, `next_30_days`, or `custom`. |
| `dateFrom` / `dateTo` | string | – | `YYYY-MM-DD` bounds used with `custom` (or alone when no preset is selected). |
| `includeDetails` | boolean | `true` | Visit each property page for agent/broker, photos, description, year built, lot, HOA, and MLS. Search rows still return if a detail page fails. |
| `includeAgentContact` | boolean | `false` | Include agent/broker phone and any published agent email. |
| `maxItems` | integer | `100` | Maximum showing rows to return, 1–500. |
| `proxyConfiguration` | object | – | Optional Apify Proxy override. Leave empty and the actor picks a working route automatically. |

At least one location or start URL is required.

### Example: one showing in Austin (default prefill)

```json
{
    "locations": ["Austin, TX"],
    "maxItems": 1,
    "includeDetails": true
}
```

### Example: this weekend, three bedrooms or more, under $900k

```json
{
    "locations": ["Austin, TX", "78704"],
    "dateFilter": "this_weekend",
    "bedsMin": 3,
    "maxPrice": 900000,
    "includeDetails": true,
    "maxItems": 100
}
```

### Example: a custom two-day viewing window

```json
{
    "locations": ["78704"],
    "dateFilter": "custom",
    "dateFrom": "2026-10-25",
    "dateTo": "2026-10-26",
    "homeTypes": ["singleFamily", "townhouse"],
    "maxItems": 50
}
```

### Example: start from a Zillow search URL

```json
{
    "startUrls": [
        "https://www.zillow.com/austin-tx/open-houses/"
    ],
    "maxItems": 100
}
```

## How it works

1. Locations are resolved with Zillow's free autocomplete endpoint, then searched with the server-side open-house filter (`isOpenHousesOnly`) on Zillow's filtered open-house path.
2. Listing cards come from the page's `__NEXT_DATA__` payload, including all showing timestamps Zillow publishes for each property.
3. With details on, each property's page is opened once to add agent/broker, MLS, photos, description, year built, lot, HOA, and any additional showing data.
4. Date presets and custom ranges are applied to the exact showing dates after collection. Deduplication is global across pages, locations, and URLs, keyed by property ID plus showing datetime.
5. If a listing page is blocked but detail pages are not, list-level rows still return with `detailStatus: "failed"`. If Zillow blocks every route, the run fails with an explicit message instead of returning a misleading empty dataset.

## Use cases

- **Home buyers** — turn a weekend into a route with exact start times and addresses
- **Buyer's agents** — show clients what is open nearby and when
- **Listing agents** — monitor competing open houses and pricing in a farm area
- **Market researchers** — measure open-house frequency and price bands by ZIP
- **Investors** — find actively marketed properties with upcoming showings

## FAQ

**Does this need a Zillow account or login?**
No. It reads public Zillow search and property pages. No cookies, logins, or API keys are required.

**Is this one row per property or per showing?**
Per showing. A property with two open houses on the same weekend produces two rows. `nextOpenHouse` identifies its earliest matching showing.

**What timezone are the times in?**
Zillow publishes showing times as local wall-clock time without an offset, and the actor preserves them that way. Treat `startDateTime` as the property's local time and confirm with the listing agent.

**What happens if Zillow blocks the run?**
The actor tries direct requests first and automatically routes through Apify Proxy when it sees a real block. If every route is blocked, the run fails with a clear message — it never reports zero results as if the market were empty.

**What does `detailStatus` mean?**
`ok` means the property page was read; `failed` means it was blocked or unparseable but the row still has search-level data; `skipped` means details were off or the fetch cap was reached; `degraded` means the Jina Reader fallback supplied listing-card data only.

**Why are `zestimate`, `yearBuilt`, or `taxAssessedValue` missing on some rows?**
Zillow does not publish all fields for every listing. Zestimate in particular is absent on many cards. Detail enrichment fills year built, lot, HOA, and MLS when available.

**Why do some rows have no agent phone or email?**
Contact details are opt-in through **Include agent contact details** and only appear when Zillow publishes them on the property page. The actor does not guess or enrich contacts from third-party databases.

**How many results can I get?**
`maxItems` caps the run at 500 showing rows. Zillow also caps a search at about 20 pages. In dense metros, split the search by ZIP code, price band, or home type.

**Which URL formats work in `startUrls`?**
Standard Zillow search URLs and open-house URLs. Legacy `/city/open-houses/` links are normalized to the filtered open-house path. Individual `/homedetails/` property URLs are not supported.

**Is this affiliated with Zillow?**
No. This is an independent actor that reads publicly available Zillow pages and is not operated or endorsed by Zillow. Open-house times originate from MLS feeds and can change; confirm with the listing agent before visiting.
