# Amazon Multi-Domain Product Price & Detail Scraper

Point this actor at an Amazon product — or a batch of them, across any mix of the 21 supported country domains — and get back pricing, ratings, seller, variant and technical detail for each. Accepts full product URLs or bare ASINs, so you can feed it either a list of links or just a list of product codes.

## What this actor does

- Scrapes any mix of Amazon country domains in a single run — `amazon.com`, `.co.uk`, `.de`, `.fr`, `.co.jp`, `.in`, and 15 others.
- Accepts full product URLs (`/dp/ASIN`) or bare 10-character ASINs, building the product URL for you when only an ASIN is given.
- Returns price, list price, stock status, star rating and review breakdown, seller details, bestseller ranks, variant data, images, description, features and technical specs for each product, plus book-specific fields when the listing is a book.
- Can set a delivery postal code before each product is read, so buy-box price and availability reflect that destination where Amazon allows it.
- Omits any field it could not populate for a given product, so you never see an empty placeholder in a record.

## Output per product

- `title` — Product title
- `url` — Product page URL
- `asin` — Amazon Standard Identification Number
- `inStock` — Whether the buy-box is currently purchasable
- `inStockText` — Raw stock availability text
- `brand` — Product brand name
- `price` — Current price (`value`, `currency`, `display`)
- `listPrice` — Original/strike-through price if discounted
- `shippingPrice` — Shipping cost, when explicitly shown (omitted for FREE shipping)
- `stars` — Average rating (0-5)
- `starsBreakdown` — Percentage of reviews per star level (`5star`...`1star`, 0.0-1.0)
- `ratingHistogram` — Per-star histogram entries (`stars`, `percent`)
- `reviewsCount` — Total number of reviews
- `answeredQuestions` — Number of answered customer questions
- `breadCrumbs` — Category path
- `thumbnailImage` — Main product image URL
- `images[]` — All product image URLs (main + alt thumbnails), max-resolution
- `description` — Product description text
- `features[]` — Bullet-point feature list
- `variantAsins[]` — Related variant product ASINs (e.g. other colors/sizes)
- `variantAttributes[]` — Variant dimensions (`dimension`, `values[]`), e.g. Color/Size
- `priceVariants` — Per-variant pricing matrix, when the page exposes one
- `reviewsLink` — URL to the full reviews page
- `delivery` — Delivery/shipping message
- `fastestDelivery` — Fastest delivery option text
- `locationText` — The delivery destination the page rendered for
- `returnPolicy` — Return policy text
- `support` — Product support text
- `seller` — Seller information (`name`, `id`, `url`, `reviewsCount`, `averageRating`)
- `bestsellerRanks[]` — Bestseller rankings (`rank`, `category`)
- `purchaseOptions[]` — Buying options (`type`: `ONE_TIME`/`SUBSCRIBE_AND_SAVE`/`USED`, `price`, `availabilityStatus`)
- `sustainabilityFeatures` — Climate Pledge Friendly / sustainability text
- `documents[]` — Manuals/guides (`label`, `url`, `mediaType`)
- `sizeChart[]` — Apparel/footwear size-chart rows, when present
- `details[]` — Grouped technical/additional/overview detail rows (`group`, `key`, `value`, `raw`)
- `customersSay` — "Customers say" AI-generated review summary + sentiment aspects
- `relatedProducts[]` — Related-product carousels (only when `includeRelatedProducts=true`)
- `productType` — `"BOOK"` when book-specific evidence (ISBN/byline) is present
- `book` — Book-specific fields (`isbn10`, `isbn13`, `authors`, `publisher`, `format`, ...)
- `manufacturer`, `modelNumber`, `weight`, `productDimensions`, `countryOfOrigin`, `dateFirstAvailable`, `gtin`, `upc`, `isbn10`, `isbn13` — Common technical-detail fields promoted to the top level when present
- `scrapedAt` — ISO-8601 UTC timestamp when the record was scraped

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `productUrls` | array | – | Amazon product URLs to scrape (e.g., `amazon.com/dp/ASIN`). One of `productUrls`/`asins` required |
| `asins` | array | – | Bare 10-character Amazon ASINs, as an alternative/addition to `productUrls`. Builds `/dp/{ASIN}` URLs on `amazon.com` (or the first `productUrls` domain, if provided). Entries that aren't 10 letters/digits are skipped |
| `deliveryCountry` | string | – | Delivery country label. Currently it has no effect on its own: only `postalCode` changes the delivery destination |
| `postalCode` | string | – | Best-effort ZIP/postal code to set as the delivery destination before each product is scraped; affects buy-box availability/price for some products |
| `includeRelatedProducts` | boolean | `false` | Include a best-effort `relatedProducts[]` array (Frequently Bought Together / From the Brand / Similar items) on each record |
| `proxyConfiguration` | object | `{"useApifyProxy": true}` | Apify Proxy configuration. Defaults to Apify Proxy's automatic selection; if a product comes back blocked or nearly empty, the actor switches that domain's session to a residential proxy and retries. Choosing specific proxy groups yourself turns that switch off |
| `proxyCountry` | string | `AUTO` | Proxy country for geo-targeting (21 countries or `AUTO`). `AUTO` picks the country that matches each Amazon domain |
| `rateLimitDelay` | integer | `2` | Base pause between products in seconds (1-30); each pause is a random value between this and twice this |

### Example: single product

```json
{
  "productUrls": ["https://www.amazon.com/dp/B09X7MPX8L"]
}
```

### Example: bare ASINs (no full URL needed)

```json
{
  "asins": ["B09X7MPX8L", "B08H75RTZ8"]
}
```

### Example: multiple domains in one run

```json
{
  "productUrls": [
    "https://www.amazon.com/dp/B09X7MPX8L",
    "https://www.amazon.co.uk/dp/B09X7MPX8L",
    "https://www.amazon.de/dp/B09X7MPX8L"
  ]
}
```

### Example: delivery destination + related products

```json
{
  "productUrls": ["https://www.amazon.com/dp/B09X7MPX8L"],
  "postalCode": "10001",
  "includeRelatedProducts": true
}
```

## Use cases

- **Price monitoring** — track price, list price, and stock status across your catalog or competitors' listings
- **Market research** — compare ratings, review counts, and bestseller ranks across products and categories
- **Catalog enrichment** — pull images, descriptions, features, and technical details to populate your own product database
- **Repricing tools** — feed buy-box price/availability by delivery destination into a repricing engine
- **Review/reputation tracking** — monitor star ratings, rating breakdowns, and "Customers say" sentiment over time
- **Cross-marketplace comparison** — scrape the same ASIN across multiple country domains to compare pricing and availability

## FAQ

**Which Amazon domains are supported?**
21 country domains: amazon.com, .co.uk, .de, .fr, .es, .it, .ca, .com.au, .co.jp, .in, .com.br, .com.mx, .nl, .se, .pl, .com.tr, .ae, .sa, .sg, .com.be, .eg. Mix domains freely in one run; the actor processes URLs domain by domain, each with a proxy from the matching country unless you set `proxyCountry`. URLs from other domains, and Amazon search or category pages, are skipped.

**Do I need to configure the proxy myself?**
No. `proxyConfiguration` defaults to Apify Proxy's automatic selection, and the actor moves a domain to a residential proxy by itself when it detects a block. Change it only if you want to force a specific proxy group.

**What happens if a product page can't be reached?**
That ASIN is skipped and logged without a dataset row, and the run continues with the remaining URLs — one blocked or missing product doesn't stop the batch. The same ASIN listed twice is scraped once.

**Can I scrape by ASIN instead of a full URL?**
Yes — use the `asins` input field with bare 10-character ASINs; the actor builds the `/dp/{ASIN}` URL for you (on `amazon.com`, or the domain of the first `productUrls` entry if both are supplied).

**Why is a field missing from some records?**
Empty/null fields are dropped at push time, so the dataset only carries fields that were actually populated for a given product. Fields like `priceVariants`, `sizeChart`, and `book` only appear on products that actually carry that kind of data (a variant matrix, an apparel size chart, a book listing).

**Does `deliveryCountry`/`postalCode` always change the result?**
No. Only `postalCode` is applied, and only on a best-effort basis: when Amazon doesn't offer a settable delivery location for that page, the product is still scraped using the proxy's own default location (shown in `locationText`).

**Is this affiliated with Amazon?**
No, this is a third-party actor that scrapes publicly available Amazon product pages. It is not affiliated with, endorsed by, or sponsored by Amazon.com, Inc.
