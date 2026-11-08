# Glassdoor Review Export - Ratings, Pros, Cons & Replies

Collect employee reviews from Glassdoor companies by URL, company name, or employer id. Get the overall rating and every sub-rating, pros, cons, advice to management, reviewer job title and location, employment status, helpful votes, language, employer responses, company logo, canonical review URLs, and optional company profile data. No Glassdoor login, cookie, or proxy setup is required. The actor escalates from direct requests to Apify datacenter and residential proxies only when Glassdoor blocks the session.

## What this actor does

- Accepts one or many Glassdoor company Review or Overview URLs, company names, or employer ids.
- Reads Glassdoor's public review data through its own JSON endpoint, so it does not need a browser or a logged-in session.
- Returns every review Glassdoor serves, including beyond the roughly 200 reviews the public review page shows.
- Supports exact single or multi-star filtering, employment type(s), current employees only, employer responses only, keyword search, job-title keywords, job function, location, language selection, worldwide review coverage, a recent-date window, and client-side `dateFrom`/`dateTo` ranges.
- Keeps the 25 fields from the previous version and adds canonical review URLs, company logo, language data, employer responses, company context, and optional firmographics.
- Applies an exact post-filter when keyword and star rating are combined, because Glassdoor treats that server-side rating as a minimum, not an exact match.
- Reports a completeness contract (`saved`, `available`, `siteTotal`, `stopReason`) in the run status and in the `RUN_SUMMARY` key-value record.
- Supports incremental monitoring with `onlyNew` and a named `monitorId` state store: per-company review-id watermarks and seen sets, `isNew`/`firstSeenAt` output, optional `emitUnchanged`, and state updates only after a successful dataset push.
- Resolves company and location names with exact/unique matching. Ambiguous or invalid values produce typed warnings instead of silently taking the first autocomplete row.
- Omits fields that Glassdoor does not provide for a review instead of writing empty strings, nulls, or zero placeholders.

Typical uses: employer-brand research, culture and sentiment analysis, HR benchmarking, due diligence, recruiting research, and building review datasets for analytics.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `companies` | string list | Any (prefill: Google Reviews URL) | Glassdoor Review or Overview URLs, company names, or employer ids. Add one item per company. |
| `maxItems` | integer 1-50,000 | 100 | Maximum reviews to save across all companies. |
| `maxReviewsPerCompany` | integer 0-50,000 | 0 | Maximum reviews per company. 0 means no per-company limit. |
| `sortBy` | select | Newest first (`mostRecent`) | Newest first, most relevant, oldest first, highest rated, lowest rated, or classic relevance. |
| `location` | text | empty | City, state, metro area, or country, such as New York, NY or London. Resolved automatically through Glassdoor's location search. |
| `jobFunction` | select | Any job function | Administrative, Arts & Design, Business, Consulting, Customer Services & Support, Education, Engineering, Finance & Accounting, Healthcare, Human Resources, Information Technology, Legal, Marketing, Media & Communications, Military & Protective Services, Operations, Other, Product & Project Management, Research & Science, Retail & Food Services, Sales, Skilled Labor & Manufacturing, or Transportation. |
| `postedWithinDays` | select | Any time | Keep only reviews from the last 7, 30, 90, 180, or 365 days. Sorting is forced to newest first. |
| `dateFrom` | text | empty | Keep reviews posted on or after this date (`YYYY-MM-DD`). Applied client-side; sorting is forced to newest first. |
| `dateTo` | text | empty | Keep reviews posted on or before this date (`YYYY-MM-DD`). Applied client-side; sorting is forced to newest first. |
| `rating` | select | Any rating | Keep only reviews with an exact 1-5 star overall rating. |
| `ratings` | string list | empty | Keep reviews with any of several exact star ratings. When set, it takes precedence over `rating`. |
| `employmentType` | select | Any | Full-time (regular), part-time, intern, contract, freelance, or temporary. |
| `employmentTypes` | string list | empty | Keep reviews with any of several employment statuses. When set, it takes precedence over `employmentType`. |
| `onlyCurrentEmployees` | boolean | false | Keep only reviews from current employees. |
| `onlyWithEmployerResponses` | boolean | false | Keep only reviews that have an official employer response. |
| `jobTitleKeywords` | text | empty | Keep reviews whose job title matches these words. Glassdoor may include closely related titles. |
| `keyword` | text | empty | Keep reviews that mention this word or phrase. Combined with a star rating, the actor applies an exact client-side rating filter. |
| `language` | select | English | English, French, German, Dutch, Portuguese, Spanish, Italian, or all languages. |
| `languages` | string list | empty | Collect reviews in any of several languages. When set, it takes precedence over `language`. |
| `includeWorldwideReviews` | boolean | false | Remove Glassdoor's default review criteria and include reviews from all countries. |
| `includeCompanySummary` | boolean | false | Add one `companySummary` record per company with saved, available, site total, stop reason, logo, rating, and URL. |
| `includeCompanyProfile` | boolean | false | Add website, headquarters, size, revenue, industry, CEO, and company sub-ratings to each review. |
| `onlyNew` | boolean | false | Emit only reviews that were not seen in a previous run. Stores a per-company review-id watermark and seen set in the named `monitorId` key-value store. Forces newest-first order. |
| `monitorId` | string | `glassdoor-reviews` | Name of the key-value store that holds monitoring state. Use the same value on every scheduled run. |
| `emitUnchanged` | boolean | false | With `onlyNew`, also emit previously seen reviews that have not changed. Each emitted review gets `isNew: false` and its original `firstSeenAt`. |

### Examples

One company by URL:

```json
{
  "companies": ["https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"],
  "maxItems": 50,
  "sortBy": "mostRecent"
}
```

Several companies by name or id:

```json
{
  "companies": ["Microsoft", "Amazon", "9079"],
  "maxItems": 300,
  "maxReviewsPerCompany": 100,
  "language": "eng"
}
```

Recent five-star reviews from current employees:

```json
{
  "companies": ["https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"],
  "maxItems": 100,
  "rating": "5",
  "onlyCurrentEmployees": true,
  "postedWithinDays": "90"
}
```

Exact date range with several star ratings and languages:

```json
{
  "companies": ["https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"],
  "maxItems": 200,
  "dateFrom": "2026-01-01",
  "dateTo": "2026-06-30",
  "ratings": ["1", "2"],
  "languages": ["eng", "fra"]
}
```

New York engineers with employer responses:

```json
{
  "companies": ["https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"],
  "maxItems": 50,
  "location": "New York, NY",
  "jobFunction": "1007",
  "onlyWithEmployerResponses": true
}
```

All languages, worldwide, with company profile:

```json
{
  "companies": ["https://www.glassdoor.com/Reviews/Siemens-Reviews-E3510.htm"],
  "maxItems": 200,
  "language": "all",
  "includeWorldwideReviews": true,
  "includeCompanyProfile": true
}
```

Scheduled incremental monitoring:

```json
{
  "companies": ["https://www.glassdoor.com/Reviews/Google-Reviews-E9079.htm"],
  "maxItems": 500,
  "onlyNew": true,
  "monitorId": "google-reviews"
}
```

## Output

Each dataset item is one review. The actor keeps these existing fields with the same names:

`reviewId`, `reviewDate`, `title`, `pros`, `cons`, `advice`, `ratingOverall`, `ratingWorkLifeBalance`, `ratingCultureAndValues`, `ratingDiversityAndInclusion`, `ratingSeniorLeadership`, `ratingCareerOpportunities`, `ratingCompensationAndBenefits`, `ratingCeo`, `ratingBusinessOutlook`, `ratingRecommendToFriend`, `jobTitle`, `location`, `employmentStatus`, `isCurrentJob`, `lengthOfEmployment`, `countHelpful`, `countNotHelpful`, `companyName`, `companyId`.

New fields are added beside them:

| Field | Description |
|---|---|
| `reviewUrl` | Canonical link to the company reviews page with this review's `#Review<id>` anchor. Built from Glassdoor's canonical Reviews URL, so non-ASCII company names such as L'Oréal and Nestlé stay valid. |
| `companyLogo` | Company square logo URL, from the company profile or the review response. |
| `jobTitleId` | Glassdoor's job-title id. |
| `locationId` | Glassdoor's location id. |
| `locationType` | Location type, such as `CITY`. |
| `isFeatured` | Whether Glassdoor marked the review as featured. |
| `languageId` | Review language bucket, such as `eng` or `fra`. |
| `originalLanguageId` | Original language when Glassdoor exposes it. |
| `summaryOriginal`, `prosOriginal`, `consOriginal`, `adviceOriginal` | Original text when Glassdoor exposes it. |
| `translationMethod` | Translation method when Glassdoor exposes it. |
| `hasEmployerResponse` | Whether the employer replied to the review. |
| `employerResponses` | Employer replies, with response text, date, responder job title, and helpful count. |
| `companyRating` | Company's overall rating. |
| `companyReviewCount` | Company's total review count. |
| `companyUrl` | Company's Glassdoor reviews page. |
| `companyRatingDistribution` | Company's star distribution by rating category. |
| `sourceDomain` | Glassdoor domain used for the data. |
| `scrapedAt` | Run timestamp in UTC. |

When `onlyNew` is on, each emitted review also gets these monitoring fields:

| Field | Description |
|---|---|
| `isNew` | `true` when the review id was never seen by this monitor, `false` for a previously seen review emitted because `emitUnchanged` is on. |
| `firstSeenAt` | UTC timestamp of the first run that saw this review. |
| `lastSeenAt` | UTC timestamp of the current run that saw this review. |
| `changed` | `true` when a previously seen review's tracked content changed since the stored snapshot. |
| `lastChangedAt` | UTC timestamp of the first or latest detected content change. |

When `includeCompanyProfile` is on, each review also gets `companyWebsite`, `companyHeadquarters`, `companySize`, `companyRevenue`, `companyType`, `companyFoundedYear`, `companyIndustry`, `companyCeo`, and `companySubRatings`.

`companySubRatings` keeps the six category ratings on Glassdoor's 1-5 scale (`overall`, `workLifeBalance`, `cultureAndValues`, `diversityAndInclusion`, `seniorManagement`, `careerOpportunities`, `compensationAndBenefits`) and converts the three fraction fields to 0-100 percentages: `ceoApprovalPct`, `recommendToFriendPct`, and `businessOutlookPct`. A `scale` string documents both scales.

`lengthOfEmployment` is Glassdoor's tenure bucket; `0` means less than one year, not missing.

Missing values are omitted. For example, a review without advice has no `advice` key, and a review without sub-ratings has no sub-rating keys. Booleans such as `isCurrentJob`, `isFeatured`, and `hasEmployerResponse` are always present.

## Completeness and company summaries

Every run reports a completeness contract in the status message and in the `RUN_SUMMARY` key-value record:

| Field | Meaning |
|---|---|
| `saved` | Reviews written to the dataset. |
| `available` | Server-side review count for the exact filter set, when it is exact. `null` when a client-side filter (keyword + rating, multi-star, date window) makes the server count non-exact. |
| `siteTotal` | Glassdoor's total review count across the processed companies. |
| `stopReason` | Why scraping stopped: `maxItems`, `maxReviewsPerCompany`, `postedWithinDays`, `dateFrom`, `onlyNew`, `source exhausted`, `error`, or `completed`. |

When `includeCompanySummary` is on, the actor also writes one record per company with `recordType: "companySummary"` and the same `saved`/`available`/`siteTotal`/`stopReason` fields plus company id, name, logo, rating, URL, and the resolved location. With `onlyNew`, summaries also include `newReviews`, `unchangedReviews`, `monitorId`, and the stored `watermark`. Filter on `recordType` to separate summaries from reviews.

## Incremental monitoring

Set `onlyNew` to run the actor on a schedule and receive only reviews that are new since the previous run. Monitoring state lives in a named key-value store whose name is `monitorId` (default `glassdoor-reviews`). Use the same `monitorId` on every run that belongs to the same monitor.

How it works:

- Each company has its own state record with a numeric `reviewId` watermark and a `seen` set of review ids, first-seen timestamps, last-seen timestamps, and content hashes.
- The first run emits all matching reviews (up to `maxItems`) as `isNew: true` and records their ids.
- Later runs read newest first and stop as soon as they reach the stored watermark, so they do not page through the entire history. A run that stops this way reports `stopReason: "onlyNew"`.
- A review is emitted only when its id is not in the seen set. Previously seen reviews are skipped by default, so they are not billed twice.
- `emitUnchanged` re-emits previously seen reviews with `isNew: false`, their original `firstSeenAt`, and `changed` set when the tracked review content differs from the stored hash.
- State is written only after the dataset push succeeds. If a push fails, the affected ids are not marked as seen, so the next run retries them.
- `maxItems` and `maxReviewsPerCompany` stop the run early without advancing the watermark past unseen reviews. The next run resumes where the previous one stopped.
- Monitoring state is tied to the current filter set (ratings, employment types, keyword, location, language, date window, and so on). Changing filters starts a fresh baseline for that company.

Only reviews above the stored watermark are read, so edits to older reviews are not detected unless `emitUnchanged` is used on a review that is re-encountered. To start over, use a new `monitorId` or delete the named key-value store.

## How far back and how many reviews

Glassdoor's public page shows only a slice of a company's reviews. This actor uses Glassdoor's review endpoint, which can return thousands of reviews. For Google, the actor reaches about 74,000 reviews, close to Glassdoor's own total. For smaller companies, it returns everything Glassdoor serves.

Glassdoor still counts a small number of reviews it does not serve. The actor reports the available count and the site total in the run status, so you can see the gap instead of guessing. Set `language` to all (or list every `languages` value) and `includeWorldwideReviews` to true to reach the broadest set.

## Languages and countries

Glassdoor stores reviews in language buckets. Set `language` to collect English, French, German, Dutch, Portuguese, Spanish, Italian, or all languages, or list several values in `languages`. Region-specific Glassdoor URLs are accepted, but the data comes from Glassdoor's global review endpoint; the country domain alone does not create a separate review set. `sourceDomain` records the domain from the input URL.

## FAQ

**Do I need a Glassdoor account or cookie?**
No. The actor reads public review data without a login, cookie, or user-supplied proxy.

**Why did I get fewer reviews than `maxItems`?**
The company may have fewer reviews than requested, Glassdoor's filters may exclude some reviews, or the recent-date window may have been reached. The run status shows the stop reason and the available count out of the site total (for example, available 51,182 of 74,053).

**Why are some fields missing on some reviews?**
Glassdoor does not require reviewers to provide advice, tenure, sub-ratings, CEO approval, business outlook, or a response. Missing values are omitted, not filled with placeholders.

**Can I filter by reviewer location or job function?**
Yes. Enter a city, state, metro area, or country in `location`; the actor resolves it through Glassdoor's location search before scraping. Select a `jobFunction` category to keep only that function. Ambiguous locations are reported with the chosen candidate and fallbacks, and a zero-result candidate falls back to the next one. If a location cannot be resolved at all, the actor warns and ignores the filter instead of failing the run.

**Can I filter by an exact date range?**
Yes. Set `dateFrom` and `dateTo` (`YYYY-MM-DD`). Glassdoor's endpoint does not accept arbitrary date bounds, so the actor reads newest-first and applies the range client-side. It stops once reviews older than `dateFrom` are reached. `postedWithinDays` remains a shortcut for a recent window.

**Can I filter by several star ratings, languages, or employment types?**
Yes. Use the `ratings`, `languages`, and `employmentTypes` lists. Multi-star and date filters are applied client-side, so the run status marks the server count as non-exact instead of claiming it is the final count.

**Can I monitor only new reviews?**
Yes. Run the actor on a schedule with `onlyNew: true` and the same `monitorId`. The actor stores a per-company review-id watermark and seen set in the named key-value store, emits only reviews it has not seen before, and reports `stopReason: "onlyNew"` when it reaches the watermark. Set `emitUnchanged: true` to also receive previously seen reviews with `isNew: false` and change flags. Use a new `monitorId` to start a fresh baseline.

**What happens with an ambiguous or invalid company or location?**
The actor no longer silently takes the first autocomplete row. Company names require an exact or unique match; ambiguous names are skipped with a warning that lists candidates. Location candidates are ranked (city/country before state), ambiguous choices are reported, and a zero-result location falls back to the next candidate. An unresolved location is ignored with a warning instead of failing the whole run.

**Is this affiliated with Glassdoor?**
No. This actor collects public review data and is not affiliated with, endorsed by, or sponsored by Glassdoor.

## Data source and limitations

- Data source: Glassdoor's public review and company endpoints.
- No user credentials, cookies, or proxy configuration are required.
- Reviewer names are not exposed by Glassdoor's public review data. The actor does not attempt to identify reviewers.
- Employer responses are optional and appear only when Glassdoor provides them. Use onlyWithEmployerResponses to keep response-bearing reviews only.
- Glassdoor does not expose original-language or translation text for the sampled reviews; those fields are omitted unless the source provides them.
- Arbitrary date ranges are applied client-side, so very old ranges may require paging through newer reviews first.
- Keyword + exact rating filtering is also client-side because Glassdoor treats the server rating as a minimum. Newest-first order may page through many non-matching reviews; highest-rated or lowest-rated order is faster for sparse exact ratings.
- Company names are resolved through Glassdoor autocomplete with exact/unique matching. For ambiguous names, use the company URL or employer id.
- Regional Glassdoor URLs are accepted for company resolution, but review data still comes from Glassdoor's global endpoint; `sourceDomain` records the input domain.
- Monitoring state is stored in a named key-value store. Use the same `monitorId` across scheduled runs; a different id starts a fresh baseline. State is tied to the current filter set, and edits to reviews older than the stored watermark are not re-read.
- Glassdoor can change its public endpoints without notice. The actor rotates sessions and escalates direct → datacenter → residential proxies on repeated blocks. If a run reports a block or an endpoint error, re-run later or contact support with the run id.
