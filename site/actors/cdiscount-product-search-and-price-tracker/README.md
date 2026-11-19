# Cdiscount Product Search & Price Tracker

Cdiscount is one of France's largest online marketplaces, but comparing prices or ratings across more than a handful of listings means clicking through page after page by hand. This actor turns a Cdiscount keyword search, a list of product URLs, or a top-rated-products lookup into structured product records with pricing, discount, and rating data already extracted.

## What this actor does

- Searches Cdiscount by keyword, with sort order (relevance, price, rating, newest) and a price range filter applied to the results.
- Fetches full product pages by URL to pull brand, seller, and description alongside the pricing and rating fields.
- Surfaces top-rated products for a keyword by reading the same search results sorted by customer rating — this mode doesn't add new fields, it just orders the results differently.
- Computes the discount percentage itself from the current and pre-discount price whenever both are published.
- Leaves a field out of the record entirely when Cdiscount doesn't publish it for that product, instead of sending an empty placeholder.

## Output per product

| Field | Description |
|---|---|
| `productId` | Cdiscount's internal product identifier |
| `title` | Product name |
| `brand` | Manufacturer or brand name |
| `price` | Current price in euros |
| `originalPrice` | Pre-discount price in euros, when Cdiscount shows one |
| `discountPercent` | Discount percentage, computed from `price` and `originalPrice` |
| `rating` | Customer rating, 0–5 scale |
| `reviewCount` | Number of customer reviews |
| `imageUrl` | Main product image URL |
| `productUrl` | Direct link to the Cdiscount product page |
| `category` | Product category or department, from search results |
| `seller` | Marketplace seller name (from `productDetails` mode) |
| `description` | Product description text (from `productDetails` mode) |
| `searchKeyword` | The keyword that returned this product (`search` and `topSellers` modes) |
| `recordType` | Always `product` |
| `scrapedAt` | ISO 8601 UTC timestamp of the scrape |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` (keyword search), `productDetails` (fetch specific URLs), or `topSellers` (keyword search sorted by rating). Required. |
| `keyword` | string | `smartphone` | Search keyword, used in `search` and `topSellers` modes. |
| `productUrls` | array | `[]` | Cdiscount product page URLs to scrape, used in `productDetails` mode. |
| `sortBy` | string | `relevance` | Result order for `search` mode: `relevance`, `price_asc`, `price_desc`, `rating`, or `new`. |
| `minPrice` | integer | – | Keep only products priced at or above this value, in euros. |
| `maxPrice` | integer | – | Keep only products priced at or below this value, in euros. |
| `maxItems` | integer | `20` | Maximum number of products to return. |

### Example: keyword search with a price range

```json
{
  "mode": "search",
  "keyword": "aspirateur",
  "sortBy": "price_asc",
  "minPrice": 50,
  "maxPrice": 200,
  "maxItems": 50
}
```

### Example: specific product pages

```json
{
  "mode": "productDetails",
  "productUrls": [
    "https://www.cdiscount.com/telephonie/telephone-mobile/exemple-produit.html"
  ],
  "maxItems": 10
}
```

### Example: top-rated products for a category

```json
{
  "mode": "topSellers",
  "keyword": "ordinateur portable",
  "maxItems": 30
}
```

## Use cases

- **Price tracking** — watch how a product's price and discount move over time by rerunning `productDetails` on the same URLs.
- **Market research** — pull a category's full price and rating spread with a single `search` run.
- **Competitive benchmarking** — compare brand, seller, and rating data for similar products side by side.
- **Catalog enrichment** — add Cdiscount pricing and availability signals to a product database by matching on `productId`.
- **Deal discovery** — sort by `price_asc` or filter by `minPrice`/`maxPrice` to surface the cheapest options in a category.

## FAQ

**Does this need a Cdiscount account or login?**
No. All three modes read Cdiscount's public search and product pages.

**What currency are the prices in?**
Euros. Cdiscount is a French marketplace and doesn't publish prices in other currencies.

**What's actually different about `topSellers` mode?**
It runs the same keyword search as `search` mode, just sorted by customer rating instead of relevance. It doesn't add seller or description fields — for those, use `productDetails` with the product's URL.

**Why don't search results include `seller` or `description`?**
Those two fields only appear on the full product page, which `productDetails` mode fetches. Search results only carry what's visible on the search results grid.

**Why is `originalPrice` or `discountPercent` sometimes missing?**
Those fields are only included when Cdiscount itself publishes a pre-discount "crossed out" price for that product. If a product isn't discounted, there's nothing to compute a percentage from.

**Can I combine a price range with a sort order?**
Yes — `minPrice`/`maxPrice` and `sortBy` both apply to `search` mode and can be set together.

**How many products can one run return?**
Up to the `maxItems` value you set, capped at 500 per run.

**Is this affiliated with Cdiscount?**
No. This actor reads Cdiscount's public pages and is not affiliated with, endorsed by, or connected to Cdiscount in any way.
