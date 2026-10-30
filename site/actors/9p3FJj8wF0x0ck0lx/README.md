# Flipkart Product Price & Specs Scraper

Flipkart lists price, MRP, discount and a short spec summary on nearly every product card and detail page, but that data is locked inside the page markup. This actor pulls it out as structured records — whether you start from a keyword search, a category page, or a list of product links you already have — with no API key or login step.

## What this actor does

- **Three modes:** `search` (keyword search), `byCategory` (browse category URL), `byUrl` (fetch specific product URLs)
- **Filters:** price range (min/max in INR), minimum rating
- **Sort options:** relevance, price low-to-high, price high-to-low, popularity, newest, highest rated
- **Rich pricing data:** sale price, original MRP, discount percentage, currency (INR)
- **Pagination:** automatically pages through results up to your `maxItems` limit
- **Empty fields are omitted** — only populated fields appear in output records

## Output per product

- `productId` — Flipkart product PID identifier
- `itemId` — Flipkart internal item identifier
- `title` — full product title as shown on Flipkart
- `subtitle` — secondary descriptive line shown under the title, when Flipkart provides one
- `url` — full URL to the product listing
- `brand` — brand name (extracted from title)
- `price` — current sale price in INR
- `originalPrice` — original MRP in INR (when discounted)
- `discountPercent` — discount percentage off original price (when > 0)
- `currency` — always `INR`
- `rating` — average product rating (1.0–5.0)
- `reviewCount` — total number of ratings
- `keySpecs` — array of key product specifications (processor, RAM, storage, etc.)
- `imageUrl` — main product image (400×400, HTTPS)
- `availability` — product availability status
- `seller` — seller name (when available)
- `recordType` — always `product`
- `scrapedAt` — UTC timestamp of when the record was scraped

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `byCategory` / `byUrl` |
| `searchQuery` | string | – | Keyword search query (mode=search) |
| `categoryUrl` | string | – | Flipkart category URL, e.g. `https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g` (mode=byCategory) |
| `startUrls` | array | – | List of Flipkart product URLs (mode=byUrl) |
| `sortBy` | string | `relevance` | Sort order: `relevance`, `price_asc`, `price_desc`, `popularity`, `newest`, `rating` |
| `minPrice` | integer | – | Minimum price filter in INR |
| `maxPrice` | integer | – | Maximum price filter in INR |
| `minRating` | number | – | Minimum product rating (1.0–5.0) |
| `maxItems` | integer | `20` | Maximum products to return (1–500) |

### Example: search for laptops under ₹60,000

```json
{
  "mode": "search",
  "searchQuery": "laptop",
  "maxPrice": 60000,
  "minRating": 4.0,
  "sortBy": "price_asc",
  "maxItems": 50
}
```

### Example: browse a category

```json
{
  "mode": "byCategory",
  "categoryUrl": "https://www.flipkart.com/laptops/pr?sid=6bo%2Cb5g",
  "sortBy": "popularity",
  "maxItems": 100
}
```

### Example: fetch specific product URLs

```json
{
  "mode": "byUrl",
  "startUrls": [
    {"url": "https://www.flipkart.com/asus-expertbook-laptop/p/itm0af4b?pid=COMH8Z2Q"},
    {"url": "https://www.flipkart.com/samsung-galaxy-s24/p/itm123?pid=SMSG123"}
  ]
}
```

### Example: top-rated smartphones under ₹30,000

```json
{
  "mode": "search",
  "searchQuery": "smartphone",
  "maxPrice": 30000,
  "minRating": 4.2,
  "sortBy": "rating",
  "maxItems": 30
}
```

## Use cases

- **Repricing and price tracking** — re-run the same search or product list on a schedule to catch price and discount changes
- **Brand and category benchmarking** — pull a category URL to compare ratings and pricing across competing brands
- **Deal discovery** — sort by discount or price and filter by minimum rating to surface genuinely good offers
- **Spec-sheet collection** — build a database of key specs (RAM, storage, processor, etc.) for a product line
- **Seller landscape mapping** — see which sellers list the top-rated products for a given search term
- **Catalog gap analysis** — compare your own product catalog against what's currently listed on Flipkart

## FAQ

**Does this actor cover all of Flipkart's catalog?**
It covers whatever your search query, category URL or product links return — Flipkart itself decides how many results exist for a given query or category.

**What currency are prices in?**
Indian Rupees (INR) only, since that's the only currency Flipkart lists in. The `currency` field on every record confirms this.

**Why might some products be missing `originalPrice` or `discountPercent`?**
If a product is not currently on sale (i.e., the sale price equals the original MRP), these fields are omitted. Only products with an active discount show these fields.

**How many results can I get per run?**
Set `maxItems` up to 500. Flipkart shows approximately 5–24 products per page depending on the category; the actor paginates automatically.

**Can I filter products by specific brands?**
Use the `searchQuery` to include brand names (e.g., `"Samsung 4K TV"` or `"Apple iPhone"`). Category URLs from Flipkart may also include brand filter parameters that the actor will preserve.

**Why does the `keySpecs` field have multiple values?**
Flipkart provides 3–5 key specifications per product (processor type, RAM, storage, OS, display size, etc.) as a quick summary. These are stored as an array of strings.

**Does this actor require cookies or login?**
No. This actor scrapes Flipkart's public product listings without any authentication.

**Is this actor affiliated with Flipkart?**
No. This is an independent third-party scraper that uses Flipkart's public website. It is not affiliated with, endorsed by, or connected to Flipkart Internet Private Limited or Walmart Inc.
