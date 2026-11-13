# Wish.com Product Price & Rating Scraper

Wish.com lists budget, direct-from-manufacturer products across dozens of categories, each with its own price, discount, rating, and merchant information. This actor queries Wish by keyword, category, or specific product ID and returns one structured record per product.

## What this actor does

- Searches Wish by keyword, browses a category, or looks up specific products by ID.
- Collects the public listing rows Wish renders; anonymous Wish currently exposes about 12 items per search/category, so the source may cap the requested `maxItems`.
- Filters `search`/`byCategory` results by price range, minimum rating, and sale status.
- Returns price, rating, merchant ID, review count and discount from search/category listings; `byProductId` lookups return a lighter record (see below).
- Fields Wish doesn't provide for a given product are left out of that product's record.

## Output per product

`search` and `byCategory` return:

| Field | Description |
|---|---|
| `productId` | Wish product ID (24-character hex string). |
| `name` | Product name/title. |
| `price` | Listed price in USD. |
| `rating` | Average customer rating (0–5), when shown on the listing tile. |
| `ratingCount` | Number of reviews shown for the listing, when greater than zero. |
| `numBought` | Purchase count shown on the tile (e.g. `42 bought this`), when present. |
| `merchantId` | Seller/merchant identifier. |
| `mainImageUrl` | Main product image URL. |
| `isOnSale` | Whether the listing currently has a crossed/list price above the current price. |
| `discountPercent` | Discount percentage derived from the tile's local current and crossed prices, when on sale. |
| `productUrl` | Direct link to the Wish product page. |
| `recordType` | Always `"product"`. |
| `siteName` | Always `"Wish"`. |
| `scrapedAt` | ISO 8601 timestamp of when this actor fetched the record. |

`byProductId` returns a lighter record from the product detail page — `productId`, `productUrl`, `mainImageUrl` (when found), plus the same `recordType`/`siteName`/`scrapedAt` — without `name`, `price`, `rating`, or `merchantId`. `isOnSale` on a `byProductId` record is always `false`, since the detail page lookup doesn't carry sale-price data; set `onSaleOnly: true` only with `search`/`byCategory`, since it will exclude every `byProductId` result.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | String (select) | `"search"` | What to fetch: `search` (keyword), `byProductId` (specific products), or `byCategory` (browse). |
| `query` | String | `"phone case"` | Search keyword, used when `mode` is `search`. |
| `productIds` | Array of strings | `[]` | Wish product IDs to fetch directly, used when `mode` is `byProductId`. |
| `category` | String (select) | `"electronics"` | Category to browse, used when `mode` is `byCategory` (e.g. Fashion & Clothing, Home & Garden, Beauty & Personal Care, Toys & Games, and 16 others). |
| `minPrice` | Number | – | Drop products cheaper than this price (USD). |
| `maxPrice` | Number | – | Drop products more expensive than this price (USD). |
| `minRating` | Number | – | Drop products with an average rating below this value (0.0–5.0). |
| `onSaleOnly` | Boolean | `false` | Only return products that currently have a discounted price. |
| `maxItems` | Integer | `5` | Maximum number of products to return (1–500). |

### Example: keyword search under a price cap

```json
{
    "mode": "search",
    "query": "wireless earbuds",
    "maxPrice": 30,
    "maxItems": 40
}
```

### Example: browse a category, on-sale items only

```json
{
    "mode": "byCategory",
    "category": "electronics",
    "onSaleOnly": true,
    "maxItems": 50
}
```

### Example: look up specific products by ID

```json
{
    "mode": "byProductId",
    "productIds": ["5e955e7d91a1d604c5af24b2"]
}
```

## Use cases

- **Dropshipping research** — scan a category or keyword for low-priced, well-rated products worth sourcing.
- **Price monitoring** — track `price` for a set of search results over time.
- **Catalog building** — collect product images and listing prices for a category to seed a comparison feed.

## FAQ

**Do I need a Wish account to use this?**
No. This actor reads publicly accessible Wish product pages and listings.

**What categories can I browse?**
`byCategory` accepts any of 20 categories covering fashion, electronics, home & garden, beauty, toys, sports, automotive, pets, jewelry, health, bags & accessories, office & school, tools, baby, gaming, outdoor, shoes, phone accessories, computers, and kitchen.

**Why are some fields missing on certain products?**
Not every product tile exposes every field, and `byProductId` lookups return a smaller field set than `search`/`byCategory` (see Output above). Fields that Wish doesn't provide for a given product, or that this actor doesn't extract for that mode, are omitted rather than filled with a placeholder.

**What is a Wish product ID, and where do I find one?**
It's the 24-character hex string that appears in a product's URL (`wish.com/product/{productId}`). Any product returned by `search` or `byCategory` includes its own `productId` you can reuse with `byProductId`.

**Is `maxItems` always reached?**

No. The public listing surface currently exposes about 12 products per search/category; there is no working anonymous offset pagination. The actor emits what Wish serves and documents the cap.

**How current is `rating`?**
It reflects Wish's displayed 0-5 rating on the search/category listing tile. `ratingCount` is a separate field from the tile's review count; it is never used as the rating.

**Can I combine `minPrice`, `maxPrice`, `minRating`, and `onSaleOnly` in one run?**
Yes, but they only have an effect on `search` and `byCategory` results — `byProductId` records don't carry price/rating/sale data, so `onSaleOnly: true` will exclude every `byProductId` result.

**Is this affiliated with Wish?**
No. This actor is an independent tool that reads Wish's public product pages and is not affiliated with or endorsed by Wish (ContextLogic Inc.).
