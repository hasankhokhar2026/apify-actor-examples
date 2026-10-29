# BizBuySell Businesses-for-Sale & Financials Scraper

BizBuySell is the largest US marketplace for buying and selling small businesses, franchises and commercial real estate. This actor pulls listing cards straight from a state or category search URL and, on request, opens each listing to add the financial figures sellers disclose — cash flow, revenue, EBITDA, real estate and headcount.

## What this actor does

- **Browses a search URL** you give it (a US state page, the "established businesses" category, or the full marketplace) and walks pages until `maxItems` is reached
- **Extracts price in two forms** — a formatted string like `$1,150,000` and a numeric value for sorting, side by side
- **Pulls the full listing summary** rather than the truncated card preview
- **Re-hosts the listing photo** in the run's own storage so the image link opens reliably, while keeping the original source URL too
- **Optional financial enrichment** — turn on `enrichDetails` to fetch each listing's detail page for Cash Flow, Gross Revenue, EBITDA, Real Estate, Inventory, FF&E, Rent, founding year and employee count
- Fields that BizBuySell doesn't disclose for a given listing are left out of that record rather than sent as empty values

## Output per listing

- `url` — direct link to the listing on bizbuysell.com
- `productId` — BizBuySell's numeric listing ID
- `title` — business listing headline
- `description` — full listing summary text
- `location` — city and state, e.g. `Bonita Springs, FL`
- `category` — BizBuySell business category, when the source populates it
- `askingPrice` — formatted price, or `Not Disclosed` when the seller hides it
- `askingPriceNumeric` — numeric price for filtering/sorting (omitted for "Not Disclosed" listings)
- `image` — hosted URL of the listing's primary photo
- `imageOriginal` — the original BizBuySell CDN image URL
- `askingPriceDetail` — price as shown on the detail page, with `enrichDetails` on
- `cashFlow` — Seller's Discretionary Earnings, with `enrichDetails` on
- `grossRevenue` — annual gross revenue, with `enrichDetails` on
- `ebitda` — earnings before interest, tax, depreciation and amortization, with `enrichDetails` on
- `realEstate` — included real-estate value or status (`Owned`, `Leased`), with `enrichDetails` on
- `inventory`, `ffe`, `rentMonthly` — inventory value, furniture/fixtures/equipment, and monthly rent, with `enrichDetails` on
- `established` — year the business was founded, with `enrichDetails` on
- `employees` — headcount, with `enrichDetails` on
- `searchUrl` — the search URL this listing was found on
- `scrapedAt` — ISO 8601 UTC timestamp of extraction

If a run finds no listings at all (for example, a category path BizBuySell's mobile site doesn't support), it writes a single record with `_status: "no_data"`, `_reason`, and `_message` explaining why, instead of any listing fields.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchUrl` | string | – | BizBuySell search URL to scrape. State paths (e.g. `/california-businesses-for-sale/`) and the base marketplace URL work; keyword/price query strings and city sub-paths are not applied. |
| `maxItems` | integer | `50` | Maximum number of listings to extract (1–1,000). |
| `enrichDetails` | boolean | `false` | When true, opens each listing's detail page to add the financial fields listed above. |
| `proxy` | object | – | Optional proxy configuration; not required to retrieve data. |

### Example: statewide search

```json
{
    "searchUrl": "https://www.bizbuysell.com/california-businesses-for-sale/",
    "maxItems": 100
}
```

### Example: established businesses with financials

```json
{
    "searchUrl": "https://www.bizbuysell.com/established-businesses-for-sale/",
    "maxItems": 50,
    "enrichDetails": true
}
```

### Example: full marketplace, listings only

```json
{
    "searchUrl": "https://www.bizbuysell.com/businesses-for-sale/",
    "maxItems": 20,
    "enrichDetails": false
}
```

## Use cases

- **Buy-side deal sourcing** — build a sortable shortlist of businesses for sale by state and price
- **Business brokers** — track new and existing listings and their disclosed financials across a market
- **M&A and search-fund research** — pull cash flow and revenue figures in bulk to screen acquisition targets
- **Franchise and investment analysts** — monitor "established businesses" listings for valuation benchmarking
- **Market research** — study how asking prices and financial disclosure vary by state or category

## FAQ

**Do I need a BizBuySell account?**
No — every field this actor returns comes from public listing pages.

**Why does `askingPriceNumeric` sometimes disappear?**
Some sellers list their business as "Not Disclosed." Those records keep `askingPrice: "Not Disclosed"` but have no numeric price, since there isn't one to parse.

**Can I filter by keyword or price range?**
Only through the `searchUrl` you supply — use a US state path like `/texas-businesses-for-sale/`, the "established businesses" category, or the base marketplace URL. Query-string filters (`?q=`, `?pmin=`, `?pmax=`) and city sub-paths in the URL are not applied, and not every category path BizBuySell shows on its desktop site resolves the same way, so a run can come back empty for some of them.

**What does `enrichDetails` add, and is it slower?**
It fetches each listing's own detail page for Cash Flow, Gross Revenue, EBITDA, Real Estate, Inventory, FF&E, Rent, founding year and employee count. It adds one extra fetch per listing, so large runs with enrichment take longer than listings-only runs.

**Why are some financial fields missing even with `enrichDetails` on?**
BizBuySell sellers fill in these fields voluntarily. If a seller didn't disclose, say, EBITDA, that field is simply absent from the record.

**How many listings are on one search page?**
Roughly 55–58 per page, so a run with `maxItems: 100` typically needs just two pages.

**Is this affiliated with BizBuySell?**
No, this is an independent, third-party actor that reads BizBuySell's public listing pages. It is not affiliated with or endorsed by BizBuySell.com.
