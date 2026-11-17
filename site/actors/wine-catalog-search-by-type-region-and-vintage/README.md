# Wine Catalog Search by Type, Region & Vintage

Looking for structured wine data without building your own tasting database from scratch? This actor searches a public wine catalog spanning red, white, sparkling, rosé, dessert and port wines, and returns each matching bottle as a record with winery, vintage, community rating, country and region — filterable by name, producer, origin, rating and vintage year.

## What this actor does

- Searches wines by free-text keyword matched against the wine name and winery
- Browses an entire wine category at once (reds, whites, sparkling, rosé, dessert or port)
- Fetches every wine across all six categories in one run
- Filters results by country, region, winery, minimum rating, and a vintage year range
- Empty fields are omitted from records — a field only appears when the catalog actually has that data for the wine

## Output per wine

- `wineName` — full wine name as listed, which may include vintage year and varietal
- `winery` — producer/winery name
- `vintage` — vintage year, extracted from the wine name when present (omitted for non-vintage wines)
- `country` — country of origin
- `region` — wine region or appellation
- `ratingAverage` — community average rating (1.0–5.0 scale)
- `reviewsCount` — number of community ratings behind the average
- `wineType` — category: Red, White, Sparkling, Rosé, Dessert, or Port
- `imageUrl` — wine bottle image URL
- `sourceUrl` — direct link to the catalog record
- `recordType` — always `wine`
- `scrapedAt` — ISO timestamp when the record was collected

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` (filter by name/winery/country/region), `byType` (browse one category), or `all` (every category) |
| `searchQuery` | string | `cabernet` | Free-text query matched against wine name and winery, used in `search` mode |
| `wineType` | string | `reds` | `reds`, `whites`, `sparkling`, `rose`, `dessert`, or `port` — the category to fetch, used only in `byType` mode (ignored in `search`/`all`, which cover every category) |
| `filterCountry` | string | – | Only return wines from this country, e.g. `France` (case-insensitive partial match) |
| `filterRegion` | string | – | Only return wines from this region, e.g. `Napa Valley` (case-insensitive partial match) |
| `filterWinery` | string | – | Only return wines from this winery (case-insensitive partial match) |
| `minRating` | number | – | Minimum community rating (1.0–5.0) |
| `vintageMin` | integer | – | Only return wines with a vintage year at or after this value |
| `vintageMax` | integer | – | Only return wines with a vintage year at or before this value |
| `maxItems` | integer | `100` | Maximum number of records to return (1–5000) |

### Example: highly-rated French Bordeaux reds

```json
{
  "mode": "search",
  "searchQuery": "bordeaux",
  "filterCountry": "France",
  "minRating": 4.5,
  "maxItems": 50
}
```

### Example: every port wine in the catalog

```json
{
  "mode": "byType",
  "wineType": "port",
  "maxItems": 500
}
```

### Example: Italian Barolo wines from the 1990s

```json
{
  "mode": "search",
  "filterCountry": "Italy",
  "filterRegion": "Barolo",
  "vintageMin": 1990,
  "vintageMax": 1999
}
```

## Use cases

- **Wine list curation** — pull a category or region to build a restaurant or shop wine list
- **Cellar research** — filter by winery and vintage range to find bottles worth tracking down
- **Tasting app content** — seed an app's wine database with structured records by type and region
- **Comparative tasting notes** — gather a region's top-rated wines before planning a tasting flight
- **Market mapping** — see how wine counts and ratings are distributed across countries and regions

## FAQ

**Do I need an API key or login?** No. The catalog this actor reads is fully public with no registration or key required.

**Are prices included?** No — the underlying catalog does not publish pricing data, so no price field is returned.

**Can I search for an exact wine name?** Set `mode` to `search` and put part of the name in `searchQuery`; the match is case-insensitive and checks both the wine name and winery fields.

**Why do some wines have no `vintage`?** The vintage year is parsed out of the wine name text. Non-vintage ("N.V.") wines have no year to extract, so the field is left out.

**How are ratings scored?** Ratings are community scores on a 1.0–5.0 scale, aggregated from wine enthusiast reviews in the source catalog.

**What's the difference between `mode: byType` and `mode: all`?** `byType` fetches one category you choose via `wineType`; `all` fetches every category (reds, whites, sparkling, rosé, dessert, port) in a single run.

**How fresh is the data?** The actor queries the catalog live on every run, so results reflect whatever the source currently has published.
