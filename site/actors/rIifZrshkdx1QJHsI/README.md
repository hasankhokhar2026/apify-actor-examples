# Freelancer.com Project Budget & Bids Scraper

Freelancer.com publishes project budgets, bid activity, skills and deadlines on every listing. This actor turns that into a structured dataset you can filter, sort and export. Search by keyword, browse a skill/category page, or paste project URLs and ids. It returns the budget in the project's own currency and in USD, the bid count, an optional full bid list with bidder details, the required skills, the employer's public rating and verification flags, and the posting and closing dates. No login, cookies or proxy setup is required.

## What this actor does

- **Three ways to find projects:** keyword search, category/skill browse, or direct project URL/id lookup. Auto-detect picks the right one from the fields you fill in.
- **Fixed and hourly projects:** budgets stay separate, with native-currency and USD values on every record.
- **Real filters:** project type, budget range, skills, languages, bid-count range and posting-date range.
- **Bid intelligence:** bid count and average bid always; an optional full bid list with bidder username, country, amount, delivery period and proposal text.
- **Employer context:** country, city, rating, review count, member-since date and payment/email/phone verification flags when the public project page publishes them.
- **Closed projects:** search them with `includeClosed`, or fetch any closed project directly by URL or id.
- **Clean output:** empty fields are omitted at every depth, so you never have to defend against `null`.

## Output per project

- `projectId` — Freelancer project id
- `title`, `pageTitle`, `slug` — project title, page title and URL slug
- `sourceUrl`, `canonicalUrl` — where the project was found and its canonical project URL
- `status`, `subStatus`, `frontendStatus` — project status as published
- `projectType` — `fixed` or `hourly`
- `budget` — fixed-price budget display string, e.g. `$250-750 USD`
- `budgetMinMax` — fixed budget as `{min, max, currency}`
- `budgetUsdMin`, `budgetUsdMax` — fixed budget converted to USD
- `hourlyRate` — hourly rate display string, e.g. `$15-30 USD / hr`
- `hourlyRateMinMax` — hourly rate as `{min, max, currency}`
- `hourlyRateUsdMin`, `hourlyRateUsdMax` — hourly rate converted to USD
- `currency`, `currencySymbol` — project currency
- `paymentType` — fixed-price or hourly label from the page
- `bidCount` — number of bids received
- `averageBid` — average bid in the project's currency
- `averageBidUsd` — average bid converted to USD
- `bids` — individual bids when `includeBids` is enabled: bidder id, username, display name, country, city, registration date, hourly rate, rating, review count, amount, currency, delivery period, proposal, submitted date, rank, milestone percentage and sealed flag
- `description` — full project brief
- `skills` — skill names attached to the project
- `skillSlugs`, `skillIds`, `categories` — skill slugs, numeric ids and top-level categories
- `employer` — public client details: country, country code, city, rating, review count, member-since date and verification flags
- `postedAt`, `updatedAt`, `endsAt`, `latestActivityAt` — ISO 8601 dates
- `bidPeriodDays`, `daysLeft` — bidding window and days remaining
- `postedText` — relative posting text from the project page, when available
- `hourlyCommitmentHours`, `hourlyCommitmentInterval`, `hourlyDuration` — hourly project commitment
- `isFeatured`, `isUrgent`, `isNda`, `isSealed`, `isNonpublic`, `isFulltime`, `isLocal`, `isProjectManagement`, `isRecruiter` — project flags
- `projectCountry`, `projectCity` — published project location, when available
- `marketplaceRating`, `marketplaceReviewCount`, `marketplaceDescription` — marketplace rating block when the page carries it
- `recordType: "project"`, `scrapedAt` — record type and scrape timestamp

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `auto` | `auto`, `search`, `byProject` or `byCategory` |
| `query` | string | `python` | Keyword for `mode=search` |
| `projectUrls` | array | `[]` | Project URLs, paths or numeric ids for `mode=byProject` |
| `categoryUrls` | array | `[]` | `/jobs/<skill>/` URLs or skill slugs for `mode=byCategory` |
| `projectType` | string | `any` | `any`, `fixed` or `hourly` |
| `budgetMin` | integer | `0` | Minimum fixed budget or hourly rate in USD; `0` = no minimum |
| `budgetMax` | integer | `0` | Maximum fixed budget or hourly rate in USD; `0` = no maximum |
| `minBidCount` | integer | `0` | Minimum number of bids; `0` = no minimum |
| `maxBidCount` | integer | `0` | Maximum number of bids; `0` = no maximum |
| `skills` | array | `[]` | Skill names, slugs or numeric ids |
| `languages` | array | `[]` | ISO 639-1 language codes, e.g. `en`, `de`, `hi` |
| `postedAfter` | string | – | ISO date/datetime lower bound on posting time |
| `postedBefore` | string | – | ISO date/datetime upper bound on posting time |
| `includeClosed` | boolean | `false` | Include closed projects in search/category results |
| `includeDetails` | boolean | `true` | Fetch the public project page for employer details and page text. When off, a project URL is still resolved to its id, but page-only fields are omitted |
| `includeBids` | boolean | `false` | Fetch individual bids |
| `maxBidsPerProject` | integer | `20` | Maximum bids returned per project (1–1000) |
| `sortBy` | string | `latest` | `latest`, `ending_soon`, `lowest_budget`, `highest_budget`, `lowest_bids` or `highest_bids`; ending-soon and budget sorts order the collected pool |
| `maxPages` | integer | `5` | Maximum listing pages (99 projects per page) |
| `maxItems` | integer | `50` | Hard cap on emitted projects (1–10000) |

### Example: keyword search with a fixed budget

```json
{
  "mode": "search",
  "query": "python",
  "projectType": "fixed",
  "budgetMin": 250,
  "budgetMax": 1500,
  "languages": ["en"],
  "maxItems": 100
}
```

### Example: hourly projects with low competition

```json
{
  "mode": "search",
  "query": "react",
  "projectType": "hourly",
  "budgetMin": 20,
  "budgetMax": 80,
  "maxBidCount": 10,
  "sortBy": "lowest_bids",
  "maxItems": 50
}
```

### Example: browse a skill page and include bids

```json
{
  "mode": "byCategory",
  "categoryUrls": ["https://www.freelancer.com/jobs/logo-design/"],
  "includeBids": true,
  "maxBidsPerProject": 10,
  "maxItems": 25
}
```

### Example: fetch specific projects, including a closed one

```json
{
  "mode": "byProject",
  "projectUrls": [
    "https://www.freelancer.com/projects/python/cricket-prediction-rewards-bot",
    "40425363"
  ],
  "includeDetails": true,
  "includeBids": true,
  "maxBidsPerProject": 20
}
```

## Use cases

- **Freelance demand monitoring** — track project volume and budgets across skills and categories
- **Pricing research** — compare fixed budgets and hourly rates across currencies in USD
- **Bid-competition analysis** — find low-bid, high-budget projects and inspect who is bidding
- **Employer intelligence** — see client country, rating, reviews and verification flags before bidding
- **Market and trend research** — export project descriptions, skills and posting dates for analysis
- **Opportunity alerts** — schedule keyword or category searches and filter by budget, bids and age

## FAQ

**Do I need a Freelancer.com account, cookies or a proxy?**
No. The actor reads public project data and runs without login, cookies or proxy setup. It chooses a working connection automatically.

**Why is the employer missing from some records?**
Freelancer publishes the client's country, rating, reviews, member-since date and verification flags on many project pages, but not all. Closed-project pages in particular can be served in a reduced form without the client block. The actor returns the employer object when the public page carries it and omits it when it does not. The employer's username and hire rate are not public.

**What does `includeDetails` change?**
The actor always reads the public project API for the title, budget, skills, dates and bid counts. `includeDetails` adds one project-page request for employer details, the page title and the relative posting text. When it is off, a project URL is still resolved to its project id, but those page-only fields are omitted.

**How many bids can I get per project?**
`bidCount` and `averageBid` are always included. Set `includeBids` to true to get individual bids; `maxBidsPerProject` controls how many. Some projects hide their bid list from public view, so you may get the count without individual bids. Some bidders also leave the proposal text blank, so that field can be absent on an individual bid.

**Why do some bids show an amount of 0?**
Freelancer hides the amount and proposal for sealed bids. Those bids carry `sealed: true`; the zero amount is the source's placeholder, not a real bid of zero. Visible bids keep their real amount.

**Why don't closed projects appear first when `includeClosed` is on?**
The closed archive is much older and larger than the active listing, so a broad keyword returns matching active projects first and reaches closed ones only after several pages. Use a keyword or category that identifies the closed project, or pass its URL/id directly; direct project lookup always includes closed projects.

**What is the difference between `budget` and `hourlyRate`?**
Fixed-price projects use `budget`; hourly projects use `hourlyRate`. For hourly projects the numbers are a rate per hour, not a total. `projectType` tells you which one applies.

**Are budgets converted to USD?**
Yes. `budgetMinMax` and `hourlyRateMinMax` keep the project's own currency, while `budgetUsdMin`, `budgetUsdMax`, `hourlyRateUsdMin`, `hourlyRateUsdMax` and `averageBidUsd` are converted to USD. Filters use USD.

**Can I search closed projects?**
Yes. Set `includeClosed` to true in search or category mode. Direct project URLs and ids work for closed projects without any extra setting.

**Why do I get fewer rows than `maxItems`?**
A restrictive filter can run out of matches within `maxPages`. Increase `maxPages` or narrow the keyword/category. One keyword returns at most about 5,000 active projects.

**Why are some fields missing from a record?**
The source does not publish every field for every project. Empty values are omitted instead of being sent as `null`, `""` or `[]`. This is normal for optional fields such as employer details, hourly commitment or marketplace rating.

**How fresh is the data?**
Each run reads the live project listing. Bid counts and statuses can change quickly; `scrapedAt` records when the row was collected.

**Is this affiliated with Freelancer.com?**
No. This is an independent, third-party actor that reads public Freelancer.com project data. It is not affiliated with or endorsed by Freelancer.com.
