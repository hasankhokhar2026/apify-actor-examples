# M.Video Russia Electronics Product & Review Scraper

Scrape **mvideo.ru**, one of Russia's largest electronics and appliance retailers, without cookies, logins, or proxy setup. Search the full catalog, browse any category with live brand / condition / price filters, pull complete product detail with seller and store availability, and export customer reviews — all for a chosen Russian city.

## What this actor does

- **Four modes:** `search`, `byCategory`, `productDetails`, `reviews`
- **Full pagination** — search walks every result page (about 2,100+ unique TV listings across ~38 pages at test time), de-duplicated by product ID
- **Live facets** — brand, seller, condition and parallel-import filters are resolved from each response, so the actor uses the IDs the site is actually serving instead of stale hardcoded values
- **City-aware availability** — stock status, pickup stores and delivery dates follow the city you choose (Москва, Санкт-Петербург, Владивосток, Казань, Екатеринбург, Новосибирск and others)
- **Product detail** — prices, promo discounts, bonus rubles, rating, specifications, images, breadcrumbs, similar SKUs, seller/buybox and other marketplace offers
- **Store stock** — optional per-store pickup list with address, metro, coordinates, quantity and schedule
- **Customer reviews** — paginated review export with rating, text, pros/cons, photos, replies and likes; product detail adds the star histogram
- **Empty fields are omitted** — no `null` placeholders anywhere in a record

## Output per product (`recordType: "product"`)

- `productId`, `name`, `modelName`, `brandName`, `brandId`
- `productUrl`, `sourceUrl`
- `categoryId`, `categoryName`, `breadcrumbs[]`, `breadcrumbPath[]` (`{name, categoryId}`)
- `salePrice`, `basePrice`, `promoPrice`, `discountPercent`, `discountAmount`, `discounts[]`, `bonusAmount`, `currency`
- `ratingStar`, `ratingCount`, `totalRating`, `ratingsStats`, `ratingBreakdown`, `reviewsTotal`, `reviews[]`
- `inStock`, `soldOut`, `availabilityStatus`, `availabilityDate`, `storeOnly`, `isPrepayment`, `showcase`, `isPreorder`, `isLastChance`, `isNew`
- `condition`, `productType`, `materialSource`
- `description`, `specifications[]`, `weightKg`, `imageUrl`, `imageUrls[]`, `videos[]`, `images3d[]`, `certificates[]`, `instructions[]`
- `seller` (`{id, name, legalName, inn, ogrn, address, phone, rating, orders, reviews}`), `multiofferCount`, `otherOffers[]`, `similarProducts[]`
- `deliveryDate`, `stockLocation`, `hasExpressDelivery`, `prepaidOnly`
- `stores[]` (`{storeId, name, address, metro, lat, lng, quantity, availabilityDate, schedule, isAllDay}`), `storeCount`, `storeQuantity`
- `cityId`, `cityName`, `regionId`
- `position`, `query`, `source`, `recordType`, `scrapedAt`

Listing modes (`search`, `byCategory`) return the identity, price, stock, rating and image fields available in the catalog response. Detail enrichment (specifications, seller, stores, reviews) is produced by `productDetails`.

## Output per review (`recordType: "review"`, mode = `reviews`)

- `reviewId`, `productId`, `productUrl`
- `rating`, `author`, `date`
- `text`, `pros`, `cons`
- `photos[]`, `responses[]`
- `likes`, `dislikes`, `isPopular`
- `recordType`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `byCategory` / `productDetails` / `reviews` |
| `searchQuery` | string | `телевизор` | Free-text query (mode=search) |
| `city` | string | `Москва` | City name or mvideo city ID; controls stock, stores and delivery |
| `category` | string (select) | `""` | Top-level category (mode=byCategory) |
| `categoryUrl` | string | – | Any category URL or slug/ID; overrides `category` |
| `productUrls` | array | `[]` | Product URLs or numeric IDs (mode=productDetails / reviews) |
| `brands` | array | `[]` | Brand names or slugs, e.g. `Samsung`, `lg` |
| `sellers` | array | `[]` | Seller names or slugs, e.g. `BQ.ru`, `bqru` (mode=byCategory; search has no seller facet) |
| `minPrice` / `maxPrice` | integer | – | Sale-price range in RUB |
| `minRating` | number | – | Minimum rating (0–5); unrated products are excluded when set |
| `minDiscount` | integer | – | Minimum discount percent (0–99) |
| `condition` | string | `any` | `any` / `new` / `refurbished` / `used` / `markdown` / `showcase` (search / category; resolved from the live facet) |
| `fromAbroad` | boolean | `false` | Parallel-import listings only (mode=search) |
| `sortOrder` | string | `popularity` | `popularity` / `priceAsc` / `priceDesc` |
| `maxItems` | integer | `100` | Hard cap on emitted records (0–10,000; `0` = all, capped at 10,000) |
| `maxReviews` | integer | `20` | Reviews per product (0–200; 20 per page) |
| `includeStoreStock` | boolean | `false` | Attach `stores[]` in mode=productDetails |
| `storeLimit` | integer | `20` | Maximum stores per product |
| `includeOtherOffers` | boolean | `true` | Attach `otherOffers[]` in mode=productDetails |
| `failOnEmpty` | boolean | `false` | Mark the run failed when zero records are emitted |
| `proxyConfiguration` | object | automatic | Optional; the actor connects directly first and escalates only if blocked |

### Example: search with filters

```json
{
  "mode": "search",
  "searchQuery": "телевизор",
  "city": "Москва",
  "brands": ["Samsung", "LG"],
  "minPrice": 30000,
  "maxPrice": 90000,
  "condition": "new",
  "sortOrder": "priceAsc",
  "maxItems": 200
}
```

### Example: browse a category, used or refurbished only

```json
{
  "mode": "byCategory",
  "categoryUrl": "https://www.mvideo.ru/televizory-i-cifrovoe-tv-1/televizory-65",
  "city": "Санкт-Петербург",
  "condition": "refurbished",
  "minDiscount": 10,
  "maxItems": 100
}
```

### Example: full detail with stores and seller offers

```json
{
  "mode": "productDetails",
  "productUrls": [
    "https://www.mvideo.ru/products/televizor-general-electronics-ge55lqs2-401211841",
    "402415077"
  ],
  "city": "Москва",
  "maxReviews": 20,
  "includeStoreStock": true,
  "includeOtherOffers": true
}
```

### Example: export reviews

```json
{
  "mode": "reviews",
  "productUrls": ["400205087"],
  "maxReviews": 200,
  "maxItems": 200
}
```

## Use cases

- **Price monitoring** — track sale prices, promo discounts and bonus rubles across a category
- **Assortment research** — compare brand and seller coverage in Russian electronics retail
- **Catalog enrichment** — pull specifications, images and breadcrumbs for a known SKU list
- **Availability intelligence** — monitor stock and pickup stores by city for selected products
- **Review analytics** — export review text, pros/cons and star distributions for sentiment analysis
- **Marketplace seller tracking** — compare the buybox seller and other offers on marketplace listings

## FAQ

**Do I need cookies, a login, or a proxy?** No. Catalog, product detail and reviews are read from mvideo.ru's public endpoints without an account. The actor connects directly first; if the site temporarily rate-limits a detail or review request, it retries and falls back to a real browser session, and only then to a different Apify Proxy route. If every HTTP route is blocked, it can continue in a browser-only session. You do not configure anything.

**Why does the city matter?** mvideo.ru serves city-specific stock, pickup stores and delivery dates. In testing, catalog prices for fixed products did not differ between cities, so treat the city setting as an availability selector rather than a price-comparison tool.

**How many search results can I get?** Search pages through the source's own cursor. At the time of testing, `телевизор` declared 2,253 results across 38 pages and yielded 2,125 unique products; the source itself does not surface a small number of advertised or duplicate rows. Set `maxItems` to the number you need.

**Why are some fields missing on some products?** Empty fields are omitted. Marketplace rows may lack a description, an M.Video-owned product has no third-party seller, and not every SKU has a rating, discount, store stock or video.

**Are videos and 3D images included?** The fields exist and are filled when mvideo.ru returns them, but most products have none. The actor does not promise video or 3D content.

**What does `condition` guarantee?** The filter is applied through the site's live condition facet. Refurbished and markdown items can be recognized from the product name; marketplace "used" listings do not always expose a machine-readable condition, so treat the echoed condition as the filter you requested, not a per-row certification.

**Can I sort by rating, newest, or discount?** No. Popularity and sale-price ordering are supported. For `priceAsc` / `priceDesc`, the actor sorts the emitted rows by sale price because the source's own ordering is approximate. `minRating` and `minDiscount` are applied as filters instead.

**Why is there no "in stock only" toggle?** In validation, every sampled catalog listing was marked available, so the toggle was a no-op. Use the `inStock` / `soldOut` fields in the output if you need to filter downstream.

**How many reviews can I fetch?** The source serves 20 reviews per page with no login wall. `maxReviews` controls the per-product cap (up to 200); `maxItems` caps the total rows in `reviews` mode.

**Are review filters or date sorting supported?** No. The review list supports useful/rating ordering; the undocumented review filters returned empty results in testing, so they are not exposed.

**Why did a brand or seller filter stop the run?** Filter facets are resolved from the live response. If a requested brand, seller, condition or parallel-import facet is not present for that query or category, the actor stops with a clear message rather than silently returning unfiltered results. Remove that filter or try a broader query/category.

**How fresh is the data?** Every run reads current catalog, price, stock and review data directly from mvideo.ru.

**Is this actor affiliated with mvideo.ru?** No. It is an independent, third-party actor that reads publicly reachable product data. It is not affiliated with, endorsed by, or operated by M.Video.
