# Amazon Third-Party Seller Profile & Storefront Catalog

Every third-party seller on Amazon has a public profile page and a storefront of their own listings. This actor turns both into structured records — the seller's business identity, rating history and recent individual feedback from the profile, and every product currently listed in their storefront catalog. No login, cookies, or proxy setup required.

## What this actor does

- **Three modes:** `PROFILE` (seller profile + feedback), `PRODUCTS` (storefront catalog), `BOTH` (default)
- **Two input paths:** supply seller IDs directly, or supply product URLs and the actor auto-derives the seller ID from each product's buy-box "sold by" link
- **Seller profile:** name, logo, overall stars, positive-feedback percentage, and 30-day / 90-day / 12-month / lifetime rating windows with counts
- **Feedback histogram:** percentage breakdown across 5/4/3/2/1 stars
- **Individual feedback entries:** recent feedback rating, text, rater, date, and the seller's own reply when Amazon displays one — filterable by exact star rating and time period
- **Public business data:** legal business name, business address, and customer-service phone number — data Amazon itself displays publicly on the seller profile page (toggle off with `includeBusinessDetails`)
- **Storefront catalog:** reuses the standard Amazon search-result card schema (title, price, rating, image, badges) for every product in the seller's shop
- **Category narrowing:** apply any category/facet from the seller's own refinement rail (`categoryFilter`)
- **Sort + pagination:** Amazon's six storefront sort orders, up to 100 pages (the seller's own result count is the real limit), with a separate per-seller product cap
- **23 Amazon marketplaces supported**
- **Empty fields are omitted** — no null placeholders, no fabricated data

## Output per seller profile record (`recordType: "sellerProfile"`)

- `sellerId`, `sellerName`, `sellerLogo`, `profileUrl`, `storefrontUrl`, `sourceUrl`
  (same URL as `profileUrl`)
- `starRating` — overall star rating shown in the page header
- `positivePercent12m`, `ratingsCount12m` — 12-month positive-feedback percent and count (when shown)
- `positivePercentWindow`, `positivePercent`, `positivePercentRatingsCount` — the exact window Amazon's own page header currently displays
- `feedbackWindows[]` — `{window, starRating, ratingsCount}` for each of 30 days / 90 days / 12 months / lifetime that Amazon actually shows data for
- `feedbackHistogram` — `{"5": {percent}, "4": {percent}, ...}`
- `feedbackEntries[]` — recent individual feedback, newest first:
  `{rating, text, dateText, rater, raterProfileUrl?, raterAvatarUrl?, wasSuppressed?,
  suppressReason?, hasSellerResponse?, responseText?}`. Amazon returns 5 entries per page;
  the actor merges the profile page's server-rendered entries with further pages from the
  profile's own feedback endpoint, deduped by rating/text/date/rater.
- `feedbackEntriesCount` — number of entries included
- `feedbackPeriod`, `feedbackRating` — the filters used for the entries
- `aboutText` — the seller's "About" description
- `phone` — customer-service phone number (public, `includeBusinessDetails=true`)
- `businessName`, `businessAddress` — public legal business identity
  (`includeBusinessDetails=true`). For the common 5-line Western format, `businessAddress` is
  `{street, city, state, zip, country}`; for addresses that don't fit that exact 5-line shape,
  `businessAddress` is instead `{addressLines: [...]}` — the real, ordered address lines exactly
  as Amazon renders them, never force-fit into the wrong field
- `returnRefundPolicyText`, `shippingPolicyText`, `privacyPolicyText` — the seller's own
  policy text, when Amazon's page renders one
- `scrapedAt`

## Output per seller product record (`recordType: "sellerProduct"`)

- `asin`, `sellerId`, `title`, `url`, `sourceUrl` (same URL as `url`)
- `price {value, currency, display}`, `listPrice`
- `stars`, `reviewsCount`
- `thumbnailImage`
- `prime`, `sponsored`, `resultType` (`ORGANIC`/`SPONSORED`), `badge`
- `boughtInPastMonth`
- `position {page, positionOnPage, globalPosition}`
- `scrapedAt`

## Output per storefront facets record (`recordType: "storefrontFacets"`)

One record per seller with products (mode `PRODUCTS`/`BOTH`), built from the storefront's own
refinement rail and sort dropdown — lets you discover what departments/filters and sort orders
exist for a seller's catalog before deciding what to request.

- `sellerId`, `storefrontUrl`, `sourceUrl` (same URL as `storefrontUrl`)
- `facets[]` — `{groupName, label, url, selected, refinementParameter?}` from the
  storefront's `#s-refinements` rail (Department, Delivery Day, Free Shipping, etc.).
  `refinementParameter` is the exact `rh` token `categoryFilter` accepts.
- `sortOptions[]` — `{value, label, selected}` from the storefront's own "Sort by" dropdown —
  `value` is the exact string the `sortBy` input accepts
- `pagesRequested`, `pagesFetched` — how many storefront pages were fetched vs.
  `maxProductPages`. A short fetch is never silently indistinguishable from a genuinely
  small storefront: `pagesStoppedReason` explains it (`BLOCKED`, `NO_MORE_RESULTS`,
  `MAX_PRODUCTS`, `UNEXPECTED_ERROR`)
- `scrapedAt`

## Output per error/terminal record (`recordType: "sellerError"`)

Emitted instead of a normal record when a seller/page could not be resolved
(not found, blocked, CAPTCHA, etc.) — the actor never silently returns zero
items for a requested seller without explaining why.

- `sellerId`, `sourceUrl`, `pageClassification` (e.g. `NOT_FOUND`, `CAPTCHA`, `DOG_PAGE_503`), `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `BOTH` | `PROFILE` / `PRODUCTS` / `BOTH` |
| `sellerIds` | array | – | Seller/merchant IDs or seller/storefront URLs |
| `productUrls` | array | – | Product URLs to derive seller IDs from (buy-box seller link) |
| `marketplace` | string | `US` | Amazon marketplace/domain (23 supported) |
| `maxProductPages` | int | `3` | Max storefront pages per seller, ~16 products/page (1-100) |
| `maxProductsPerSeller` | int | `200` | Hard cap on product records per seller |
| `categoryFilter` | string | – | Optional `rh` refinement token or full Amazon facet URL from `storefrontFacets` |
| `includeBusinessDetails` | bool | `true` | Include public business name/address/phone |
| `includeFeedbackEntries` | bool | `true` | Include recent individual feedback entries |
| `maxFeedbackEntries` | int | `20` | Max individual feedback entries per seller |
| `feedbackRating` | string | `all` | Exact star filter: `all`, `5`, `4`, `3`, `2`, `1` |
| `feedbackPeriod` | string | `12 months` | `30 days` / `90 days` / `12 months` / `lifetime` |
| `sortBy` | string | (default/Featured) | Storefront sort order matching Amazon's own dropdown |
| `proxyCountry` | string | `AUTO` | Optional geo override; `AUTO` follows the marketplace |

At least one of `sellerIds` or `productUrls` is required.

### Example: look up two sellers directly

```json
{
  "mode": "BOTH",
  "sellerIds": ["A294P4X9EWVXLJ", "A35BKAA6VXTYCT"],
  "maxProductPages": 2,
  "maxFeedbackEntries": 10
}
```

### Example: derive the seller from a product page

```json
{
  "mode": "PROFILE",
  "productUrls": ["https://www.amazon.com/dp/B0BTYCRJSS"]
}
```

### Example: one storefront category, price ascending, UK marketplace

```json
{
  "mode": "PRODUCTS",
  "sellerIds": ["A294P4X9EWVXLJ"],
  "marketplace": "GB",
  "categoryFilter": "n:172282",
  "sortBy": "price-asc-rank",
  "maxProductPages": 5,
  "maxProductsPerSeller": 80
}
```

### Example: recent critical feedback only

```json
{
  "mode": "PROFILE",
  "sellerIds": ["A294P4X9EWVXLJ"],
  "includeFeedbackEntries": true,
  "feedbackRating": "1",
  "feedbackPeriod": "90 days",
  "maxFeedbackEntries": 20
}
```

## Use cases

- **Lead generation** — build a list of active third-party sellers with public business
  name/address/phone for outreach
- **Competitor research** — monitor a competing seller's full storefront catalog, categories,
  pricing and sort order
- **Seller due-diligence** — check a seller's rating history across multiple feedback windows
  and read their recent individual feedback
- **Brand protection** — pull recent critical feedback and any seller replies
- **Marketplace research** — compare seller reputations across categories and marketplaces
- **Supply-chain verification** — confirm a seller's legal business identity before sourcing

## FAQ

**Is this affiliated with Amazon?**
No. This is an independent third-party actor that reads Amazon's own public seller profile and
storefront pages — no API keys, cookies, or login required.

**Do I need to configure a proxy?**
No. The actor chooses a working connection automatically and needs no proxy setup from you. Leave
`proxyCountry` on `AUTO` unless you specifically need another marketplace's exit country.

**Are individual feedback comments included?**
Yes. The public profile page renders recent individual feedback entries, and the actor also asks
the profile's own feedback endpoint for more pages. Each entry includes the star rating, the
feedback text (when the buyer wrote one), the rater display name, the date Amazon shows, and the
seller's reply when present. Filters let you request only a specific star rating and time window.

**Why are feedback dates not ISO-formatted?**
Amazon serves the date exactly as displayed for that marketplace ("November 11, 2026",
"9. November 2026", "22 octobre 2026"). The actor keeps that display string in `dateText` rather
than inventing a machine date it cannot verify.

**Is the business name/address/phone customer personal data?**
No. This is the seller's own public business identity that Amazon displays on every
seller's public profile page, distinct from any Amazon customer's personal data. You can disable it
with `includeBusinessDetails: false`.

**Why do some sellers have fewer feedback windows or no entries?**
Amazon only shows a feedback window when the seller has ratings data for that window, and only
renders entries when feedback exists. Amazon Resale, for example, has a profile but no feedback
histogram or entries. The actor reports exactly what Amazon displays, never a fabricated shape.

**Why is a seller record sometimes missing instead of empty?**
If a seller ID can't be resolved (not found, blocked, CAPTCHA), the actor emits an explicit
error/terminal record (`recordType: "sellerError"`) with a `pageClassification` explaining why,
rather than silently returning nothing.

**How many products does the storefront catalog return?**
Up to `maxProductPages` × ~16 products, further capped by `maxProductsPerSeller`. That is exactly
what Amazon's own storefront pagination exposes for that seller, not a fixed/guaranteed count.

**Does this work on every Amazon marketplace?**
Yes — all 23 supported marketplaces use the same profile/storefront/feedback surfaces. Non-US
marketplaces can occasionally route through a slower connection; the actor retries automatically.

**Why does `profileUrl`/`storefrontUrl` return an error in a plain script check?**
Amazon blocks some non-browser requests to `/sp?seller=...` and `/s?me=...` with a `503`, even
though the exact same URL loads fine in a real browser (or via this actor). `productUrl`
(`/dp/ASIN`) and media/thumbnail URLs are not behind this same block and return `200` from a plain
client.

**Is `sortBy` guaranteed across every storefront page?**
Amazon's own storefront reliably honors a non-default `sortBy` on page 1. For later pages the
actor carries the sort session forward using Amazon's own "next page" link and query-id, but
Amazon does not guarantee the same strict order past page 1 for every sort value — treat page 1 as
the authoritative sorted sample if you need a strict global order.

## Limitations

- **Member-since date and seller response time** are not present on the public seller profile
  pages this actor reads, so they are not emitted.
- **Positive / neutral / negative feedback counts** are not displayed separately; Amazon exposes
  the star histogram and positive-feedback percentage instead.
- **Storefront depth:** Amazon stops at the seller's own result count (for example 973 results =
  61 pages); `maxProductPages` defaults to 3 and can be raised to 100. Use `categoryFilter` to
  partition a very large catalog into narrower slices if you need a smaller, complete view.
- **Feedback pagination** stops at `maxFeedbackEntries` (1–200) and follows Amazon's own
  `hasNextPage` signal; a seller with no feedback yields no `feedbackEntries` field.
- **Seller discovery from category/search pages** is a different use case and is not part of this
  actor; supply seller IDs, seller URLs, or product URLs.
