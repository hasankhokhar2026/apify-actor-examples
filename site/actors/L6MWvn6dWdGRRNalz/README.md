# Coupang Best Sellers & Rocket Delivery Flags

Collect Coupang best sellers by category, Coupang's own keyword suggestions, or the Coupang category tree. The best-seller surface returns product identity, Korean-won pricing, discount, rating, review count, Rocket delivery, delivery promise, cashback, unit price, coupon and category breadcrumb data. No user proxy, cookie, or login is required; the actor selects its own Apify proxy route when Coupang blocks direct access.

Coupang's Akamai edge blocks keyword search, product-detail pages and review pages from non-Korean and datacenter IPs. Those modes are kept in the Mode dropdown for older saved tasks but are marked unavailable; they stop with a clear status message instead of returning an empty dataset. The actor ships the best-seller, keyword-suggestion and category-tree surfaces that work without user credentials.

## What this actor does

- Ranks the products on a Coupang best100 page from 1 to 30, with current price, original price, discount, rating, review count, Rocket delivery, delivery promise, cashback, unit price and coupon when Coupang publishes them.
- Walks all 15 top-level categories with `category=all` for up to 450 unique products from the top-level pages.
- Optionally walks a category's child best100 pages when `includeSubcategories=true`, stopping as soon as `maxItems` is reached.
- Deduplicates variants by `vendorItemId`, then `itemId`, then `productId` plus price.
- Returns Coupang's search-box suggestions for a list of keywords.
- Returns the Coupang category tree with category IDs, names, levels, parent IDs, paths and URLs.
- Keeps products tied to `productId`, `itemId` and `vendorItemId`, so variants are not merged by product ID alone.
- Omits fields Coupang does not publish for a product rather than writing nulls or placeholders.

## Output per best-seller product

| Field | Description |
|---|---|
| `productId` | Coupang product ID |
| `itemId` | Coupang item ID for the exact listing |
| `vendorItemId` | Coupang vendor-item ID for the exact seller option |
| `productName` | Product name as shown on Coupang |
| `price` | Current price in KRW |
| `originalPrice` | Original price in KRW, when higher than the current price |
| `discountRate` | Discount percentage, when greater than zero |
| `unitPrice` | Unit-price text, when Coupang shows one |
| `coupon` | Coupon object or text, when Coupang shows one |
| `rating` | Average star rating, when shown |
| `reviewCount` | Number of reviews, when shown |
| `imageUrl` | Product image URL |
| `productUrl` | Direct Coupang product URL, preserving item and vendor-item IDs |
| `isRocket` | `true` when the card carries Coupang's Rocket badge |
| `isRocketFresh` | `true` only when the card's Rocket image is the Rocket Fresh badge |
| `isFreeShipping` | `true` only when the card carries Coupang's free-shipping badge |
| `deliveryPromise` | Coupang's delivery promise text, when shown |
| `cashbackText` | Coupang's cashback text, when shown |
| `cashback` | Cashback amount in KRW parsed from `cashbackText` |
| `isSponsored` | Whether the card is marked as sponsored |
| `isSoldOut` | Whether the card is marked as sold out |
| `rank` | Position on the best100 page, starting at 1 |
| `categoryId` | Coupang best100 category ID that produced the row |
| `categoryName` | Human-readable category name |
| `categories` | Category breadcrumb path from the Coupang category tree, when available |
| `currency` | `KRW` |
| `source` | `bestSellers` |
| `recordType` | `product` |
| `scrapedAt` | UTC timestamp when the record was scraped |

Existing compatibility fields `brand`, `seller`, `description` and `categories` remain in the output schema. `brand`, `seller` and `description` are not published on the best100 page, so they are omitted from best-seller records rather than fabricated.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `bestSellers` | Best sellers, keyword suggestions, category tree, or a legacy mode. Search, product details and reviews are marked unavailable and stop with a clear status. |
| `category` | select | `electronics` | Best-seller category. Includes all 15 top-level categories plus All categories. Each page returns up to 30 products. |
| `categoryId` | string | – | Optional numeric Coupang best100 category ID or `/np/categories/` URL. Overrides the category dropdown. |
| `includeSubcategories` | boolean | `false` | Continue into child best100 pages until Maximum products is reached. Small `maxItems` values usually need no child pages. |
| `minPrice` | integer | – | Minimum price in KRW. |
| `maxPrice` | integer | – | Maximum price in KRW. |
| `rocketOnly` | boolean | `false` | Keep only products with Coupang's Rocket delivery badge. |
| `minRating` | number | – | Keep only products rated at least this many stars. Products without a rating are skipped. |
| `maxItems` | integer | `20` | Maximum products to return. One best100 page has at most 30. |
| `searchQueries` | string list | `[]` | Keywords for keyword suggestions. Korean or English. |
| `maxSuggestions` | integer | `10` | Maximum suggestions per keyword (1-10). |
| `maxCategories` | integer | `1000` | Maximum category nodes to return (1-5000). The full tree currently has about 2,740 nodes. |

### Example: best sellers in electronics

```json
{
  "mode": "bestSellers",
  "category": "electronics",
  "maxItems": 30
}
```

### Example: more than 30 rows with child categories

```json
{
  "mode": "bestSellers",
  "category": "electronics",
  "includeSubcategories": true,
  "maxItems": 100
}
```

### Example: keyword suggestions

```json
{
  "mode": "keywordSuggestions",
  "searchQueries": ["laptop", "무선 이어폰"],
  "maxSuggestions": 10
}
```

### Example: category tree

```json
{
  "mode": "categories",
  "maxCategories": 5000
}
```

### Example: legacy mode alias

```json
{
  "mode": "categoryProducts",
  "category": "electronics",
  "maxItems": 30
}
```

`categoryProducts` is a visible legacy alias that returns best sellers. Legacy `keyword`, `sortBy` and `productIds` keys are tolerated and mapped or ignored as appropriate; they are not shown as separate current inputs.

## Use cases

- **Best-seller tracking** — see which products Coupang ranks highest in a category and how their prices and ratings change.
- **Price monitoring** — track current price, original price, discount, unit price and coupon availability.
- **Delivery analysis** — compare Rocket, Rocket Fresh, free-shipping and delivery-promise coverage.
- **Assortment research** — inspect brand and category composition across Coupang's top-level departments.
- **Search-box research** — collect Coupang's own keyword suggestions for content, SEO and merchandising work.
- **Category mapping** — export the live category tree with IDs, parent IDs, paths and URLs.

## Limits and behavior

- One Coupang best100 page exposes at most **30 products**. The actor pages into child categories only when `includeSubcategories=true` and `maxItems` is still unmet.
- `category=all` walks the 15 top-level pages and returns at most **450 unique products**; enable child fan-out to go deeper.
- Keyword search, product-detail pages and reviews are blocked without a Korean residential proxy. They are not claimed as working and fail with a clear status message.
- Keyword suggestions are capped at 10 per query by Coupang. Multiple queries can be supplied for broader coverage.
- The category tree currently contains about 2,740 nodes. Raise `maxCategories` to 5000 to export all of them.
- The actor uses its own hardcoded Apify proxy route when Coupang's edge blocks a request. Users do not configure a proxy.
- A blocked or parse-failed run fails honestly; it never exits successfully with an empty dataset.

## FAQ

**Do I need a Coupang account, cookie or proxy?**
No. The best-seller, keyword-suggestion and category-tree modes work without user credentials or proxy setup. The actor handles any required proxy route itself.

**Why can't I search Coupang by keyword?**
Coupang's search page is protected by Akamai and refuses non-Korean and datacenter traffic. This deployment ships the working best-seller, keyword-suggestion and category-tree surfaces instead of claiming a search path it cannot fill.

**How do I get more than 30 products from one category?**
Set `includeSubcategories=true` and raise `maxItems`. The actor reads child best100 pages in order until the limit is met.

**Why are some fields like `brand` or `seller` missing?**
Those fields are not published on Coupang's best100 cards. The actor omits them rather than inventing values. Product-detail enrichment is unavailable without the blocked detail page.

**Why is `categories` empty sometimes?**
The breadcrumb comes from Coupang's category tree. If the tree cannot be fetched on a run, products are still returned and the run status says the breadcrumb was unavailable.

**What currency are prices in?**
Korean Won (KRW), matching Coupang.

**How do I find a category ID?**
Category IDs are the numeric value in a Coupang category URL, e.g. `178155` in `https://www.coupang.com/np/categories/178155`.

**Is this affiliated with Coupang?**
No. This actor reads Coupang's public pages and is not affiliated with, endorsed by, or sponsored by Coupang.

## Data source

Coupang's public best100 category pages, keyword suggestion endpoint and category tree. No private API, partner API, user login or user-supplied credentials are used.
