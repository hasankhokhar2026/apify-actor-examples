# Farfetch Luxury Fashion Price & Discount Extractor

Farfetch aggregates luxury fashion from boutiques and designer brands worldwide into one marketplace. This actor searches Farfetch by keyword, brand, gender, new arrivals or sale items — or looks up specific product URLs directly — and returns each item as a structured record with pricing, discount, color and designer details.

## What this actor does

- Searches Farfetch products by free-text keyword
- Browses all products from a specific luxury brand
- Lists new arrivals and currently discounted sale items, optionally filtered by gender
- Fetches full product details for a list of specific Farfetch product URLs
- Empty fields are omitted from records — a field only appears when Farfetch actually published that data for the product

## Output per product

- `productId` — Farfetch's internal product ID
- `brand` — brand/designer label on the product
- `title` — product name
- `price` — current (final/discounted) price
- `originalPrice` — pre-discount price, when the item is on sale
- `discountPercent` — discount percentage, when on sale
- `currency` — currency code (e.g. USD, EUR, GBP), matching the locale of the request
- `color` — product color
- `gender` — target gender category
- `category` — product category (e.g. bags, shoes)
- `imageUrl` — primary product image URL
- `productUrl` — direct link to the Farfetch product page
- `designer` — designer name, when distinct from `brand`
- `material` — product material, when listed
- `mode` — which scraping mode produced this record
- `scrapedAt` — ISO timestamp when the record was collected

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search`, `searchByBrand`, `newIn`, `saleItems`, or `productDetails` |
| `keyword` | string | `Gucci bag` | Search keyword, used in `search` mode |
| `brand` | string | – | Brand name/slug to filter by (e.g. `gucci`, `prada`), used in `searchByBrand` mode |
| `gender` | string | – (all genders) | `women`, `men`, or `kids` |
| `productUrls` | array | `[]` | Farfetch product page URLs to scrape directly, used in `productDetails` mode |
| `maxItems` | integer | `20` | Maximum number of products to return (1–1000) |

### Example: keyword search

```json
{
  "mode": "search",
  "keyword": "Prada shoes",
  "maxItems": 30
}
```

### Example: everything from one designer, women's only

```json
{
  "mode": "searchByBrand",
  "brand": "balenciaga",
  "gender": "women",
  "maxItems": 50
}
```

### Example: current sale items for men

```json
{
  "mode": "saleItems",
  "gender": "men",
  "maxItems": 40
}
```

### Example: look up specific products

```json
{
  "mode": "productDetails",
  "productUrls": [
    "https://www.farfetch.com/shopping/women/gucci-gg-marmont-shoulder-bag-item-12345678.aspx"
  ]
}
```

## Use cases

- **Price monitoring** — track a designer's catalog for price changes and new discounts
- **Trend forecasting** — scan new arrivals by gender to see what's launching across brands
- **Sale tracking** — pull `saleItems` regularly to catch deep discounts as they appear
- **Competitive benchmarking** — compare the same designer's pricing against other luxury retailers
- **Catalog enrichment** — feed a list of product URLs through `productDetails` to backfill price, color and material data

## FAQ

**Do I need a Farfetch account?** No — only publicly available product listings are read; no login or cookies are required.

**What currency are prices shown in?** Whatever currency Farfetch returns for the request, reflected in the `currency` field — check it rather than assuming USD.

**Why does a product have no `originalPrice` or `discountPercent`?** Those fields only appear when the item is actually marked down; full-price items simply don't carry a discount.

**What's the difference between `brand` and `designer`?** `brand` is the label Farfetch shows on the product card; `designer` is populated separately when Farfetch's product data distinguishes a specific designer from the brand line.

**Can I combine brand and gender filters?** Yes — set `mode` to `searchByBrand`, fill in `brand`, and set `gender` to narrow that brand's catalog to women's, men's, or kids' items.

**How many products can one run return?** Up to `maxItems`, capped at 1000.

**Is this affiliated with Farfetch?** No. This is an independent, third-party actor that reads Farfetch's publicly available product pages; it is not operated by or affiliated with Farfetch.com.
