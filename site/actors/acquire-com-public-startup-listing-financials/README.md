# Acquire.com Public Startup Listing Financials Extractor

Acquire.com is a marketplace where founders list SaaS products, ecommerce stores, mobile apps, agencies, newsletters and other online businesses for sale. This actor turns those public listings into structured deal data: asking price, trailing-twelve-month revenue and profit, last month's numbers, valuation multiples, growth, customer metrics, company details and the seller's own acquisition notes. It reads only the pages Acquire publishes for search engines, so no account, cookie or proxy setup is required.

## What this actor does

- **Three ways to collect listings:** browse the whole public marketplace, search it by keyword, or refresh a list of specific listing URLs
- **Full public financials:** asking price, TTM and last-month revenue/profit, revenue and profit multiples, ARR, growth, customers, churn and other disclosed metrics
- **Deal filters:** price, revenue, profit, multiples, growth, ARR, customers, business age, team size, category, location, business model, tech stack, financing, document counts, verified-business, recast-financials, open-to-offers and badge signals
- **Optional public Firebase enrichment:** turn on `includePublicDetails` to add marketplace status and history, first-listed date, financial snapshot, recast SDE, Google Analytics traffic, views/favorites/conversations, file-count breakdown and seller flags
- **Covers the public marketplace:** the sitemap currently exposes roughly 1,250 public listings, and a single run can return all of them
- **Clean records:** empty fields are omitted at every depth, and numeric values are parsed from the display text so they can be sorted and charted
- **Legacy URLs keep working:** both current `/public/<slug>` links and older `/startup/<slug>` links are accepted

## Output per listing

Identity and listing basics:

- `type`, `recordType` — always `acquire_listing`
- `url`, `sourceUrl` — canonical public listing URL
- `id`, `slug` — short listing ID and full URL slug
- `listingHeadline` — seller-written title
- `category`, `categoryLabel` — category code and the page's display label
- `location` — seller country
- `listingType` — `startup_acquisition`
- `lastModified` — sitemap last-updated time, when found through the sitemap

Price and financials:

- `askingPrice`, `askingPriceText`, `priceCurrency` — numeric price, displayed price (including `Open to offers`) and currency
- `ttmRevenue`, `ttmProfit` — trailing-twelve-month revenue and net profit
- `lastMonthRevenue`, `lastMonthProfit` — most recent month's revenue and profit
- `revenueAnnual`, `profitAnnual`, `revenueMonthly`, `profitMonthly` — backward-compatible names for the same figures
- `totalRevenueAnnual`, `totalProfitAnnual`, `totalRevenueMonthly`, `totalProfitMonthly` — legacy aliases
- `revenueMultiple`, `profitMultiple` — asking price divided by TTM revenue / TTM profit
- `annualGrowthRate` — year-over-year revenue growth percentage
- `arr`, `churnRate`, `churnRateRange`, `churnRateTrend` — disclosed recurring revenue and churn metrics
- `customers`, `customersRange`, `customersHigh`, `customersValueType` — customer count, the displayed range, its upper bound and an `exact` / `band` / `openEnded` marker
- `customerMetrics` — every other customer metric shown, such as downloads, monthly active users, app-store rating, paying users, SKUs, inventory value, contract value and retention
- `totalDownloads`, `monthlyActiveUsers`, `appStoreRating`, `payingUsers`, `skuCount`, `inventoryValue`, `productManufactured`, `avgContractValue`, `clientRetentionRate`, `topClientConcentration`, `topCustomerLocation`, `userStickiness` — parsed dedicated fields when the listing discloses them

Company and acquisition details:

- `dateFounded`, `foundedYear`
- `teamSize`, `teamSizeMin`, `teamSizeMax`
- `businessModel`, `businessModelKeywords`, `businessModelDescription`
- `techStackKeywords`, `techStackDescription`
- `growthOpportunityHighlights`, `growthOpportunitiesDescription`
- `competitors[]`, `keyAssets[]`
- `sellingReasoning[]`, `sellingReasoningDescription`, `financing[]`
- `askingPriceReasoning` — the seller's explanation of the asking price
- `pnlDocumentCount`, `supportingFileCount` — document counts shown as badges
- `connectedMetrics`, `metricsConnected` — whether a Google Analytics traffic section is present
- `verifiedBusiness` — public Verified business highlight (US entities with a verified address and incorporation certificate)
- `underAdvisory`, `advisory` — Guided by Acquire badge, when present
- `underMAAdvisory` — public Under M&A advisory highlight, when present
- `priceReduced` — Price Reduced badge, when present
- `recastFinancials` — public Recast financials hero badge or highlight card, when present
- `financingPreApproved` — public Pre-approved for financing highlight, when present
- `openToOffers` — asking price is shown as open to offers
- `askingPriceHistory` — public price-history table, when present

Content and metadata:

- `about` — the seller's full description
- `insights.highlights[]` — the Key Highlights bullets; with enrichment, also `insights.views`, `insights.weeklyViews`, `insights.favorites` and `insights.conversations`
- `image` — the page's social preview image
- `brand`, `source`, `canonicalUrl`, `pageType`
- `keywords` — meta keywords, when present
- `status` — `available` or `sold`
- `marketplaceStatus`, `underOffer` — public Firebase marketplace status and under-offer flag, when enrichment is on
- `statusHistory[]` — public status changes with ISO dates, when enrichment is on
- `firstListedAt`, `marketplaceAppearanceAt`, `createdAt`, `lastStatusChangeAt`, `updatedAt` — public listing dates, when enrichment is on
- `financialSnapshot` — public revenue/expenses/net income/SDE entries, when enrichment is on
- `recastSde` — latest non-zero SDE from the public financial snapshot, when present
- `gaTraffic` — weekly public Google Analytics Users, Sessions, BounceRate (percent) and SessionDuration (seconds) plus top channels, when enrichment is on
- `fileCounts` — public file-count breakdown (`profitAndLoss`, `supportingFiles`, `cim`, `videoPreview`, `recastProfitAndLoss`), when enrichment is on
- `sellerVerified`, `sellerRespondsQuickly`, `sellerLastResponseAt` — public seller flags, present and true when the public document reports them
- `scrapedAt` — ISO-8601 UTC collection time

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `auto` | `auto`, `browse`, `search`, or `byUrls` |
| `urls` | array | `[]` | Specific `/public/<slug>` or `/startup/<slug>` listing links (mode=byUrls) |
| `searchQuery` | string | – | Words to find across the listing text (mode=search); all words must appear |
| `categories` | array | `[]` | Limit to categories such as SaaS, Ecommerce, Mobile Apps, Agency, Marketplace, AI, Content, Newsletter, Shopify App or Crypto |
| `locations` | array | `[]` | Seller country or region names, case-insensitive |
| `minPrice` / `maxPrice` | integer | – | Asking price range in USD |
| `minTTMGrossRevenue` / `maxTTMGrossRevenue` | integer | – | Trailing-twelve-month revenue range in USD |
| `minTTMNetProfit` / `maxTTMNetProfit` | integer | – | Trailing-twelve-month net profit range in USD; negative values allowed |
| `minAnnualRecurringRevenue` / `maxAnnualRecurringRevenue` | integer | – | Backward-compatible annual revenue range |
| `minArr` / `maxArr` | integer | – | Annual recurring revenue range, when the listing discloses ARR |
| `minRevenueMultiple` / `maxRevenueMultiple` | number | – | Asking price ÷ TTM revenue range |
| `minProfitMultiple` / `maxProfitMultiple` | number | – | Asking price ÷ TTM profit range |
| `minAnnualGrowthRate` / `maxAnnualGrowthRate` | number | – | Year-over-year revenue growth percentage range |
| `customers` / `maxCustomers` | integer | – | Customer-count range; the lower bound of a displayed band is compared |
| `minAge` / `maxAge` | integer | – | Business age range in years, derived from Date Founded |
| `teamSizes` | array | `[]` | `Just me (1)`, `Small (2-20)`, `Medium (21-100)` |
| `businessModels` | array | `[]` | Keywords for the seller's business-model tags, e.g. Subscription, B2B, DTC |
| `techStack` | array | `[]` | Keywords for the seller's tech-stack list, e.g. WordPress, Shopify, Laravel |
| `financingTypes` | array | `[]` | Bootstrapped, Loans, Crowdfunding, Angel investment, Grants or Other |
| `minPnlDocuments` | integer | – | Minimum P&L document count |
| `minSupportingFiles` | integer | – | Minimum supporting-file count |
| `connectedMetrics` | boolean | `false` | Only listings with a Google Analytics traffic section |
| `verifiedBusiness` | boolean | `false` | Only listings with the public Verified business highlight |
| `underAdvisory` | boolean | `false` | Only listings with the Guided by Acquire badge |
| `recastFinancials` | boolean | `false` | Only listings with the Recast financials badge or highlight card |
| `priceReducedOnly` | boolean | `false` | Only listings with a Price Reduced badge |
| `openToOffersOnly` | boolean | `false` | Only listings shown as open to offers |
| `includePublicDetails` | boolean | `false` | Add public Firebase status, dates, financial snapshot, GA traffic, insights, file counts and seller flags for returned listings |
| `sortBy` | string | `newest` | `newest`, `oldest`, `sitemap`, or a price / revenue / profit / growth / multiple low-high sort |
| `maxItems` | integer | `50` | Maximum listing records to save (1–1,250) |
| `maxScan` | integer | `0` | Optional cap on pages inspected; 0 means no extra cap |
| `maxConcurrency` | integer | `3` | Concurrent listing-page requests (1–8) |
| `proxyConfiguration` | object | – | Optional connection override; no proxy is required |

### Example: newest SaaS listings with disclosed profit

```json
{
  "mode": "browse",
  "categories": ["SaaS"],
  "minTTMNetProfit": 10000,
  "sortBy": "newest",
  "maxItems": 50
}
```

### Example: affordable, fast-growing ecommerce or content businesses

```json
{
  "mode": "browse",
  "categories": ["Ecommerce", "Content"],
  "maxPrice": 150000,
  "minAnnualGrowthRate": 20,
  "sortBy": "revenue-multiple-low",
  "maxItems": 40
}
```

### Example: keyword search across the public marketplace

```json
{
  "mode": "search",
  "searchQuery": "Shopify subscription",
  "maxItems": 25
}
```

### Example: refresh specific listings

```json
{
  "mode": "byUrls",
  "urls": [
    "https://app.acquire.com/public/oa2pfifwmk-b2c-speech-therapy-app-for-kids-5-000-customers-300k-arr-974-growth",
    "https://app.acquire.com/startup/b2dtmgraxt-ai-helpdesk-guided-selling-wordpress-plugins-profitable-1k-customers"
  ]
}
```

## Use cases

- **Deal sourcing:** build a shortlist of acquisition targets by category, price, revenue, profit, growth and multiple
- **Valuation research:** compare revenue and profit multiples across SaaS, ecommerce, mobile and content businesses
- **Daily monitoring:** schedule a newest-first run and send new listings to a spreadsheet, CRM, Slack or email
- **Due-diligence prep:** pull the seller's description, price reasoning, highlights, assets, financing and document counts before an introductory call
- **Market mapping:** see which tech stacks, business models and locations are coming to market
- **Portfolio screening:** filter for recurring revenue, ARR, low churn, team size or a specific acquisition budget

## FAQ

**Do I need an Acquire.com account?** No. The actor reads only the public listing pages that Acquire exposes to search engines.

**Can I get the seller's identity, website, contact details or data-room files?** No. Those remain restricted. Public enrichment adds aggregate seller flags and listing metadata, never seller IDs, names, emails, contacts or private document bytes.

**What does `includePublicDetails` add?** For returned listings only, it reads Acquire's public Firebase documents and adds marketplace status/history, first-listed and update dates, financial snapshot, recast SDE, weekly Google Analytics traffic with channels, views/favorites/conversations, a file-count breakdown and public seller flags. The page parser remains the primary source; enrichment failures are skipped gracefully.

**Why are some fields missing for some listings?** Sellers choose which metrics to disclose. A field appears only when the public page or, with `includePublicDetails`, the public Firebase document shows it; empty fields are omitted rather than filled with placeholders.

**Are the financial values numbers or text?** The actor parses displayed values such as `$1.2M`, `$351k` and `+974%` into numbers, while keeping the original asking-price text in `askingPriceText`.

**How many listings can one run return?** The public sitemap currently contains about 1,250 listings, and `maxItems` allows up to 1,250, so the whole public marketplace fits in one run.

**What does "newest" mean?** It means most recently updated according to the sitemap's last-modified timestamp, not the date the listing was first published.

**Why do customer counts sometimes look low?** Acquire often shows a band such as `1,000-5,000`. `customers` holds the lower bound, `customersHigh` the upper bound, `customersRange` the original text and `customersValueType` says whether the source is `exact`, a `band` or `openEnded`.

**Do I need a proxy or cookies?** No. The actor connects directly by default and can fall back to a standard platform proxy if the source starts blocking requests.

**Is this affiliated with Acquire.com?** No. This is an independent, third-party actor that reads publicly available listing pages.

**What happens when no listing matches?** The run still succeeds, returns no records, and the status message explains how many pages were inspected and why nothing matched.
