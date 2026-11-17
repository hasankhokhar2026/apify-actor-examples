# Gumroad Product Search & Storefront Extractor

Gumroad hosts independent creators selling ebooks, courses, templates, memberships and other digital products. This actor searches Gumroad's discover results by keyword, resolves specific product URLs, or pulls every product from a seller's storefront — returning price, rating, product type and creator details for each item, with no login required.

## What this actor does

- Searches Gumroad's public discover results by keyword
- Resolves a list of exact Gumroad product URLs directly
- Scrapes a seller's storefront to collect every product they sell
- Filters by product type, price range, minimum rating, pay-what-you-want pricing and seller verification
- Optionally emits a separate seller profile record for each unique creator encountered
- Empty fields are omitted from records — a field only appears when Gumroad actually publishes that data for the item

## Output per product

- `productId`, `permalink` — Gumroad's internal product ID and permalink
- `title` — product name
- `url` — direct product URL
- `thumbnailUrl` — product thumbnail image
- `nativeType` — product type (e.g. `digital`, `course`, `membership`, `bundle`, `podcast`, `audiobook`, `newsletter`, `ticket`)
- `priceCents` — price in the smallest currency unit (cents)
- `price` — price as a decimal amount
- `currencyCode` — currency code the price is denominated in
- `isPayWhatYouWant` — `true` when the buyer can set their own price
- `isSalesLimited`, `quantityRemaining` — whether the product has a sales cap, and units left when shown
- `ratingCount`, `ratingAverage` — number of ratings and the average score
- `sellerId`, `sellerName`, `sellerProfileUrl`, `sellerAvatarUrl`, `sellerVerified` — the selling creator's identity and verification state
- `sellerSubdomain` — the creator's Gumroad subdomain
- `creatorTwitterHandle` — creator's linked Twitter/X handle, when shown
- `summary` — short product summary
- `recurrence` — billing recurrence, for subscription-style products
- `durationInMonths` — membership duration, when applicable
- `attributes` — product attribute list (e.g. format, length), when shown
- `descriptionHtml`, `descriptionText` — full product description
- `coverUrls` — product cover image URLs
- `recordType` — `product`
- `scrapedAt` — ISO timestamp when the record was collected

## Output per seller (when `includeSellerRecord` is enabled)

- `sellerId`, `sellerName`, `sellerAvatarUrl`, `sellerProfileUrl`, `sellerSubdomain`, `sellerVerified`, `sellerTwitterHandle`
- `productCount` — number of products observed for this seller during the run
- `productTypes` — distinct product types observed for this seller
- `recordType` — `seller`
- `scrapedAt` — ISO timestamp when the record was collected

Invalid lookups (e.g. a malformed product or seller URL) return a typed `error` record rather than failing the run silently.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `searchProducts` | `searchProducts`, `byProductUrls`, or `bySellerUrls` |
| `searchQuery` | string | – | Discover keyword, used in `searchProducts` mode |
| `productUrls` | array | – | Gumroad product URLs to enrich, used in `byProductUrls` mode |
| `sellerUrls` | array | – | Gumroad seller/storefront URLs to scrape, used in `bySellerUrls` mode |
| `nativeTypes` | array | `[]` | Restrict to one or more product types: `digital`, `course`, `membership`, `bundle`, `podcast`, `audiobook`, `newsletter`, `ticket`. Leave empty for all types |
| `minPrice` / `maxPrice` | number | – | Price range in USD |
| `minRating` | number | – | Minimum average rating (0–5) |
| `payWhatYouWantOnly` | boolean | `false` | Only include products that let the buyer set their own price |
| `sellerVerifiedOnly` | boolean | `false` | Only include products from verified Gumroad sellers |
| `includeSellerRecord` | boolean | `true` | Also emit a seller profile record for each unique seller encountered |
| `sortBy` | string | `relevance` | `relevance`, `priceAsc`, `priceDesc`, `ratingDesc`, or `newest` |
| `maxItems` | integer | `5` | Maximum number of records to extract (1–5000) |

### Example: search for Notion templates under $20

```json
{
  "mode": "searchProducts",
  "searchQuery": "notion",
  "maxPrice": 20,
  "sortBy": "ratingDesc",
  "maxItems": 30
}
```

### Example: enrich specific product URLs

```json
{
  "mode": "byProductUrls",
  "productUrls": ["https://gumroad.com/l/exampleproduct"]
}
```

### Example: snapshot a seller's full storefront

```json
{
  "mode": "bySellerUrls",
  "sellerUrls": ["https://exampleseller.gumroad.com"],
  "includeSellerRecord": true,
  "maxItems": 100
}
```

## Use cases

- **Pricing research** — compare prices and ratings across competing digital products in a niche
- **Affiliate offer hunting** — search a topic to find highly-rated products worth promoting
- **Creator lead generation** — build a list of sellers in a category along with their storefront size
- **Storefront monitoring** — re-scrape a seller URL over time to track new products or price changes
- **Market mapping** — filter by `nativeType` to see how courses, memberships and bundles compare in a category

## FAQ

**Do I need a Gumroad account?** No — only publicly available product and storefront data is read; no login, cookies or API key are required.

**What's the difference between the three modes?** `searchProducts` runs a discover keyword search, `byProductUrls` resolves specific product links you already have, and `bySellerUrls` walks an entire seller's storefront to list every product they sell.

**Why do some products have no `ratingCount`?** Not every Gumroad product has received reviews yet; in that case the rating fields are left out rather than shown as zero.

**What does `includeSellerRecord` add?** When enabled, the actor also pushes one extra record per unique seller it encounters, summarizing their profile and how many products were seen for them in this run.

**Can I combine multiple product-type filters?** Yes — `nativeTypes` accepts a list, so you can include, for example, both `course` and `membership` in the same run.

**Why did a URL come back as an `error` record instead of a product?** The URL didn't resolve to a valid Gumroad product or seller page — the actor reports this explicitly rather than failing the whole run.

**Is this affiliated with Gumroad?** No. This is an independent, third-party actor that reads Gumroad's publicly available pages; it is not operated by or affiliated with Gumroad, Inc.
