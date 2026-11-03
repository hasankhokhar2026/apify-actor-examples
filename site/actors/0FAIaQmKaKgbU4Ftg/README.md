# Amazon Best Sellers & Rankings Scraper

Scrape **Amazon's chart family** -- Best Sellers, New Releases, Most Wished For, Most Gifted, and Movers & Shakers -- for any category on any Amazon marketplace. Get rank, ASIN, title, price, rating, and category for every product Amazon currently exposes on a chart, with optional recursion into subcategories and optional product-detail enrichment.

## What this actor does

- **Five chart types:** Best Sellers, New Releases, Most Wished For, Most Gifted, Movers & Shakers
- **Any category:** pass a category slug (`electronics`), a slug + browse-node ID (`electronics/172541`), or paste a full Amazon chart URL
- **Category-tree recursion:** optionally walk each category's subcategory links up to a configurable depth, scraping every subcategory's own chart too
- **20 Amazon marketplaces:** amazon.com, .co.uk, .de, .fr, .it, .es, .ca, .com.au, .co.jp, .in, .com.br, .com.mx, .nl, .se, .pl, .com.tr, .ae, .sa, .sg, .eg
- **Honest empty-chart handling:** Movers & Shakers legitimately has no items for many categories -- the actor emits a clear chart-metadata record instead of silently returning zero items or substituting unrelated products
- **Empty fields are omitted**

## Output per chart item

- `rank` -- position on the chart
- `asin` -- Amazon Standard Identification Number
- `title`, `url`, `image`
- `price` -- `{value, currency, display}` (only emitted when Amazon shows an explicit price)
- `stars`, `reviewsCount`
- `badge` -- e.g. `BestSeller`, `AmazonsChoice` (only when Amazon shows one)
- `format` -- format/variant summary, e.g. `"Paperback"` or `"4 formats available"` (books/media charts only, when Amazon's card shows one)
- `chartType`, `category`, `categoryNodeId`, `categoryUrl`, `page`
- `rankChangeDirection`, `rankChangeAmount` -- Movers & Shakers only, and only when Amazon's own rank-change marker is present
- `listPrice`, `inStock` -- only when `includeProductDetails` is enabled, and only when the product's own detail page shows explicit crossed-out list-price or in-stock/out-of-stock evidence (never inferred)
- `childCategories` -- sibling/child category links `{name, path, url, nodeId}` from the chart page's own category nav, when present (e.g. "Camera & Photo", "Computers & Accessories" under Electronics)
- `recordType: "chartItem"`, `scrapedAt`

## Output: chart metadata record

Emitted once per category when a chart is empty or a page cannot be loaded, instead of returning zero items silently:

- `chartType`, `category`, `categoryNodeId`, `categoryUrl`, `domain`
- `extractedItemCount` -- how many items were actually extracted (0 for an empty/failed chart)
- `message` -- human-readable explanation (e.g. "No items currently available for this chart/category.")
- `recordType: "chartMetadata"`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `chartType` | string | `bestSellers` | `bestSellers` / `newReleases` / `mostWishedFor` / `mostGifted` / `moversAndShakers` |
| `domain` | string | `amazon.com` | Which Amazon marketplace to scrape |
| `categoryUrls` | array | `["electronics"]` | Category slugs, slug/nodeId pairs, or full chart URLs |
| `categoryNodeIds` | array | `[]` | Additional `rootSlug/nodeId` entries |
| `maxDepth` | int | `0` | Subcategory recursion depth (0-3) |
| `startPage` | int | `1` | First chart page to fetch |
| `maxPages` | int | `2` | Max chart pages to fetch per category |
| `maxItemsPerCategory` | int | `60` | Hard cap on items per category |
| `maxItems` | int | `200` | Hard cap on total items across the run |
| `includeProductDetails` | boolean | `false` | Enrich items with product-detail-page data |
| `maxProductDetails` | int | `10` | Cap on product-detail fetches when enabled |
| `proxyConfiguration` | object | AUTO | Apify proxy (datacenter by default) |

### Example: Best Sellers in Electronics

```json
{
  "chartType": "bestSellers",
  "categoryUrls": ["electronics"],
  "maxItems": 50
}
```

### Example: New Releases for a specific subcategory (Headphones)

```json
{
  "chartType": "newReleases",
  "categoryUrls": ["electronics/172541"],
  "maxItems": 30
}
```

### Example: recurse a whole department's subcategories

```json
{
  "chartType": "bestSellers",
  "categoryUrls": ["electronics"],
  "maxDepth": 2,
  "maxItemsPerCategory": 20,
  "maxItems": 500
}
```

### Example: Movers & Shakers on the UK marketplace

```json
{
  "chartType": "moversAndShakers",
  "domain": "amazon.co.uk",
  "categoryUrls": ["electronics"]
}
```

## Use cases

- **Market research** -- track which products dominate a category's chart over time
- **Competitive intelligence** -- monitor a competitor's category ranking and pricing
- **Trend spotting** -- New Releases and Movers & Shakers surface emerging products before they're widely known
- **Gift-guide content** -- Most Gifted and Most Wished For power seasonal buying-guide content
- **Category research** -- recurse a department's full subcategory tree to map an entire vertical's top products

## FAQ

**Is this actor affiliated with Amazon?**
No. This is a third-party actor that scrapes Amazon's public chart pages.

**Does the actor guarantee "Top 100" for every category?**
No. The actor extracts all chart items Amazon currently exposes up to your `maxPages`/`maxItemsPerCategory` limits in a single session. Amazon's own pagination does not reliably expose a fixed rank count on every category, so the actor never claims a guaranteed top-N -- check `extractedItemCount` on the chart-metadata record to see how many items were actually found.

**Why is Movers & Shakers sometimes empty?**
Amazon itself frequently has no movers-and-shakers data for a given category at a given time -- this is a real, documented state on Amazon's own site, not a scraper bug. The actor emits a chart-metadata record explaining this instead of guessing or substituting unrelated recommended products.

**Why do some items have no `price` or `rating`?**
Amazon only shows these when they exist on the chart card. The actor never fabricates a price or rating -- if the field is missing, it's omitted from the record entirely.

**How is `rank` different from position across separate runs?**
`rank` reflects Amazon's own displayed chart position at scrape time. The actor holds no state between runs, so `rankChangeDirection`/`rankChangeAmount` (Movers & Shakers only) are populated strictly from Amazon's own rank-change marker on the page, never inferred by comparing separate runs.

**Does the actor need a proxy?**
No -- it uses Apify's free AUTO (datacenter) proxy by default, which works for the large majority of requests. If a session gets repeatedly blocked, the actor automatically escalates to a residential proxy session as a fallback.

**Can I scrape a whole department's subcategories in one run?**
Yes -- set `maxDepth` to 1-3 and the actor walks each category's subcategory links (visible in Amazon's own left-nav) that many levels deep, scraping each subcategory's own chart.
