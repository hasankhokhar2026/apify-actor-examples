# Glassdoor Review Export - Ratings, Pros, Cons & Replies

Collect employee reviews from Glassdoor companies by URL, company name, or employer id. Get the overall rating and every sub-rating, pros, cons, advice to management, reviewer job title and location, employment status, helpful votes, language, employer responses, and optional company profile data. No Glassdoor login, cookie, or proxy setup is required.

## What this actor does

- Accepts one or many Glassdoor company Review or Overview URLs, company names, or employer ids.
- Reads Glassdoor's public review data through its own JSON endpoint, so it does not need a browser or a logged-in session.
- Returns every review Glassdoor serves, including beyond the roughly 200 reviews the public review page shows.
- Supports exact star filtering, employment type, current employees only, employer responses only, keyword search, job-title keywords, job function, location, language selection, worldwide review coverage, and a recent-date window.
- Keeps the 25 fields from the previous version and adds review URLs, language data, employer responses, company context, and optional firmographics.
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
| `rating` | select | Any rating | Keep only reviews with an exact 1-5 star overall rating. |
| `employmentType` | select | Any | Full-time (regular), part-time, intern, contract, freelance, or temporary. |
| `onlyCurrentEmployees` | boolean | false | Keep only reviews from current employees. |
| `onlyWithEmployerResponses` | boolean | false | Keep only reviews that have an official employer response. |
| `jobTitleKeywords` | text | empty | Keep reviews whose job title matches these words. Glassdoor may include closely related titles. |
| `keyword` | text | empty | Keep reviews that mention this word or phrase. |
| `language` | select | English | English, French, German, Dutch, Portuguese, Spanish, Italian, or all languages. |
| `includeWorldwideReviews` | boolean | false | Remove Glassdoor's default review criteria and include reviews from all countries. |
| `includeCompanyProfile` | boolean | false | Add website, headquarters, size, revenue, industry, CEO, and company sub-ratings to each review. |

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

## Output

Each dataset item is one review. The actor keeps these existing fields with the same names:

`reviewId`, `reviewDate`, `title`, `pros`, `cons`, `advice`, `ratingOverall`, `ratingWorkLifeBalance`, `ratingCultureAndValues`, `ratingDiversityAndInclusion`, `ratingSeniorLeadership`, `ratingCareerOpportunities`, `ratingCompensationAndBenefits`, `ratingCeo`, `ratingBusinessOutlook`, `ratingRecommendToFriend`, `jobTitle`, `location`, `employmentStatus`, `isCurrentJob`, `lengthOfEmployment`, `countHelpful`, `countNotHelpful`, `companyName`, `companyId`.

New fields are added beside them:

| Field | Description |
|---|---|
| `reviewUrl` | Link to the company reviews page with this review's anchor. |
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

When `includeCompanyProfile` is on, each review also gets `companyWebsite`, `companyHeadquarters`, `companySize`, `companyRevenue`, `companyType`, `companyFoundedYear`, `companyIndustry`, `companyCeo`, and `companySubRatings`.

Missing values are omitted. For example, a review without advice has no `advice` key, and a review without sub-ratings has no sub-rating keys. Booleans such as `isCurrentJob`, `isFeatured`, and `hasEmployerResponse` are always present.

## How far back and how many reviews

Glassdoor's public page shows only a slice of a company's reviews. This actor uses Glassdoor's review endpoint, which can return thousands of reviews. For Google, the actor reaches about 74,000 reviews, close to Glassdoor's own total. For smaller companies, it returns everything Glassdoor serves.

Glassdoor still counts a small number of reviews it does not serve. The actor reports the filtered review count and the site total in the run status, so you can see the gap instead of guessing. Set `language` to all and `includeWorldwideReviews` to true to reach the broadest set.

## Languages and countries

Glassdoor stores reviews in language buckets. Set `language` to collect English, French, German, Dutch, Portuguese, Spanish, Italian, or all languages. Region-specific Glassdoor URLs are accepted, but the data comes from Glassdoor's global review endpoint; the country domain alone does not create a separate review set.

## FAQ

**Do I need a Glassdoor account or cookie?**
No. The actor reads public review data without a login, cookie, or user-supplied proxy.

**Why did I get fewer reviews than `maxItems`?**
The company may have fewer reviews than requested, Glassdoor's filters may exclude some reviews, or the recent-date window may have been reached. The run status shows the stop reason and the available count out of the site total (for example, available 51,182 of 74,053).

**Why are some fields missing on some reviews?**
Glassdoor does not require reviewers to provide advice, tenure, sub-ratings, CEO approval, business outlook, or a response. Missing values are omitted, not filled with placeholders.

**Can I filter by reviewer location or job function?**
Yes. Enter a city, state, metro area, or country in `location`; the actor resolves it through Glassdoor's location search before scraping. Select a `jobFunction` category to keep only that function. If a location cannot be resolved, the run fails with a clear message instead of silently ignoring the filter.

**Can I filter by an exact date range?**
The actor supports "posted within N days" by reading newest-first and stopping at the cutoff. Arbitrary start/end dates are not supported by the public endpoint.

**Can I monitor only new reviews?**
Run the actor on a schedule with Newest first and deduplicate by `reviewId` in your workflow. The actor does not keep state between runs.

**Is this affiliated with Glassdoor?**
No. This actor collects public review data and is not affiliated with, endorsed by, or sponsored by Glassdoor.

## Data source and limitations

- Data source: Glassdoor's public review and company endpoints.
- No user credentials, cookies, or proxy configuration are required.
- Reviewer names are not exposed by Glassdoor's public review data. The actor does not attempt to identify reviewers.
- Employer responses are optional and appear only when Glassdoor provides them. Use onlyWithEmployerResponses to keep response-bearing reviews only.
- Glassdoor does not expose original-language or translation text for the sampled reviews; those fields are omitted unless the source provides them.
- Arbitrary start/end date ranges are not available. Use postedWithinDays for a recent-date window.
- Company names are resolved through Glassdoor autocomplete. For ambiguous names, use the company URL or employer id.
- Glassdoor can change its public endpoints without notice. If a run reports a block or an endpoint error, re-run later or contact support with the run id.
