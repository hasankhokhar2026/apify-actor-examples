# Freelancer.com Project Budget & Bids Scraper

Freelancer.com lists its project budgets, bid counts and deadlines right on the listing page, but pulling that into a spreadsheet means visiting each project one at a time. This actor collects it in bulk — starting from a direct project link, a search keyword, a category page, or a user's list of posted projects — and returns the budget, bids, skills and description for each one.

## What this actor does

- **Four ways to find projects**: direct project URLs, search keywords, category-listing URLs, or a user profile's posted projects — combine any of them in one run
- **Normalizes budget and hourly rate** into both the display string (e.g. `$250-750 USD`) and a numeric `{min, max, currency}` object for sorting and filtering
- **Filters by project type and bid count**, and sorts search/category results by budget or bid count
- **Crawls multiple pages** per search, category or user URL up to the limit you set
- Fields a project page doesn't carry (such as `marketplaceRating` on a listing with no reviews) are left out of that record rather than sent empty

## Output per project

- `title`, `pageTitle`, `slug` — project title, full page title, and URL slug
- `projectId` — Freelancer's internal project ID
- `status` — project status as shown on the page
- `budget` — fixed-price budget as a display string, e.g. `$250-750 USD`
- `budgetMinMax` — the same budget as `{min, max, currency}`
- `hourlyRate` — hourly rate as a display string, e.g. `$15-30 USD / hr`
- `hourlyRateMinMax` — the same hourly rate as `{min, max, currency}`
- `paymentType` — fixed-price or hourly, as labeled on the page
- `averageBid` — average bid amount (whole number when the source value is whole, decimal otherwise)
- `bidCount` — number of bids received
- `daysLeft` — days remaining to bid
- `postedText` — how long ago the project was posted, as shown on the page
- `description` — full project description
- `skills` — list of skill tags attached to the project (up to 20)
- `marketplaceRating`, `marketplaceReviewCount`, `marketplaceDescription` — the posting employer's marketplace rating, review count and description, when shown
- `sourceUrl`, `canonicalUrl` — the URL the project was found at, and its canonical project URL
- `recordType`, `scrapedAt` — record type tag and ISO 8601 scrape timestamp

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `projectUrls` | array | `["https://www.freelancer.com/projects/python/cricket-prediction-rewards-bot"]` | Direct Freelancer project URLs. |
| `searchQueries` | array | `[]` | Keywords to search as Freelancer job listings, e.g. `python`, `react`, `nodejs`. |
| `categoryUrls` | array | `[]` | Freelancer listing URLs, e.g. `https://www.freelancer.com/jobs/python/`. |
| `userUrls` | array | `[]` | Freelancer user/employer profile URLs; the actor scrapes the public projects that user posted. |
| `projectType` | string | `any` | `any`, `fixed` (fixed-price only) or `hourly` (hourly only). |
| `sortBy` | string | `latest` | `latest`, `lowest_budget`, `highest_budget`, `lowest_bids` or `highest_bids` — applied to search/category/user results. |
| `minBidCount` | integer | `0` | Drop projects with fewer than this many bids. |
| `searchPages` | integer | `1` | Pages to crawl per search query, category or user URL (1–10). |
| `maxItems` | integer | `25` | Hard cap on emitted projects (1–500). |
| `useProxy` | boolean | `false` | Route requests through Apify proxy; usually unnecessary since Freelancer.com is normally reachable directly. |
| `autoEscalateOnBlock` | boolean | `true` | Retry a blocked request through a different proxy automatically. |
| `proxyConfiguration` | object | `{}` | Advanced Apify proxy configuration, used only when `useProxy` is enabled. |

### Example: search by keyword

```json
{
    "searchQueries": ["python", "react native"],
    "projectType": "fixed",
    "sortBy": "highest_budget",
    "maxItems": 50
}
```

### Example: a category page, hourly projects with bids

```json
{
    "categoryUrls": ["https://www.freelancer.com/jobs/python/"],
    "projectType": "hourly",
    "minBidCount": 5,
    "searchPages": 3,
    "maxItems": 100
}
```

### Example: projects posted by one employer

```json
{
    "userUrls": ["https://www.freelancer.com/u/exampleuser"],
    "searchPages": 2,
    "maxItems": 40
}
```

## Use cases

- **Freelance demand monitoring** — track how many projects post in a skill category over time
- **Pricing research** — compare typical budgets and hourly rates for a given skill set
- **Bid-competition analysis** — use `bidCount` and `sortBy` to find under-bid, high-budget opportunities
- **Employer intelligence** — pull every public project a specific client has posted via `userUrls`
- **Market trend tracking** — watch how project volume and pricing shift across categories

## FAQ

**Why does sorting by highest budget mix different currencies?**
Freelancer's own listing endpoint sorts by raw numeric budget without converting currencies, so a large-number project in one currency can outrank a smaller-number project in another even if the second is worth more in USD. This actor preserves Freelancer's own order rather than re-ranking client-side; append `currency=USD` (or another ISO code) to your category URL if you need a single-currency view.

**How do I sort or filter by budget locally after scraping?**
Use `budgetMinMax` or `hourlyRateMinMax` — both carry numeric `min`, `max` and `currency` fields, while `budget`/`hourlyRate` stay as the original display strings.

**Do I need a proxy to run this?**
No. Freelancer.com is normally reachable directly; `useProxy` and `autoEscalateOnBlock` exist as fallbacks in case you see empty pages.

**Can I combine project URLs, search queries, category URLs and user URLs in one run?**
Yes — all four input types are processed together when provided.

**Why might `marketplaceRating` be missing from a project?**
That field only appears when the posting employer has a visible marketplace rating on the page; new or unrated accounts won't have one to extract.

**Is this affiliated with Freelancer.com?**
No, this is an independent, third-party actor that reads Freelancer.com's public project pages. It is not affiliated with or endorsed by Freelancer Technology Pty Limited.
