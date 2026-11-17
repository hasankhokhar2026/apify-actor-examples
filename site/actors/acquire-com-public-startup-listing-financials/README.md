# Acquire.com Public Startup Listing Financials Extractor

Acquire.com lists startups and SaaS businesses for sale with asking price, revenue and profit figures attached. This actor reads Acquire's public listing pages — the same pages Acquire exposes to search engines, no login required — and turns each one into a structured record, with more than a dozen financial and business filters to narrow down the deals you care about.

## What this actor does

- Scrapes Acquire's public `/startup/<slug>` listing pages, either from a direct list of URLs or by walking the public sitemap
- Filters listings by category, asking price, annual revenue, revenue/profit multiples, business age, growth rate, customer count, location and more
- Derives `revenueMultiple` and `profitMultiple` from asking price and the listing's own reported financials when both are present
- Sorts results by listing freshness (sitemap `lastmod`) or by asking price
- Empty fields are omitted from records — a field only appears when Acquire actually published that data on the public page

## Output per listing

- `type` — always `acquire_listing`
- `url` — canonical `/startup/<slug>` listing URL
- `id` — short ID parsed from the listing's slug
- `listingHeadline` — listing title
- `listingType` — `startup_acquisition`, when a category was identified
- `category` — `SaaS`, `Ecommerce`, `Content`, `Services`, `Mobile Apps`, etc.
- `askingPrice`, `priceCurrency` — asking price and its currency
- `revenueAnnual`, `revenueMonthly` — reported annual/monthly revenue
- `profitAnnual`, `profitMonthly` — reported annual/monthly profit
- `totalRevenueAnnual`, `totalRevenueMonthly`, `totalProfitAnnual`, `totalProfitMonthly` — aliases of the revenue/profit fields above
- `revenueMultiple` — `askingPrice / revenueAnnual`, when both are known
- `profitMultiple` — `askingPrice / profitAnnual`, when both are known
- `customers` — customer count, when shown on the listing
- `businessModel` — business model description
- `teamSize` — reported team size
- `dateFounded` — when the business was founded
- `location` — business location, when shown
- `annualGrowthRate` — reported annual growth rate percentage
- `recastFinancials` — `true` when the listing's financials section indicates seller-recast figures
- `connectedMetrics` — `true` when the listing shows connected analytics (e.g. Google Analytics, Stripe)
- `metricsConnected` — detail on which metrics are connected, when shown
- `underAdvisory`, `advisory` — whether the listing is under Acquire advisory support, and the advisory status detail
- `techStackKeywords` — technology stack items listed under the Tech Stack section
- `businessModelKeywords` — business-model bullet points, when a dedicated section exists
- `growthOpportunityHighlights` — growth-opportunity bullet points
- `insights` — `{highlights}` key-insights bullet points
- `askingPriceHistory` — array of `{date, price}` entries, when a price-history table is shown
- `keywords` — page meta keywords
- `about` — full listing description
- `status` — `available`, `sold`, or `Under Offer`
- `image` — preview image URL
- `brand` — brand name from the page's structured data (typically `Acquire.com`)
- `source` — site name (typically `Acquire.com`)
- `canonicalUrl` — canonical URL for the page
- `pageType` — Open Graph page type (typically `website`)
- `scrapedAt` — ISO-8601 UTC timestamp when the record was collected

If zero listings match your filters, a single `acquire_blocked` record is emitted explaining why, so the run still finishes with output.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `urls` | array | `[]` | Direct Acquire.com listing URLs (`/startup/<slug>` preferred); overrides category/filter search when set |
| `categories` | array | `[]` | Limit to one or more categories: `SaaS`, `Ecommerce`, `Content`, `Services`, `Mobile Apps`, `Marketplace`, `Newsletter`, `Digital Marketing Agency`, `Shopify App`, `AI`, `Other` |
| `minPrice` / `maxPrice` | integer | – | Asking price range in USD |
| `locations` | array | `[]` | Country/region substrings to match against the listing's location (case-insensitive) |
| `minAnnualRecurringRevenue` / `maxAnnualRecurringRevenue` | integer | – | Annual revenue range in USD |
| `customers` | integer | – | Minimum reported customer count |
| `minAge` / `maxAge` | integer | – | Business age range in years, derived from the founding date |
| `minRevenueMultiple` / `maxRevenueMultiple` | integer | – | Range for `askingPrice / annualRevenue` |
| `minProfitMultiple` / `maxProfitMultiple` | integer | – | Range for `askingPrice / annualProfit` |
| `minTTMGrossRevenue` / `maxTTMGrossRevenue` | integer | – | Trailing-twelve-month gross revenue range in USD |
| `minTTMNetProfit` / `maxTTMNetProfit` | integer | – | Trailing-twelve-month net profit range in USD |
| `minAnnualGrowthRate` / `maxAnnualGrowthRate` | integer | – | Annual growth rate percentage range |
| `recastFinancials` | boolean | `false` | Only return listings flagged as having seller-recast financials |
| `connectedMetrics` | boolean | `false` | Only return listings showing connected analytics (e.g. Google Analytics, Stripe) |
| `underAdvisory` | boolean | `false` | Only return listings flagged as under Acquire advisory support |
| `hideUnderOffer` | boolean | `false` | Skip listings whose status is `Under Offer` |
| `verifiedBusiness` | boolean | `false` | Only return listings whose copy mentions being verified |
| `sortBy` | string | `newest` | `newest`, `oldest`, `price-low`, or `price-high` |
| `maxItems` | integer | `3` | Maximum listings to return (1–500) |
| `proxyConfiguration` | object | Residential US | Apify proxy configuration |

### Example: SaaS deals under $100k with a revenue multiple cap

```json
{
  "categories": ["SaaS"],
  "maxPrice": 100000,
  "maxRevenueMultiple": 3,
  "maxItems": 30
}
```

### Example: fast-growing, verified ecommerce businesses

```json
{
  "categories": ["Ecommerce"],
  "minAnnualGrowthRate": 20,
  "verifiedBusiness": true,
  "maxItems": 20
}
```

### Example: enrich specific listing URLs

```json
{
  "urls": [
    "https://app.acquire.com/startup/turnkey-calendly-alternative-abc1234567"
  ]
}
```

## Use cases

- **Deal sourcing** — filter listings by category, price and multiple to build a shortlist of acquisition targets
- **Due diligence prep** — pull a specific listing's full financials and highlights before reaching out to the seller
- **Market benchmarking** — compare revenue and profit multiples across categories to gauge fair pricing
- **Growth-stage screening** — filter on `minAnnualGrowthRate` to find fast-growing SaaS or ecommerce businesses for sale
- **Advisory/verification screening** — isolate listings under Acquire advisory support or flagged as verified for lower-risk sourcing

## FAQ

**Do I need to log into Acquire.com?** No — this actor only reads the public listing pages that Acquire exposes to search engines; the internal, login-gated marketplace is not accessed.

**Why are fields like churn rate, team structure, or raw analytics screenshots never returned?** Those live behind Acquire's authenticated in-app view and aren't part of the public page; the actor only emits fields it can read from the public listing.

**What counts as "verified" for the `verifiedBusiness` filter?** The public pages don't expose a structured verified flag, so this filter keeps listings whose headline or description text literally mentions being verified.

**Why does `sortBy` rely on sitemap freshness rather than a "newest" field on the listing?** The sitemap's `lastmod` is the only cross-category freshness signal available without logging in; price-based sorts over-fetch listings and re-sort them after scraping.

**Why is `revenueMultiple` sometimes missing even though `askingPrice` is present?** It's only computed when the listing also reports annual revenue; without both numbers there's nothing to divide.

**What happens if no listings match my filters?** The actor still finishes successfully and returns a single record explaining that nothing matched, so your downstream pipeline always sees output.

**Is this affiliated with Acquire.com?** No. This is an independent, third-party actor that reads Acquire.com's publicly available listing pages; it is not operated by or affiliated with Acquire.com.
