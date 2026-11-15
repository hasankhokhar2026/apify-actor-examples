# Seek.com.au Job Search with Salary & Work-Type Filters

Search SEEK Australia and New Zealand by keyword, location, work type, work arrangement, salary, posting date and classification — or paste search, company and job URLs. Every row carries the listing card plus, when enabled, the full ad text, parsed salary, published contacts, company profile and applicant counts.

SEEK's public HTML pages are behind Cloudflare, but the JSON endpoints the site itself uses are not. This actor talks to those endpoints directly: no login, no cookies, no proxy and no browser.

## What this actor does

- Searches `seek.com.au` (AU) and `seek.co.nz` (NZ) through SEEK's own search API
- Accepts search URLs, category pages, company pages and direct job links, including expired job links
- Builds searches from keywords, city/suburb, state, postcode, radius, work type, work arrangement, date range, salary range and classification
- Paginates up to SEEK's 550-result ceiling per query; multiple search terms merge into one de-duplicated dataset
- Fetches each job's detail through SEEK's GraphQL endpoint for the full description, exact dates, contacts, company profile, screening questions, video and applicant insights
- Auto-enables detail fetching when you ask for jobs with an email or phone number
- Applies every filter again on the finished record, so a result never silently ignores your input
- Omits a field when SEEK does not provide it; never sends `null`, empty strings, empty arrays or placeholder records

## Output per job

| Field | Description |
|---|---|
| `type` | Always `"job_seek"` (the old `job_seek_blocked` placeholder is gone) |
| `id` | SEEK job ID |
| `url` / `jobLink` | Canonical job URL (`au.seek.com` or `nz.seek.com`) |
| `applyUrl` / `applyLink` | Apply URL, always `https://…/job/<id>/apply` |
| `shareLink` | SEEK's tracked share URL |
| `title` | Job title |
| `company` / `companyId` / `companySlug` / `companyUrl` | Employer identity |
| `companyLogo` | Listing-card logo |
| `location` | `{ suburb, city, state, stateName, postCode, country, region }` |
| `locationDescription` / `locationArea` / `broaderLocationName` | SEEK's display location, area and parent region |
| `workType` / `workTypes` | Employment type, first value and full array |
| `workTypeLabels` | SEEK's raw work-type codes |
| `workArrangement` / `workArrangements` / `workArrangementTypes` | On-site/Hybrid/Remote labels and raw IDs |
| `salary` | Salary label exactly as advertised |
| `salaryDetails` | `{ min, max, currency, type }` from the robust parser |
| `salaryMin` / `salaryMax` / `salaryCurrency` / `salaryPeriod` | Flat parsed salary fields (`year`, `hour`, `day`, `week`, `month`) |
| `postedAt` / `postedAtLabel` / `expiresAt` | ISO posting/expiry dates and the “3d ago” label |
| `classification` / `subClassification` | SEEK's taxonomy names |
| `classificationId` / `subClassificationId` | SEEK's taxonomy IDs |
| `classifications` | Array of all classification/subclassification pairs on the ad |
| `teaser` / `bulletPoints` / `questionnaire` | Short summary, ad highlights, screening questions |
| `descriptionHtml` / `descriptionText` | Full ad body (detail fetch only) |
| `recruiterName` / `recruiterAgency` / `recruiterProfile` | Advertiser/recruiter identity |
| `advertiserName` / `advertiserId` / `advertiserVerified` | Advertiser details and verification |
| `isPrivateAdvertiser` / `isVerified` / `isLinkOut` / `isExpired` | Listing flags |
| `status` / `sourceZone` | SEEK's listing status and zone |
| `isFeatured` / `isPremium` / `isStandout` / `isBranded` / `displayType` | Promotion signals |
| `contactMatches` | SEEK's structured contacts, e.g. `{ "type": "Email", "value": "jobs@acme.com" }` |
| `emails` / `phoneNumbers` | Email addresses and phone numbers from structured contacts plus the ad text |
| `branding` | `{ logoUrl, coverImageUrl, id }` |
| `videoUrl` / `videoPosition` | Advertiser video, when present |
| `companyProfile` | Company profile object: ID, name, slug, industry, size, website, description, rating, review count, perks |
| `companyIndustry` / `companySize` / `companyWebsite` / `companyDescription` / `companyRating` / `companyReviewCount` / `companyPerks` | Flat company-profile fields |
| `applicantCount` / `numApplicants` | Applicant count from SEEK's insights (same value, kept for compatibility) |
| `applicantsWithResumePercentage` / `applicantsWithCoverLetterPercentage` | Applicant-quality signals when SEEK exposes them |
| `normalisedRoleTitle` / `normalisedOrganisationName` | SEEK's normalized role/company names |
| `tags` | Quick attribute tags derived from the listing's work types, arrangements and classification |
| `market` | `AU` or `NZ` |
| `searchQuery` / `searchUrl` / `sourceUrl` / `searchParams` | Provenance: what found this job and with which filters |
| `detailFetched` | `true` when the detail payload was merged |
| `scrapedAt` | UTC capture timestamp |

Compatibility notes: the old `phoneNumber` field is still recognized in code but SEEK's API returns `null` for every ad, so it is omitted. The old `directApplyUrl` field is emitted only if SEEK ever exposes an external apply target; today it does not, so `applyUrl` points at SEEK's `/job/<id>/apply` page. All other pre-revamp field names remain available.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchUrls` | array | `[]` (prefill: one Melbourne software-engineer URL) | Search, category, company or direct job URLs. AU and NZ can be mixed. |
| `searchTerms` | array | `[]` | One search per keyword phrase; results merge and de-duplicate. |
| `location` | string | – | City, suburb or region, e.g. `Sydney`, `Geelong`, `Auckland`. |
| `state` | select | Any | Australian state/territory. Full names are preferred; legacy abbreviations still work. |
| `postCode` | string | – | Australian postcode; used as the search location when no city is given. |
| `radius` | integer | – | Radius in km around the location/postcode (0–100). |
| `country` | select | `AU` | `AU` (seek.com.au) or `NZ` (seek.co.nz). |
| `workTypes` | multiselect | – | Full time, Part time, Contract/Temp, Casual/Vacation. |
| `workArrangements` | multiselect | – | On-site, Hybrid, Remote. |
| `dateRange` | select | `any` | `1`, `3`, `7`, `14`, `30`, `31` days or any time. |
| `salaryType` | select | `any` | `annual` or `hourly`. Legacy `AnnualPackage`, `YearlyPackage`, `MonthlyPackage` and `HourlyRate` are mapped automatically. |
| `salaryMin` / `salaryMax` | integer | – | Salary range in the market's currency. |
| `classification` | select | Any | All 29 SEEK top-level job families. |
| `subclassifications` | array | – | SEEK subclassification IDs or exact names; one search runs per value. |
| `companyName` | string | – | Employer/recruiter name filter. |
| `includeOneInTitle` | array | – | Keep jobs whose title contains at least one phrase. |
| `includeKeywords` | array | – | Keep jobs whose title, company, teaser, bullets, description, classification, work type or salary contains at least one phrase. |
| `excludeKeywords` | array | – | Drop jobs whose text contains any phrase. |
| `requireEmail` / `requirePhone` / `requireEmailPhone` | boolean | false | Keep jobs that publish an email, a phone, or both. Automatically enables detail fetching. |
| `sortBy` | select | KeywordRelevance | Keyword relevance or newest first. |
| `maxItems` | integer | 50 (prefill 3) | Total rows across all queries (1–10,000). |
| `scrapeJobDetails` | boolean | true (prefill false) | Fetch full ad text, contacts, company profile, insights and expiry. |
| `maxConcurrency` | integer | 4 (prefill 2) | Parallel detail requests (1–10). |

### Example: keyword and location search

```json
{
  "searchTerms": ["data engineer"],
  "location": "Sydney",
  "state": "New South Wales",
  "workTypes": ["Full time"],
  "dateRange": "7",
  "maxItems": 50
}
```

### Example: remote jobs with a salary floor

```json
{
  "searchTerms": ["software engineer"],
  "workArrangements": ["Remote"],
  "salaryType": "annual",
  "salaryMin": 120000,
  "sortBy": "ListedDate",
  "maxItems": 100
}
```

### Example: a company page and a direct job

```json
{
  "searchUrls": [
    "https://au.seek.com/companies/murdoch-childrens-research-institute-436169",
    "https://au.seek.com/job/95797430"
  ],
  "maxItems": 20
}
```

### Example: contactable ads only

```json
{
  "searchTerms": ["developer"],
  "requireEmail": true,
  "maxItems": 20
}
```

### Example: New Zealand

```json
{
  "searchTerms": ["developer"],
  "country": "NZ",
  "maxItems": 50
}
```

## Use cases

- **Recruitment sourcing** — pull fresh listings for a role and location before shortlisting
- **Salary benchmarking** — collect disclosed salary ranges across a classification
- **Competitive hiring intelligence** — track which companies are hiring in a region or field
- **Job-alert pipelines** — schedule runs with `dateRange` to surface only new roles
- **Recruiter lead generation** — use `requireEmail`/`requirePhone` to find ads with direct contact details
- **Market expansion research** — compare Australian and New Zealand demand in one run

## FAQ

**Is this affiliated with SEEK?**
No. This is an independent data extraction tool and has no connection to SEEK Limited.

**Do I need to log in or use cookies?**
No. The search and detail APIs are public and cookieless.

**Do I need a proxy?**
No. The actor never asks for one; SEEK's JSON endpoints work directly. Old tasks that still send `proxyConfiguration` keep running and the key is ignored.

**What happens when a search matches zero jobs?**
The run succeeds with an empty dataset and a status message explaining that the result was legitimately empty. There is no placeholder record. Upstream failures still fail the run after retries.

**Why is salary missing from some jobs?**
Many advertisers do not disclose a salary. When a label exists, the parser handles ranges, `k`/`m` suffixes, annual/hourly/daily/weekly/monthly rates, superannuation text, AUD/NZD and bare numeric ranges. Jobs without a disclosed salary are kept unless you choose a salary basis.

**How many results can one search return?**
SEEK returns at most 550 jobs per query (50 per page, 11 pages). Add more `searchTerms` or URLs to collect more; the actor de-duplicates across all of them and honours `maxItems` up to 10,000.

**Does `state` cover regional towns?**
Full state names work for NSW, QLD, SA, TAS, ACT and NT. SEEK resolves state-only VIC and WA searches to Melbourne and Perth, so add a regional city under `location` to collect regional jobs there.

**Why is `applyUrl` sometimes different from the ad's external apply link?**
SEEK does not expose the external LinkOut destination through its public API. `applyUrl` is therefore the canonical SEEK apply page (`/job/<id>/apply`), which routes the candidate to the employer's flow. `isLinkOut` tells you when that will leave SEEK.

**Why do contacts and company profiles appear on only some rows?**
Only some advertisers publish an email/phone or maintain a SEEK company profile. The actor ships the field when SEEK has it and omits it otherwise.

**Does detail fetching change the data?**
Yes: `scrapeJobDetails` adds the full description, exact expiry, structured contacts, company profile, screening questions, video and applicant counts. Turning it off returns the listing-card fields only.
