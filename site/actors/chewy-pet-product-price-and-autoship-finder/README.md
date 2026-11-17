# Chewy Pet Product Price & Autoship Finder

Chewy is one of the largest US online pet retailers, selling food, treats, toys and supplies for dogs, cats and other pets. This actor searches Chewy by keyword, category URL, brand name or a specific list of product URLs, and returns each product as a structured record with pricing, Autoship subscription price, rating and variant detail.

## What this actor does

- Searches Chewy products by keyword, with optional pet-type and sort filters
- Browses every product in a given category URL
- Pulls every product listed under a specific brand name
- Enriches a list of specific Chewy product URLs with full detail, including size/flavor variants
- Empty fields are omitted from records — a field only appears when Chewy actually shows that data for the product

## Output per product

- `productId` — Chewy's product/part number
- `name` — full product name
- `url` — canonical product URL
- `imageUrl` — main product image
- `images` — additional product image URLs
- `price` — current price in USD
- `salePrice` — sale price, when the product is discounted
- `autoshipPrice` — price under Chewy's Autoship subscription
- `brand` — brand/manufacturer name
- `brandUrl` — brand's page on Chewy
- `category`, `subcategory` — e.g. `Dog` / `Food`
- `rating` — average customer rating (0–5)
- `reviewCount` — total number of reviews
- `inStock` — `true` when the product is currently in stock
- `isAutoship` — `true` when Autoship is available for the product
- `pricePerUnit` — unit price text, e.g. `$1.25/oz`
- `petType` — pet type the product is intended for
- `description` — full product description (from product detail pages)
- `productVariants` — array of size/flavor options, each with its own price and stock status
- `recordType` — always `chewyProduct`
- `scrapedAt` — ISO 8601 timestamp of the scrape

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search`, `byCategory`, `byBrand`, or `byProductUrls` |
| `searchQuery` | string | `dog food` | Keyword search, used in `search` mode |
| `petType` | string | `all` | `all`, `dog`, `cat`, `fish`, `bird`, `reptile`, `small-pet`, or `farm-animal` — used in `search` mode |
| `sortBy` | string | `best-match` | `best-match`, `top-rated`, `bestselling`, `price-asc`, `price-desc`, or `new-arrivals` — used in `search` mode |
| `brandName` | string | – | Brand name to scrape all products for, used in `byBrand` mode |
| `categoryUrl` | string | – | Full Chewy category URL to browse, used in `byCategory` mode |
| `startUrls` | array | `[]` | Chewy product page URLs to enrich, used in `byProductUrls` mode |
| `minPrice` / `maxPrice` | integer | – | Price range in USD |
| `minRating` | number | – | Minimum average rating (0.0–5.0) |
| `inStockOnly` | boolean | `false` | Only return products currently in stock |
| `autoshipOnly` | boolean | `false` | Only return products eligible for Autoship |
| `maxItems` | integer | `50` | Maximum number of products to return (1–5000) |

### Example: dog food under $30, in stock

```json
{
  "mode": "search",
  "searchQuery": "dog food",
  "petType": "dog",
  "maxPrice": 30,
  "inStockOnly": true,
  "maxItems": 50
}
```

### Example: every product from one brand

```json
{
  "mode": "byBrand",
  "brandName": "Royal Canin",
  "maxItems": 100
}
```

### Example: enrich specific product pages with variants

```json
{
  "mode": "byProductUrls",
  "startUrls": [
    "https://www.chewy.com/royal-canin-adult-dry-dog-food/dp/123456"
  ]
}
```

## Use cases

- **Price monitoring** — track a watch-list of products for price or Autoship-discount changes
- **Brand catalog audits** — pull every product from a brand to check pricing and stock consistency
- **Category benchmarking** — compare price-per-unit across a whole category like dry dog food
- **Variant research** — enrich product URLs to see every size/flavor option and its individual price
- **Review tracking** — snapshot `rating` and `reviewCount` over time to watch sentiment trends

## FAQ

**Do I need a Chewy account?** No — only publicly available product listings are read; no login or API key is required.

**What is Autoship, and what does `autoshipPrice` mean?** Autoship is Chewy's recurring-delivery subscription, usually priced lower than a one-time purchase. `autoshipPrice` is that subscription price when the product offers it; `isAutoship` tells you whether the option exists at all.

**Why does a product have no `productVariants`?** That field is only populated when scraping product detail pages (`byProductUrls` mode or detail enrichment); search and category listing cards don't expose per-variant pricing.

**Can I filter by multiple pet types at once?** `petType` accepts one value per run; to cover several pet types, run the actor once per type.

**What's the difference between `search` and `byCategory` mode?** `search` uses Chewy's keyword search and respects `petType`/`sortBy`; `byCategory` walks a specific category URL directly, which is useful for exhaustively covering one product category.

**How many products can one run return?** Up to `maxItems`, capped at 5000.

**Is this affiliated with Chewy?** No. This is an independent, third-party actor that reads Chewy.com's publicly available product pages; it is not operated by or affiliated with Chewy, Inc.
