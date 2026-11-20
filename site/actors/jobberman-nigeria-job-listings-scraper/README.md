# Jobberman Nigeria Job Listings Scraper

Jobberman is Nigeria's largest online job board, listing openings across every state and industry from Lagos finance roles to remote positions for Nigerian talent. This actor searches live Jobberman listings or pulls full detail from specific job URLs, returning structured records with salary, experience and company data ready for recruitment pipelines or market research.

## What this actor does

- Searches Jobberman by free-text keyword combined with location, industry, job function and experience-level filters, or fetches a fixed list of listing URLs directly
- Orders search results the same way Jobberman itself does — Latest, Featured or Popular
- Optionally opens each listing's detail page to pull the full description, requirements, application deadline and employer information, not just the search-card summary
- Applies salary-band and keyword filters after fetching, so jobs with no disclosed salary are never silently dropped
- Never returns the same listing twice within a run
- Omits any field Jobberman didn't disclose for that listing — you won't see empty strings or nulls

## Output per job

- `jobId` — Jobberman's internal listing identifier
- `title`, `companyName`, `location`
- `employmentType` — `fullTime`, `partTime`, `contract`, `internship`, `temporary` or `volunteer`
- `category` — occupational category as shown on the listing (e.g. "Accounting, Auditing & Finance")
- `industry` — the hiring company's industry
- `experienceLevel` — qualifications/experience text from the listing
- `experienceMonths` — months of experience required, when stated
- `educationLevel` — minimum education requirement (e.g. "HND", "Bachelor's Degree")
- `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod` — only present when Jobberman discloses pay
- `descriptionHtml`, `descriptionText` — full job description, when detail enrichment is on or mode is `byUrls`
- `datePosted`, `validThrough` — ISO 8601 dates
- `datePostedRelative` — fallback like "Today" or "3 days ago" when an absolute date wasn't fetched
- `isFeatured`, `isNew`, `isEasyApply` — listing badges, when present
- `addressLocality`, `addressRegion`, `addressCountry`
- `companyLogoUrl` — omitted for Jobberman's generic placeholder icon
- `directApply` — whether Jobberman allows applying directly without leaving the site
- `sourceUrl` — canonical Jobberman listing URL
- `recordType` (always `job`), `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` (keyword + filters) or `byUrls` (direct listing fetch) |
| `searchQuery` | string | `sales` | Keyword — job title, skill or company name (mode=search) |
| `location` | string | – | Jobberman location region (e.g. `lagos`, `abuja`, `remote`) |
| `industry` | string | – | Jobberman industry filter |
| `jobFunction` | string | – | Jobberman job-function filter |
| `experienceLevel` | string | – | Experience-level filter |
| `employmentType` | string | – | Employment type filter, applied against the listing's displayed job type |
| `minSalary` | integer | – | Drop jobs whose disclosed salary band is entirely below this (NGN/month) |
| `maxSalary` | integer | – | Drop jobs whose disclosed salary band is entirely above this (NGN/month) |
| `containsKeyword` | string | – | Case-insensitive substring filter on title, company name and description |
| `sortBy` | string | `latest` | `latest`, `featured` or `popular` (mode=search) |
| `listingUrls` | array | `[]` | Direct Jobberman listing URLs (mode=byUrls) |
| `includeFullDescription` | boolean | `true` | Fetch each listing's detail page for full description, requirements, deadline and company info (mode=search); always on for mode=byUrls |
| `maxItems` | integer | `30` | Hard cap on emitted records (1–1000) |

### Example: sales jobs in Lagos with full descriptions

```json
{
  "mode": "search",
  "searchQuery": "sales",
  "location": "lagos",
  "experienceLevel": "mid-level",
  "includeFullDescription": true,
  "maxItems": 50
}
```

### Example: remote IT jobs sorted by popularity

```json
{
  "mode": "search",
  "searchQuery": "developer",
  "location": "remote",
  "industry": "it-telecoms",
  "sortBy": "popular",
  "maxItems": 40
}
```

### Example: fetch specific listings by URL

```json
{
  "mode": "byUrls",
  "listingUrls": [
    "https://www.jobberman.com/listings/accountstax-senior-2k886k"
  ]
}
```

## Use cases

- **Recruitment agencies** build a current view of Nigerian vacancies by industry or region without visiting Jobberman manually
- **Salary benchmarking** — aggregate disclosed salary bands by job function or experience level
- **Job boards and aggregators** backfill Nigerian listings into their own search index
- **HR tech and labour-market research** track hiring demand by industry across Nigerian states
- **Jobseekers and career coaches** monitor new openings matching a specific keyword or location

## FAQ

**Is this affiliated with Jobberman?**
No. This is an independent actor that reads publicly available Jobberman listing pages; it is not operated by or affiliated with Jobberman.

**Why do some jobs have no salary fields?**
Jobberman only shows pay for listings where the employer disclosed it. Jobs without a stated salary pass through filters untouched rather than being dropped.

**What's the difference between the search-card data and the enriched detail data?**
The search results page gives title, company, location and a short salary/type summary. Turning on `includeFullDescription` (or using `byUrls`) also fetches the listing's own page for the full description, deadline, qualifications and employer info.

**Why is `companyLogoUrl` sometimes missing?**
Jobberman shows a generic placeholder icon for employers that haven't uploaded a logo; this actor filters that placeholder out rather than returning a meaningless image URL.

**Can I filter by salary without excluding unlisted jobs?**
Yes — `minSalary`/`maxSalary` only remove jobs whose disclosed band falls entirely outside the range; jobs with no disclosed salary always pass through.

**How fresh are the results?**
Each run re-queries Jobberman live, so results reflect whatever is currently posted, ordered by whichever `sortBy` option you pick.

**Does `byUrls` support any listing URL?**
It expects direct Jobberman job-listing URLs (the pages under `/listings/...`); category or search pages aren't valid detail URLs.
