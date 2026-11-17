# Wine Catalog Search by Type, Region & Vintage

Need a structured wine list without hand-building a database? This actor searches and browses a public catalog of red, white, sparkling, rosé, dessert and port wines, then returns one clean record per bottle: winery, vintage, country, region, community rating, ratings count, wine type and image. Filter by keyword, category, origin, rating, ratings count or vintage year, sort the result set, or look up specific wines by ID or URL.

## What this actor does

- **Search by keyword** — every word you enter must appear in the wine name, winery, country or region.
- **Browse one category** — reds, whites, sparkling, rosé, dessert or port.
- **Browse the whole catalog** — all six categories in one run.
- **Look up specific wines** — pass `type/id` references or full source URLs.
- **Filter precisely** — country, region, winery, minimum rating, minimum ratings count and a vintage year range.
- **Sort the output** — rating, popularity, vintage, wine name or winery, ascending or descending.
- **Omit empty fields** — a field appears only when the catalog actually has that value for the wine.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `search` | `search` (keyword + filters), `byType` (one category), `all` (every category) or `byIds` (specific wines). |
| `searchQuery` | string | – | Words matched against wine name, winery, country and region. All words must match; leave empty to keep everything. |
| `wineType` | select | `all` | `all`, `reds`, `whites`, `sparkling`, `rose`, `dessert` or `port`. Applies to every mode; in `byIds`, references from other categories are skipped and reported. |
| `wineIds` | string list | `[]` | Wines to fetch in `byIds` mode, e.g. `reds/4` or `https://api.sampleapis.com/wines/reds/4`. Combine with `wineType` to keep only one category. |
| `filterCountry` | select | – | One of the catalog's 25 countries, or “All countries”. |
| `filterRegion` | string | – | Region name, case-insensitive partial match, e.g. `Champagne` or `Napa Valley`. |
| `filterWinery` | string | – | Winery name, case-insensitive partial match. |
| `minRating` | number | – | Minimum community rating, 1.0–5.0. |
| `minReviews` | integer | – | Minimum number of community ratings behind the score. |
| `vintageMin` | integer | – | Earliest vintage year. Non-vintage wines are excluded when either vintage bound is set. |
| `vintageMax` | integer | – | Latest vintage year. |
| `sortBy` | select | `default` | `default` (catalog order), `ratingDesc`, `ratingAsc`, `reviewsDesc`, `reviewsAsc`, `vintageDesc`, `vintageAsc`, `nameAsc`, `nameDesc`, `wineryAsc`, `wineryDesc`. |
| `maxItems` | integer | `100` | Maximum records to emit, 1–5000. |

## Output per wine

| Field | Description |
|---|---|
| `wineName` | Wine name as listed; often includes the vintage and varietal. |
| `winery` | Producer or winery name. |
| `vintage` | Four-digit vintage year parsed from the wine name. Omitted for non-vintage bottles. |
| `country` | Country of origin. |
| `region` | Region or appellation. |
| `ratingAverage` | Community average rating on a 1.0–5.0 scale. |
| `reviewsCount` | Number of community ratings behind the average. |
| `wineType` | Human-readable category: Red, White, Sparkling, Rosé, Dessert or Port. |
| `wineTypeKey` | Category key used by the source API: `reds`, `whites`, `sparkling`, `rose`, `dessert` or `port`. |
| `wineId` | Numeric wine ID, unique within its category. Pair it with `wineTypeKey` for lookups. |
| `imageUrl` | Bottle image URL. |
| `sourceUrl` | Direct link to the wine's source record. |
| `recordType` | Always `wine`. |
| `scrapedAt` | ISO timestamp when the record was collected. |

## Examples

### Highly rated French sparkling wines

```json
{
  "mode": "search",
  "searchQuery": "champagne",
  "filterCountry": "France",
  "minRating": 4.5,
  "minReviews": 100,
  "sortBy": "ratingDesc",
  "maxItems": 50
}
```

### Every port wine in the catalog

```json
{
  "mode": "byType",
  "wineType": "port",
  "maxItems": 500
}
```

### Italian wines from the 1990s

```json
{
  "mode": "search",
  "filterCountry": "Italy",
  "vintageMin": 1990,
  "vintageMax": 1999,
  "sortBy": "vintageAsc",
  "maxItems": 100
}
```

### Look up saved wines by ID

```json
{
  "mode": "byIds",
  "wineIds": ["reds/4", "sparkling/12", "https://api.sampleapis.com/wines/port/7"]
}
```

## Data source

Records come from the public wine catalog at `api.sampleapis.com/wines`, which serves red, white, sparkling, rosé, dessert and port wine data as JSON. The endpoint is open: no account, API key, cookie or proxy configuration is needed, and the actor reads it directly over HTTPS.

## Limitations

- **Catalog size is fixed by the source.** It currently holds about 3,455 wines (718 reds, 504 whites, 736 sparkling, 508 rosé, 586 dessert, 403 port). `maxItems` above that simply returns the whole catalog.
- **No prices, merchant offers, tasting notes or critic scores.** The source does not publish them, so none are invented.
- **Vintage is parsed from the wine name.** Bottles labelled `N.V.` or without a year have no `vintage` field and are excluded by vintage filters.
- **A handful of records lack a winery or location.** Those fields are omitted rather than filled with placeholders.
- **Ratings are a community snapshot.** They reflect the source's current values, not a live Vivino lookup.

## Use cases

- Build or refresh a restaurant, bar or shop wine list.
- Seed a cellar or tasting app with rated wines by category and region.
- Compare producers in a region before a tasting flight.
- Filter for well-reviewed, widely rated bottles for a shortlist.
- Map catalog coverage by country, region and vintage.

## FAQ

**Do I need an API key or login?** No. The catalog is public and the actor needs no credentials or proxy setup.

**Can I search a specific wine name?** Yes — put one or more words in `searchQuery`. Matching is case-insensitive and checks wine name, winery, country and region.

**Why is a wine missing `vintage`?** The year is read from the wine name. Non-vintage wines have no year to extract, so the field is omitted.

**Why are some wines missing `winery`, `country` or `region`?** The source record itself lacks that value. Empty fields are omitted instead of emitted as null.

**How do I get more than 100 records?** Raise `maxItems` (up to 5,000). If you also set filters, the actor reports how many wines matched before the cap.

**Does `byIds` accept a bare number?** No. IDs repeat across categories, so include the category: `reds/4`, not `4`.

**Does `wineType` filter `byIds` lookups?** Yes. When a category is selected, references from other categories are skipped and listed in the run summary. Use `all` to look up mixed categories in one run.

**How fresh is the data?** The actor reads the catalog on every run. The catalog itself is a curated snapshot maintained by the source.
