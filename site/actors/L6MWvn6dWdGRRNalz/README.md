# Coupang Product Finder with Rocket Delivery Flags

Search Coupang, South Korea's largest online marketplace, by keyword or category, pull details for specific product IDs, or fetch best sellers — with pricing in Korean Won, discount rate, rating and Rocket delivery status on every product.

## What this actor does

- Searches Coupang by keyword, with sort order and price-range filters
- Fetches full details for a list of specific product IDs, including description and category breadcrumb
- Browses products within a category, or fetches that category's best sellers
- Flags whether a product qualifies for Rocket (fast) delivery and free shipping
- Omits any field Coupang doesn't provide for a product rather than returning a null or placeholder value

## Output per product

| Field | Description |
|---|---|
| `productId` | Coupang's unique product ID |
| `productName` | Product name, in Korean and/or English |
| `brand` | Product brand, when listed |
| `price` | Current sale price in KRW |
| `originalPrice` | Original price before discount, when a discount applies |
| `discountRate` | Discount percentage |
| `rating` | Average customer rating (0-5) |
| `reviewCount` | Number of customer reviews |
| `imageUrl` | Product image URL |
| `seller` | Seller or vendor name |
| `isRocket` | `true` when the product qualifies for Coupang's fast Rocket delivery |
| `isFreeShipping` | `true` when shipping is free |
| `productUrl` | Direct link to the product page on Coupang |
| `description` | Product description — only present on product-detail records |
| `categories` | Category breadcrumb — only present on product-detail records |
| `scrapedAt` | UTC timestamp when the record was scraped |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string (required) | search | search (keyword search), productDetails (by product ID), categoryProducts (browse a category), or bestSellers (best sellers in a category) |
| `keyword` | string | – | Search keyword — used in `search` mode |
| `productIds` | array of strings | `[]` | Coupang product IDs to fetch — used in `productDetails` mode |
| `categoryId` | string | – | Coupang category ID — used in `categoryProducts` and `bestSellers` modes |
| `sortBy` | string | bestSelling | Sort order for search results: bestSelling, priceAsc, priceDesc, rating, or newest |
| `minPrice` / `maxPrice` | integer | – | Price range filter, in KRW |
| `rocketOnly` | boolean | false | Only include products with Rocket delivery |
| `maxItems` | integer | 20 | Maximum number of products to return (1-500) |

### Example: keyword search sorted by rating

```json
{
  "mode": "search",
  "keyword": "노트북",
  "sortBy": "rating",
  "rocketOnly": true,
  "maxItems": 30
}
```

### Example: product details by ID

```json
{
  "mode": "productDetails",
  "productIds": ["123456789", "987654321"]
}
```

### Example: best sellers in a category

```json
{
  "mode": "bestSellers",
  "categoryId": "1001",
  "maxItems": 50
}
```

## Use cases

- **Price monitoring** — track a product's price, discount rate and Rocket status over time
- **Market research** — compare ratings and review counts across brands for a product category
- **Assortment analysis** — see which products rank as best sellers in a given category
- **Cross-border sourcing** — identify well-reviewed, fast-shipping products worth importing
- **Competitive pricing** — benchmark your own pricing against similar Coupang listings

## FAQ

**What is Rocket delivery?**
Rocket (로켓배송) is Coupang's fast-delivery program, offering free next-day or same-day delivery on eligible products. `isRocket` reflects whether a product qualifies.

**What currency are prices in?**
Korean Won (KRW), matching what's shown on Coupang.

**Can I search using English keywords?**
Yes — Coupang's search accepts both Korean and English keywords.

**Why do `description` and `categories` only appear sometimes?**
Those two fields come from a product's detail page and are only populated in `productDetails` mode; search, category-browse and best-seller results don't include them.

**How do I find a category ID?**
Category IDs are the numeric identifier at the end of a Coupang category URL, e.g. the `1001` in `https://www.coupang.com/np/categories/1001`.

**Why are some fields like `brand` or `seller` missing from a product?**
Not every listing publishes a brand or seller name on Coupang; when it's missing on the page, it's left out of the record.

**Is this affiliated with Coupang?**
No. This actor reads Coupang's public pages and is not affiliated with, endorsed by, or sponsored by Coupang.
