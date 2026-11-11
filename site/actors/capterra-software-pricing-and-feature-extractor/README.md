# Capterra Software Pricing & Feature Extractor

Turn Capterra software pages into structured JSON: pricing plans and starting prices, the full feature and integration catalog, alternatives, FAQs, screenshots and videos, ratings with sub-scores and star distribution, review sentiment and topics, reviewer firmographics, and the reviews themselves with pros, cons and vendor replies.

Paste product page URLs, type product or category names, or point it at a ranked category listing. No login, cookies, API key, or proxy setup is required.

## What this actor does

- **Full product profile** - name, description, overview, logo, primary category, all use-case categories, last-updated date
- **Pricing** - starting price with currency and period, pricing model, free-trial and free-version flags, and every published plan with its included features (or "contact vendor" pricing)
- **Features** - every feature Capterra lists, plus per-feature quality rating, review count, importance percentage and a review-based description where Capterra publishes them
- **Integrations** - the complete integration list with product links, logos and review counts, plus the total count
- **Ratings** - overall rating and review count, ease-of-use / value-for-money / customer-support / functionality sub-ratings, 1-5 star distribution, recommendation percentage, review sentiment percentages and mentioned topics
- **Reviews** - reviewer name, job title, industry, company size and time using the product; overall and sub-ratings; recommendation score; pros, cons and comments; verified and incentive flags; vendor responses
- **Market context** - alternatives with ratings and prices, FAQs, awards, reviewer company-size / industry / job-function breakdowns
- **Media** - screenshot URLs and product video URLs

Every record has `sourceUrl`, `recordType` and `scrapedAt`. A field Capterra does not publish for a product is left out of that record - never emitted as `null`, an empty string, a zero or a placeholder.

## Output per product

- **Identity:** `productId`, `slug`, `name`, `url`, `sourceUrl`, `reviewsUrl`, `siteName`, `recordType`, `scrapedAt`
- **Profile:** `description`, `overview`, `logo`, `primaryCategory`, `categories[]`, `categorySlugs[]`, `lastUpdated`
- **Ratings:** `rating`, `reviewCount`, `ratingBreakdown` (`easeOfUse`, `valueForMoney`, `customerSupport` - each with `rating` and `reviewCount`), `ratingDistribution` (stars `1`-`5`), `reviewSentiment` (`positivePercent`, `neutralPercent`, `negativePercent`), `companySizeBreakdown` (`smallBusinessPercent`, `midsizePercent`, `enterprisePercent`), `topIndustries[]` and `topJobFunctions[]` (`name`, `percent`)
- **Pricing:** `startingPrice`, `priceCurrency`, `pricePeriodicity`, `pricingModel`, `freeTrial`, `freeVersion`, `pricingPlans[]` (`name`, `price`, `priceFormatted`, `priceCurrency`, `pricePeriodicity`, `pricingModel`, `startingPrice`, `attributes`)
- **Features and integrations:** `featureCount`, `features[]`, `featureDetails[]` (`name`, `description`, `rating`, `reviewCount`, `importancePercent`), `integrationsCount`, `integrations[]`, `integrationDetails[]` (`name`, `url`, `logo`, `productId`, `reviewCount`)
- **Market context:** `platforms[]`, `useCases[]` (`name`, `slug`), `supportOptions[]`, `trainingOptions[]`, `typicalCustomers[]`, `awards[]` (`name`, `type`, `year`), `pros[]` and `cons[]` (`topic`, `summary`, `mentionCount`, `reviewerName`, `reviewerTitle`, `reviewerQuote`, `sentiment`, `sentimentScore`)
- **Reviews:** `reviews[]` with reviewer name, job title, industry, company size and time using the product; overall and sub-ratings; recommendation score; pros, cons and comments; verified and incentive flags; vendor responses
- **Media:** `screenshots[]`, `videos[]`

## Modes

| Mode | Input | What happens |
|---|---|---|
| `byProductUrls` (default) | `productUrls` | Scrapes each Capterra product page. Accepts full URLs, `/p/id/slug` paths and compare URLs (both sides are expanded). Regional `capterra.*` domains work. |
| `bySearchQueries` | `searchQueries` | Searches Capterra for each name or category term and scrapes the products it returns. Capterra returns up to 20 products per query. |
| `byCategoryUrls` | `categoryUrls` | Walks a ranked category listing page by page and scrapes every product, with an optional sort order. |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `byProductUrls` | Which mode to run |
| `productUrls` | array | Slack product URL | Product pages (mode=byProductUrls) |
| `searchQueries` | array | `[]` | Names or category terms (mode=bySearchQueries) |
| `categoryUrls` | array | `[]` | Category pages or slugs (mode=byCategoryUrls) |
| `sortBy` | select | `featured` | Category order: featured, most reviews, highest rated, alphabetical |
| `maxItems` | integer | 10 | Maximum products to return (1-250) |
| `includeReviews` | boolean | true | Attach the reviews Capterra publishes on the product page |
| `maxReviews` | integer | 20 | Reviews per product (1-100) |
| `reviewSort` | select | `most_recent` | most_recent, highest_rated, lowest_rated, most_helpful |
| `minReviewRating` | integer | 0 | Keep reviews at or above this star rating (0 = no minimum) |
| `maxReviewRating` | integer | 0 | Keep reviews at or below this star rating (0 = no maximum) |
| `fetchAllReviews` | boolean | false | Walk the reviews pages for more reviews than the product page shows |
| `includeAlternatives` | boolean | true | Attach the alternatives list |
| `includeFaqs` | boolean | true | Attach the product FAQs |

### Example: several products by URL

```json
{
  "mode": "byProductUrls",
  "productUrls": [
    "https://www.capterra.com/p/135003/Slack/",
    "https://www.capterra.com/p/211559/Trello/"
  ],
  "includeReviews": true,
  "maxReviews": 10
}
```

### Example: search by name

```json
{
  "mode": "bySearchQueries",
  "searchQueries": ["project management", "CRM software"],
  "maxItems": 20
}
```

### Example: browse a category with reviews filtered to low ratings

```json
{
  "mode": "byCategoryUrls",
  "categoryUrls": ["https://www.capterra.com/team-communication-software/"],
  "sortBy": "most_reviews",
  "maxItems": 25,
  "fetchAllReviews": true,
  "maxReviews": 30,
  "maxReviewRating": 2
}
```

### Example: compare URL

```json
{
  "mode": "byProductUrls",
  "productUrls": [
    "https://www.capterra.com/compare/135003-168668/Slack-vs-Microsoft-Teams"
  ]
}
```

Both products in the compare URL are scraped as separate records.

## Output example (trimmed)

```json
{
  "productId": "135003",
  "slug": "Slack",
  "name": "Slack",
  "url": "https://www.capterra.com/p/135003/Slack/",
  "sourceUrl": "https://www.capterra.com/p/135003/Slack/",
  "reviewsUrl": "https://www.capterra.com/p/135003/Slack/reviews/",
  "siteName": "Capterra",
  "rating": 4.66,
  "reviewCount": 24266,
  "ratingBreakdown": {
    "easeOfUse": {"rating": 4.6, "reviewCount": 22799},
    "valueForMoney": {"rating": 4.5, "reviewCount": 15350},
    "customerSupport": {"rating": 4.4, "reviewCount": 13607}
  },
  "ratingDistribution": {"1": 48, "2": 129, "3": 917, "4": 5767, "5": 17405},
  "reviewSentiment": {"positivePercent": 96, "neutralPercent": 4, "negativePercent": 1},
  "startingPrice": "$8.75 / month",
  "priceCurrency": "USD",
  "pricingModel": "Per User",
  "freeTrial": true,
  "freeVersion": true,
  "primaryCategory": "Team Communication Software",
  "featureCount": 105,
  "integrationsCount": 173,
  "platforms": ["Web-Based", "Mac", "Windows", "Linux", "Android", "iPhone", "iPad"],
  "reviews": [
    {
      "reviewId": "Capterra___7215330",
      "title": "Reliable Communication and Collaboration Platform",
      "rating": 5.0,
      "date": "2026-09-18",
      "reviewerName": "Anbuselvam S.",
      "reviewerJobTitle": "LLM Trainer",
      "reviewerCompanySize": "10,001+ employees",
      "reviewerIndustry": "Information Technology and Services",
      "pros": "Slack makes day-to-day communication very easy...",
      "cons": "The number of notifications can sometimes become distracting...",
      "recommendScore": 10.0,
      "verified": true
    }
  ],
  "recordType": "software",
  "scrapedAt": "2026-11-09T17:40:00+00:00"
}
```

## Use cases

- **Competitive pricing research** - export every published plan and its included features for a set of rivals
- **Feature-gap analysis** - compare complete feature and integration catalogs side by side
- **Voice-of-customer analysis** - pull reviews with pros, cons, sub-ratings and reviewer firmographics
- **Category mapping** - enumerate a ranked category and track rating / review-count changes over time
- **Procurement shortlists** - collect alternatives, pricing, deployment options and support channels in one dataset

## FAQ

**Do I need a Capterra account, cookies or a proxy?**
No. The actor reads public pages and handles the site's bot challenge automatically. You do not configure a proxy.

**How many products can one run return?**
Up to 250. A category page lists 25 products and the actor paginates automatically. A search query returns at most 20 products because Capterra's search does not paginate; use several queries for broader coverage.

**Why is a field missing from one product?**
Capterra does not publish every field for every product. A product without listed pricing has no `startingPrice` or `pricingPlans`; a product with too few recent reviews has no firmographic breakdowns. Missing means "not published", never a made-up value.

**How many reviews can I get per product?**
The product page carries a batch of recent reviews, and `fetchAllReviews` also walks the dedicated reviews pages up to `maxReviews` (1-100). Use `minReviewRating` / `maxReviewRating` to target 1-star or 5-star reviews.

**Is the vendor profile included?**
Capterra's product pages no longer publish vendor location, website or founding year. The vendor name is included when the product was discovered through a category or search listing, where Capterra still exposes it.

**Can I use regional Capterra sites?**
Yes. Product and category URLs on `capterra.co.uk`, `capterra.in`, `capterra.com.au` and other regional domains are accepted and scraped from that domain.

**Why do non-English search terms return loosely related products?**
Search uses Capterra's own ranking on `capterra.com`. For the most relevant results use the English product or category name, or paste the product URL from the regional Capterra site instead.

**Is this affiliated with Capterra or Gartner?**
No. This is an independent tool that reads publicly available data. It is not operated by, endorsed by, or affiliated with Capterra or Gartner Digital Markets.

## Notes

- Review text is user-generated content. Use it for analysis and do not republish it in a way that misrepresents its authorship.
- Product pages, category pages and reviews pages are public; the actor does not log in or access account-only data.
- Capterra page links are public but sit behind a bot challenge, so a plain `curl`/HTTP client can receive a 403. Open page links in a normal browser.
- Logos and screenshots are served from Capterra's image CDN. Third-party hosted images that reject direct requests (for example G2's CDN) are omitted instead of being emitted as broken links. Video links point to the YouTube/Vimeo pages Capterra publishes.
