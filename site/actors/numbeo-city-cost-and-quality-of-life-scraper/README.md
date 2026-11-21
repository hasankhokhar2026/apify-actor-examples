# Numbeo City Cost and Quality of Life Scraper

Numbeo is a crowd-sourced database covering cost of living, quality of life, crime, health care, pollution, traffic and property prices for thousands of cities worldwide. This actor pulls any one of those Numbeo pages for a city (or a pair of cities, or the annual rankings table) and returns the indices and itemized price rows as structured JSON instead of a webpage you'd have to read by hand.

## What this actor does

- Covers nine Numbeo page types in one actor: cost of living, cost-of-living comparison between two cities, quality of life, crime, health care, pollution, traffic, property investment/rents, and the annual top-cities rankings
- Builds the right Numbeo URL from a plain-English city name and automatically tries alternative slug forms (e.g. appending a US state) if the first guess doesn't resolve
- Accepts a batch of cities, or a list of direct Numbeo URLs that it auto-routes to the matching parser
- Captures each item's contributor-supplied price range alongside the point estimate, when Numbeo shows one
- Omits any field Numbeo didn't display on that page — no empty strings or nulls in the output

## Output per record

Fields vary by mode; only fields the page actually shows are included.

- `city` — city name as shown in the page title
- `sourceUrl` — the Numbeo URL the record came from
- `indices` — map of index name to value (e.g. "Cost of Living Index", "Safety Index") — present on `costOfLiving`, `qualityOfLife`, `crime`, `healthCare`, `pollution`, `traffic`, `propertyInvestment`
- `qualityOfLifeIndex`, `components` — headline index value and the detailed index/ratio breakdown rows — `qualityOfLife` only
- `prices` — list of `{item, price, currency?, rangeLow?, rangeHigh?}` rows — `costOfLiving` only
- `rents` — the same `{item, price, currency?, rangeLow?, rangeHigh?}` row shape, for rental/property prices — `propertyInvestment` only
- `sections` — list of `{rows: [{label, value, ratingLabel?}]}` sub-tables (e.g. "Level of crime", "Safety walking alone at night") — `crime`, `healthCare`, `pollution`, `traffic`
- `whoPollutionData` — WHO PM10/PM2.5 reference values, map of label to number — `pollution` only
- `nearbyCities` — list of `{city, distanceKm}` for nearby cities Numbeo links from the page
- `comparison` — list of `{item, city1Price?, city1Currency?, city2Price?, city2Currency?, differencePercent?}` rows — `costOfLivingComparison`
- `title` — page heading text — `costOfLivingComparison`
- `rank`, `city`, plus whichever index columns the rankings table has that year (e.g. `costOfLivingIndex`, `rentIndex`, `groceriesIndex`, `localPurchasingPowerIndex`) — `topCities`
- `recordType: "error"` and an error message — only emitted if a requested city/URL couldn't be resolved at all

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `costOfLiving` | `costOfLiving`, `costOfLivingComparison`, `qualityOfLife`, `crime`, `healthCare`, `pollution`, `traffic`, `propertyInvestment`, `topCities` or `byUrl` |
| `city` | string | `New York` | City name in plain English, used by all single-city modes |
| `cities` | array | `[]` | Additional city names to scrape in the same run (combined with `city`) |
| `country1` | string | `United States` | Country of city 1 (mode=costOfLivingComparison) |
| `city1` | string | – | First city in the comparison (mode=costOfLivingComparison) |
| `country2` | string | `Germany` | Country of city 2 (mode=costOfLivingComparison) |
| `city2` | string | – | Second city in the comparison (mode=costOfLivingComparison) |
| `rankingsYear` | string | – | Rankings year, e.g. `2024` or `2024-mid` (mode=topCities); leave empty for the latest |
| `urls` | array | `[]` | Direct Numbeo URLs to scrape (mode=byUrl); the actor routes each to the matching parser |
| `maxItems` | integer | `5` | Hard cap on emitted records (1–1000) |
| `useProxy` | boolean | `false` | Route requests through Apify proxy; Numbeo is normally reachable without one |
| `autoEscalateOnBlock` | boolean | `true` | Automatically retry through proxy if a direct request is blocked |
| `proxyConfiguration` | object | `{"useApifyProxy": true, "apifyProxyGroups": []}` | Proxy configuration, used only when `useProxy` is enabled or escalation triggers |

### Example: cost of living for one city

```json
{
  "mode": "costOfLiving",
  "city": "New York",
  "maxItems": 1
}
```

### Example: quality of life across several cities

```json
{
  "mode": "qualityOfLife",
  "cities": ["Berlin", "Tokyo", "Lisbon", "Mexico City"],
  "maxItems": 4
}
```

### Example: compare two cities' cost of living

```json
{
  "mode": "costOfLivingComparison",
  "country1": "United States",
  "city1": "New York, NY",
  "country2": "Germany",
  "city2": "Berlin"
}
```

### Example: 2024 cost-of-living rankings

```json
{
  "mode": "topCities",
  "rankingsYear": "2024",
  "maxItems": 100
}
```

## Use cases

- **Relocation planning** — compare cost of living, safety and health care between a current and a prospective city
- **Compensation benchmarking** — pull itemized price data to adjust salary offers across cities
- **Market research** — track property price and rent indices for cities you're evaluating for investment
- **Academic and policy research** — bulk-export the annual rankings table for cross-city comparison
- **Travel and remote-work planning** — screen multiple candidate cities on pollution, traffic and quality-of-life indices in one run

## FAQ

**Is this affiliated with Numbeo?**
No. This is an independent actor that reads Numbeo's publicly available pages; it is not operated by or affiliated with Numbeo.

**Why are `rangeLow`/`rangeHigh` missing for some price items?**
Numbeo only publishes a contributor range when enough submissions exist for that item; when it doesn't show a range, this actor leaves those fields out rather than returning nulls.

**How often does the underlying data change?**
Numbeo is contributor-driven: popular cities' prices update frequently, while smaller cities may only update every few months. Each run reflects whatever Numbeo is currently displaying.

**What's the difference between `indices` and `sections`?**
`indices` is the page's headline index table (e.g. Safety Index, Crime Index). `sections` holds the detailed sub-rows underneath, like individual crime concerns or specific pollution/health-care ratings with their own value and qualitative rating label.

**Can I compare more than two cities at once?**
No — Numbeo's own comparison page only supports two cities side by side. Use separate single-city requests if you need more cities, then compare the records yourself.

**Why would a city return no data at all?**
If none of the slug variants the actor tries resolve to a real Numbeo page (for example, a misspelled or very obscure city name), that request comes back as an error record instead of a silent empty result.

**Can I pull historical rankings?**
Yes — `rankingsYear` accepts past years back to 2017 (and mid-year editions) for `topCities`. Single-city pages only ever show Numbeo's current data.

**Do I need to configure a proxy?**
Not normally — Numbeo is usually reachable directly. `autoEscalateOnBlock` automatically falls back to the configured proxy only if a direct request gets blocked.
