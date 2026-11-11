# Zillow Housing Data Explorer - ZHVI, ZORI & Forecasts

Zillow publishes a deep set of public housing metrics: home values, rents, sale and list prices,
inventory, market speed, forecasts, market heat, affordability and housing cuts by property type and
bedroom count. This actor turns those public pages and Zillow Research files into clean records -
for one neighborhood or for every ZIP code in the country.

No login, API key, cookie or proxy setup is needed.

## What this actor does

- **Three modes** - one deep record per location, tidy monthly history rows, or a bulk market scan
- **Six region types** - city, state, county, ZIP, neighborhood and United States
- **ZHVI and ZORI** - latest values plus true 1/3/6/12-month changes and up to 100 months of history
- **Market metrics** - list and sale prices, inventory, days to pending, sale-to-list, price cuts, market heat, forecasts and affordability
- **35 Zillow Research datasets** - property-type and bedroom cuts down to ZIP and neighborhood, with filters, sorting and rank
- **Benchmarks** - parent state, county and national comparisons
- **Empty fields are omitted** - never `null`, blank or placeholder values

## Modes

| Mode | What it returns |
|---|---|
| `regionTrends` (default) | One detailed record per location: ZHVI and ZORI with 1/3/6/12-month changes, median sale and list prices, inventory, new listings, days to pending, sale-to-list, % sold above/below list, 1-year forecast where Zillow publishes it, parent state/county/national benchmarks, and up to 100 months of history |
| `history` | Tidy monthly rows, one per region x month x metric, for ZHVI, ZORI or both |
| `marketScan` | Bulk one-row-per-region output from a Zillow Research dataset: property type, bedroom count, bottom/top price tier, market heat, affordability, price cuts, sale/list metrics, forecasts and new-construction price per square foot, with filters, sorting and rank |

## Supported locations

`regionTrends` and `history` accept any location Zillow's own search resolves:

- City: `Austin, TX`
- State: `Texas` or `TX`
- County: `Travis County, TX`
- ZIP code: `78701`
- Neighborhood: `Barton Hills, Austin, TX`
- United States: `United States`

ZIP codes and neighborhoods are resolved through Zillow's autocomplete and the canonical
`/home-values/{regionId}/{slug}/` page. Some neighborhoods do not have their own page; Zillow then
renders the parent city or county page, and the record's `regionName`/`regionType` show what was
actually returned.

## Input

| Field | Type | Default | Notes |
|---|---|---|---|
| `mode` | select | `regionTrends` | `regionTrends`, `history`, `marketScan` |
| `locations` | string list | `["Austin, TX"]` | Used by `regionTrends` and `history` |
| `historyMonths` | integer 1-120 | `24` | Zillow pages carry up to 100 months |
| `historyMetric` | select | `zhvi` | `zhvi`, `zori`, `both` (history mode) |
| `dataset` | select | `zhviAllHomes` | Zillow Research series (marketScan mode) |
| `geography` | select | `city` | `metro`, `state`, `county`, `city`, `zip`, `neighborhood`, `us` |
| `state` | select | `all` | Market scan filter |
| `nameContains` | text | empty | Case-insensitive region-name filter |
| `regionIds` | string list | `[]` | Exact Zillow RegionIDs |
| `sortBy` | select | `sizeRank` | Sort and rank key |
| `maxItems` | integer 1-20000 | `200` (`prefill` 3) | Hard record cap; truncation is reported |

### Example: compare three cities

```json
{
  "mode": "regionTrends",
  "locations": ["Austin, TX", "Seattle, WA", "Denver, CO"],
  "historyMonths": 36
}
```

### Example: every ZIP code in Texas, ranked by 12-month home-value change

```json
{
  "mode": "marketScan",
  "dataset": "zhviAllHomes",
  "geography": "zip",
  "state": "TX",
  "sortBy": "biggestGain12m",
  "maxItems": 500
}
```

### Example: monthly rent history for one neighborhood

```json
{
  "mode": "history",
  "locations": ["Barton Hills, Austin, TX"],
  "historyMetric": "both",
  "historyMonths": 60,
  "maxItems": 120
}
```

### Example: market heat and affordability

```json
{
  "mode": "marketScan",
  "dataset": "marketHeatIndex",
  "geography": "metro",
  "maxItems": 50
}
```

## Output per record type

### `regionMarketTrends`

- `location`, `locationType`, `slug`, `url`, `sourceUrl`, `regionId`, `regionName`, `regionType`,
  `regionDisplayName`, `state`, `stateCode`, `county`, `metro`
- `zhviLatest`, `zhviYoY` (decimal), `zhviAsOf`, `zhviChange1mPct`, `zhviChange3mPct`,
  `zhviChange6mPct`, `zhviChange12mPct`
- `zoriLatest`, `zoriAsOf`, `zoriChange1mPct`, `zoriChange3mPct`, `zoriChange6mPct`,
  `zoriChange12mPct`
- `medianListingPrice`, `forSaleInventory`, `newListings`, `listingAsOf`
- `medianSalePrice`, `saleAsOf`, `saleToListRatio`, `pctSellingAboveList`,
  `pctSellingBelowList`, `medianDaysToPending`
- `zhvfGrowth1YrPct`, `zhvfAsOf` (ZIP and US only)
- `nationalZhviLatest`, `parentStateZhviLatest`, `parentCountyZhviLatest`, `vsNationalPct`,
  `vsStatePct`, `vsCountyPct`
- `zhviHistory`, `rentalHistory`, `historyMonths`
- `recordType`, `dataSource`, `scrapedAt`

### `marketHistoryObservation`

`location`, `locationType`, `slug`, `url`, `sourceUrl`, `regionId`, `regionName`, `regionType`,
`state`, `stateCode`, `county`, `metro`, `date`, `metric` (`zhvi` or `zori`), `value`, `unit`,
`recordType`, `dataSource`, `scrapedAt`.

### `marketObservation`

`geography`, `dataset`, `datasetLabel`, `metric`, `propertyType`, `unit`, `regionId`, `sizeRank`,
`regionName`, `regionType`, `state`, `stateCode`, `county`, `metro`, `city`, `latestValue`,
`latestDate`, `value1MonthAgo`, `value3MonthsAgo`, `value6MonthsAgo`, `value12MonthsAgo`,
`change1mPct`, `change3mPct`, `change6mPct`, `change12mPct`, `forecast1MonthPct`,
`forecast3MonthPct`, `forecast1YearPct` (forecast rows), `rank`, `rankedBy`, `sourceUrl`,
`recordType`, `dataSource`, `scrapedAt`.

Empty fields are omitted at every depth. A field appears only when Zillow publishes a real value.

## Datasets available in marketScan

Home values (13 cuts): all homes, single-family, condo/co-op, bottom tier, top tier, 1, 2, 3, 4 and
5+ bedrooms. Rents: all homes plus multifamily, single-family, multifamily. Forecasts: 1-month,
3-month and 1-year growth. Market metrics: for-sale inventory, new listings, newly pending, median
list price, median sale price, median sale-to-list, % sold above/below list, median and mean days
to pending, price-cut share and mean price cut, market heat index, new-construction sale price,
new-construction price per square foot. Affordability: income needed to buy, income needed to rent,
affordable home price, years to save, homeowner affordability and renter affordability.

Each dataset supports a subset of geographies. If the selected geography is not published, the run
returns a clear status message listing the supported levels.

## How the numbers are calculated

- Every trend is computed from Zillow's monthly month-end series by matching the **same calendar
  month** 1, 3, 6 and 12 months earlier. The actor never uses a positional "last N columns" offset.
- `zhviChange12mPct` is a percent. The legacy `zhviYoY` field stays a decimal fraction, matching
  the value Zillow's page reports.
- Benchmark deltas are percent differences from the parent state, parent county or national ZHVI.
- Rank is 1-based over every matching row **before** `maxItems` truncation.

## Limitations

- Zillow publishes data for the United States only. There are no non-US locales.
- `regionTrends` history is capped by the page payload at 100 months. Use `marketScan` for Zillow
  Research series that go back further.
- ZORI is not published for states or neighborhoods. It is available for metro areas, counties,
  cities and most ZIP codes.
- ZIP and neighborhood sale metrics are published less consistently than city/county metrics;
  fields Zillow does not publish are omitted rather than filled with a placeholder.
- The Zillow Research catalog publishes an all-homes median sale price per square foot only for
  new construction. There is no all-homes price-per-square-foot series in the current catalog.
- Market heat, affordability, inventory, list/sale price, days-to-pending and sale-to-list research
  series are metro/US level only.
- Forecasts from the live page are available for ZIP codes and the United States; the research
  forecast file covers metro areas and ZIP codes.
- Zillow restates history every monthly release. Treat each run as a snapshot; `scrapedAt` and
  `sourceUrl` record when and where it came from.
- A few neighborhoods (for example Tarrytown in Austin) do not have their own home-values page and
  fall back to the parent city or county page. The actor reports the page's real region and logs a
  warning.
- Zillow page URLs (`url` and `sourceUrl` on region records) are valid but may return HTTP 403 to a
  plain `curl` or scripted HEAD request because of Zillow's bot protection. They open normally in a
  browser. Every Zillow Research CSV `sourceUrl` on market-scan records returns HTTP 200 without
  cookies or a key.

## Use cases

- **Real estate investors** - compare home-value and rent trends across target ZIP codes
- **Market research** - rank metros or counties by 12-month gains, inventory or affordability
- **Relocation and site selection** - compare housing costs, forecasts and market heat between cities
- **Proptech and lending** - feed neighborhood-level ZHVI, ZORI and forecast history into models
- **Policy and academic research** - export reproducible Zillow Research series with clear attribution

## FAQ

**Is this affiliated with Zillow?**
No. It is an independent, third-party actor that reads publicly available Zillow pages and Zillow
Research downloads.

**Do I need a Zillow account, cookie or API key?**
No. The actor works with no credentials and no proxy setup.

**What is ZHVI?**
The Zillow Home Value Index is Zillow's estimate of the typical home value for a region and housing
cut. It is a value index, not a transaction-price average.

**What is ZORI?**
The Zillow Observed Rent Index is a smoothed measure of typical market-rate rent for a region.

**Why are some fields missing for a ZIP code?**
Zillow's sale and market-speed coverage at ZIP level is thinner than at city/county level. The
actor returns what Zillow publishes and omits the rest.

**Can I get more than 20,000 rows?**
No single run exceeds 20,000 records. Split by state, region ID or name filter to cover the full
catalog.

**How fresh is the data?**
Zillow updates research data monthly, usually in the weeks after a month ends. `latestDate` and
`zhviAsOf` show the month each value covers.

## Data source

Zillow's public home-values pages and the Zillow Research public data catalog. Data is attributed to
Zillow; see Zillow's research data terms before redistributing.
