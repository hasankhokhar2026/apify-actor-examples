# Amazon Multi-Domain Product Price & Detail Scraper

Scrape **Amazon** products and discovery lists across 21 country marketplaces. Give it product URLs or ASINs and get back price, coupon, deal badges, rating, review count, bestseller rank, seller and buy-box details, offers, availability, variants, images, videos, specs, A+ text, and public top-review snippets. You can also start from keyword terms, full search URLs, or bestseller list URLs. No login, cookies, or API key is needed.

## What this actor does

- **Products by URL or ASIN** across `amazon.com`, `.co.uk`, `.de`, `.fr`, `.it`, `.es`, `.ca`, `.com.au`, `.co.jp`, `.in`, `.com.br`, `.com.mx`, `.nl`, `.se`, `.pl`, `.com.tr`, `.ae`, `.sa`, `.sg`, `.com.be`, and `.eg`.
- **Discovery by keyword, search URL, or bestseller list** with price, rating, deal, condition, and sort filters on keyword searches.
- **Locale-aware output**: marketplace language, display currency, delivery ZIP, and the rendered `locationText` are carried on every record.
- **Commercial fields**: coupon, deal badge, status badges, bought-past-month, list price, discount percent, offer count, and lowest offer.
- **Explicit failure rows** with a reason code instead of silently dropping an input.
- Empty fields are omitted from each record.

## Output per product

- `recordType` - `product`, `searchResult`, `bestseller`, or `error`
- `asin`, `parentAsin`, `title`, `brand`, `url`, `marketplace`, `status`, `warnings[]`
- `price` (`value`, `currency`, `display`), `listPrice`, `currency`, `discountPercent`, `onSale`, `savingsPercentage`
- `coupon` (`text`, `percent`, `amount`, `type`), `dealBadge`, `badges[]`
- `stars`, `reviewsCount`, `starsBreakdown`, `ratingHistogram`, `customersSay`
- `topReviews[]` - inline public snippets (`author`, `rating`, `title`, `date`, `text`, `verified`, `variant`, `helpful`)
- `boughtPastMonth` (`text`, `value`)
- `bestsellerRanks[]` (`rank`, `category`), `category`, `categories[]`
- `inStock`, `inStockText`, `availability`, `delivery`, `fastestDelivery`, `locationText`
- `seller` (`name`, `id`, `url`, `soldById`, `sellerRatingText`)
- `buybox` (`shipsFrom`, `soldBy`, `soldByAmazon`, `isFBA`)
- `offers` (`count`, `lowestPrice`), `offerCount`, `lowestOfferPrice`
- `variantAsins[]`, `variants[]` (`asin`, `isCurrent`), `variantAttributes[]`
- `images[]`, `thumbnailImage`, `videos[]`, `features[]`, `description`, `aplusText`
- `details[]`, `specifications` (`upc`, `ean`, `gtin`, `modelNumber`, dimensions, and more)
- `documents[]`, `sizeChart[]`, `returnPolicy`, `support`, `sustainabilityFeatures`
- `productType`, `book` for book listings
- `manufacturer`, `modelNumber`, `weight`, `productDimensions`, `countryOfOrigin`, `dateFirstAvailable`
- `scrapedAt` - ISO-8601 UTC timestamp

## Output per search or bestseller row

Search rows also carry `query`, `page`, `position`, `isSponsored`, and `searchUrl`. Bestseller rows carry `rank`, `listUrl`, and `listType: "bestseller"`. When `includeDetails` is on, the row is enriched with the full product fields above and `foundVia` is set.

## Output per failure

- `recordType: "error"`
- `reason` - `INVALID_INPUT`, `NOT_FOUND`, `BLOCKED_WAF`, `BLOCKED_CAPTCHA`, `UNAVAILABLE`, `NO_BUYBOX`, `PARSE_DEGRADED`, `TIMEOUT`, or `SEARCH_NO_RESULTS`
- `asin`, `url`, `marketplace`, `httpStatus`, `attempts`, `retryable`, `message`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `productUrls` | array | - | Product URLs to scrape. Any mix of supported domains |
| `asins` | array | - | Bare 10-character ASINs. Built into `/dp/` URLs |
| `searchTerms` | array | - | Keyword searches, e.g. `air fryer` |
| `searchUrls` | array | - | Full search URLs, with your own `i=`, `rh=`, and `s=` parameters |
| `bestsellerUrls` | array | - | `/zgbs/` or `/gp/bestsellers/` list URLs |
| `marketplace` | string | `auto` | Marketplace for bare ASINs and keyword terms |
| `domains` | array | - | Run ASINs and keyword terms across several marketplaces at once |
| `language` | string | `auto` | Page language, or the marketplace default |
| `currency` | string | `auto` | Display currency, or the marketplace default |
| `deliveryCountry` | string | `auto` | Country hint used to choose a representative ZIP |
| `postalCode` | string | - | Local delivery ZIP; validated against the marketplace format |
| `minPrice` / `maxPrice` | number | - | Discovery price range |
| `minRating` | string | `any` | `4`, `3`, `2`, or `1` stars and up |
| `dealsOnly` | boolean | `false` | Apply Amazon's deals filter to keyword searches |
| `primeOnly` | boolean | `false` | Apply Amazon's Prime filter to keyword searches |
| `condition` | string | `any` | `new`, `used`, `renewed`, or `collectible` |
| `brand` | string | - | Added to keyword terms and used as a title/brand post-filter |
| `stock` | string | `any` | `inStock` or `outOfStock` post-filter; unknown stock passes through |
| `sortBy` | string | `relevance` | `price-asc`, `price-desc`, `review-rank`, or `newest` |
| `maxItems` | integer | `50` | Cap on discovery rows (1-1000). Product inputs are not capped |
| `maxPages` | integer | `3` | Pages per keyword/search URL (1-20) |
| `includeDetails` | boolean | `true` | Fetch the product page for each discovery result |
| `includeSponsored` | boolean | `true` | Keep sponsored search cards; `isSponsored` is always kept |
| `includeVariants` | boolean | `true` | Include parent/child ASINs and variant dimensions |
| `includeTopReviews` | boolean | `true` | Include inline public review snippets |
| `includeFailed` | boolean | `true` | Emit error rows for failed inputs |
| `failOnEmpty` | boolean | `false` | Mark the run failed when no records are emitted |
| `rateLimitDelay` | integer | `1` | Base pause between requests (0-10 seconds) |
| `proxyConfiguration` | object | automatic | Optional proxy override; the actor works without changing it |
| `proxyCountry` | string | `AUTO` | Optional proxy exit country; `AUTO` uses each marketplace's own country |

### Example: one product

```json
{
  "asins": ["B0B8PD8TTP"],
  "postalCode": "10001"
}
```

### Example: products across three marketplaces

```json
{
  "productUrls": [
    "https://www.amazon.com/dp/B0B8PD8TTP",
    "https://www.amazon.de/dp/B008F7WGCK",
    "https://www.amazon.co.uk/dp/B09B7SB46R"
  ],
  "includeTopReviews": true,
  "includeVariants": true
}
```

### Example: keyword discovery with filters

```json
{
  "searchTerms": ["air fryer"],
  "marketplace": "amazon.com",
  "minPrice": 20,
  "maxPrice": 100,
  "minRating": "4",
  "dealsOnly": true,
  "sortBy": "price-asc",
  "maxItems": 100,
  "maxPages": 3,
  "includeDetails": true
}
```

### Example: cross-marketplace ASIN comparison and a bestseller list

```json
{
  "asins": ["B0B8PD8TTP"],
  "domains": ["amazon.com", "amazon.co.uk", "amazon.de"],
  "bestsellerUrls": ["https://www.amazon.com/gp/bestsellers/kitchen/"],
  "maxItems": 30
}
```

## Use cases

- **Price and buy-box monitoring** - track price, list price, coupon, seller, offers, and stock per marketplace
- **Catalog enrichment** - pull images, specs, variants, A+ text, and identifiers into your own catalog
- **Keyword and category research** - find products by search filters or bestseller rank, then enrich the winners
- **Cross-marketplace comparison** - run the same ASIN across several country sites in one job
- **Review and reputation tracking** - monitor star ratings, review counts, rating breakdowns, and public review snippets
- **Deal monitoring** - surface coupons, limited-time deals, and discount percentages

## FAQ

**Which marketplaces are supported?**
21 country domains: amazon.com, amazon.ca, amazon.com.mx, amazon.com.br, amazon.co.uk, amazon.de, amazon.fr, amazon.it, amazon.es, amazon.nl, amazon.com.be, amazon.se, amazon.pl, amazon.com.tr, amazon.ae, amazon.sa, amazon.eg, amazon.in, amazon.co.jp, amazon.com.au, and amazon.sg.

**Do I need cookies or an API key?**
No. Everything the actor returns comes from public Amazon pages. There is no login step and no credential input.

**Do I need to set up a proxy?**
No. The actor chooses a working connection automatically and only escalates when Amazon blocks a request. You can leave `proxyConfiguration` at its default.

**Why does the displayed price differ from the local shelf price?**
Amazon converts display currency when you request a different currency from the marketplace. The record always carries `currency` and `locationText` so you can see which currency and delivery location were used. For exact local retail pricing, keep `currency` on `auto` and set a local `postalCode`.

**Can I get Prime eligibility?**
No. The 2026 Amazon page exposes only promotional or hidden Prime icons, not a reliable per-item eligibility signal. `primeOnly` applies Amazon's own search filter, but no Prime field is emitted.

**Can I get full reviews or per-variant prices?**
No. Full review pages require a login, so only the inline public snippets are returned. Variants expose parent and child ASINs plus dimensions, but the product page does not carry per-variant prices or stock.

**Why is a field missing from a record?**
Empty values are omitted. Fields such as `coupon`, `dealBadge`, `aplusText`, `videos`, `topReviews`, and `specifications` only appear when that product or marketplace actually renders them.

**What happens to a bad ASIN or a blocked page?**
With `includeFailed` on, the actor emits an error row with a reason code and continues with the rest of the batch. A 404, a WAF challenge, and an out-of-stock product are reported as different reasons.

**Does the brand filter use Amazon's brand facets?**
No. `brand` is added to the keyword text and used as a title/brand post-filter. It is not a structured Amazon brand-ID resolver; use `searchUrls` when you already have a facet URL.

**Can I scrape category browse pages?**
Not directly. Category `/b?node=` pages do not expose product cards reliably. Use a keyword search URL with the category parameter (`/s?k=...&i=...`) or a bestseller list URL instead.

**Why are some commercial fields only best effort?**
Coupons, deal badges, bought-past-month, A+ text, videos, and top-review snippets are rendered only for some products, marketplaces, or session variants. When Amazon does not render one, the field is omitted rather than guessed.

**Is this affiliated with Amazon?**
No. This is a third-party actor that reads publicly available Amazon pages. It is not affiliated with, endorsed by, or sponsored by Amazon.
