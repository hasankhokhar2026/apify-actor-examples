# Seek.com.au Job Search with Salary & Work-Type Filters

Seek.com.au job pages embed their full listing data right inside the page, which this actor reads directly — no login, no cookies. Give it search URLs, or a keyword and location to build one, and it returns each matching job with company, salary, classification and the complete description, narrowed by work type, work arrangement, salary band and posting date.

## What this actor does

- Scrapes job listings from one or more Seek search URLs, or builds a search URL from a keyword, location, state and postcode
- Accepts a direct job URL as well as a search URL
- Fetches each job's own detail page for the full description and apply link, when enabled
- Filters results client-side by work type, work arrangement, posting date, salary range, subclassification and title keywords
- Can require that the job description contain an email address, a phone number, or both
- Omits a field from the record when Seek's own listing doesn't provide it

## Output per job

| Field | Description |
|---|---|
| `type` | `"job_seek"` for a normal record, or `"job_seek_blocked"` if a search matched zero jobs |
| `id` | Seek job ID |
| `url` / `jobLink` | Job page URL |
| `title` | Job title |
| `company` | Advertiser or company name |
| `companyLogo` | Company logo image URL |
| `location` | `{ city, state, postCode, country }` |
| `locationDescription` | Human-readable location label |
| `locationArea` | Seek's named area for the listing |
| `broaderLocationName` | Parent region name |
| `workType` | e.g. `Full Time`, `Contract/Temp` |
| `workTypeLabels` | Raw work-type enum values |
| `workArrangement` | e.g. `On-site`, `Hybrid`, `Remote` |
| `workArrangementTypes` | Raw work-arrangement enum values |
| `salary` | Salary as displayed on the listing |
| `salaryDetails` | `{ min, max, currency, type }` when Seek provides a parsed range |
| `postedAt` / `postedAtLabel` | Posting date, machine and display form |
| `expiresAt` | Listing expiry date |
| `classification` / `subClassification` | Seek's job category and subcategory |
| `normalisedRoleTitle` / `normalisedOrganisationName` | Seek's normalized title/company fields |
| `descriptionHtml` / `descriptionText` | Full job description, HTML and plain text |
| `teaser` | Short one-line summary |
| `bulletPoints` | Highlight bullet points from the listing |
| `questionnaire` | Screening questions, when the listing has any |
| `recruiterName` / `recruiterAgency` / `recruiterProfile` | Recruiter details, when posted by an agency |
| `advertiserId` / `advertiserName` / `advertiserVerified` | Advertiser identity and verification flag |
| `isPrivateAdvertiser` | True when the advertiser posts without a company identity |
| `isLinkOut` | True when applying sends the candidate to an external site |
| `isVerified` / `isExpired` | Listing status flags |
| `status` / `sourceZone` | Seek's internal listing status and zone |
| `isFeatured` / `isPremium` / `isStandout` / `isBranded` | Listing promotion flags |
| `displayType` | Seek's display-tier label for the listing |
| `applyUrl` / `applyLink` | Apply link |
| `directApplyUrl` | External apply target, when applying leaves Seek |
| `phoneNumber` | Recruiter phone number, when listed |
| `videoUrl` / `videoPosition` | Advertiser video, when the listing includes one |
| `branding` | `{ logoUrl, coverImageUrl, thumbnailCoverImageUrl, id }` |
| `companyId` / `companySlug` | Company profile identifiers |
| `companyIndustry` / `companySize` / `companyWebsite` | Company profile details |
| `companyDescription` / `companyRating` / `companyReviewCount` / `companyPerks` | Company profile content, when Seek has one |
| `companyProfile` | Raw nested company profile object, when returned |
| `numApplicants` | Number of applicants shown on the listing |
| `emails` / `phoneNumbers` | Contact details extracted from the job description text |
| `scrapedAt` | UTC timestamp of when the record was captured |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchUrls` | array | `["https://www.seek.com.au/python-jobs"]` | Seek search or direct job URLs (required) |
| `searchTerm` | string | – | Keywords used to build a search URL when `searchUrls` isn't enough on its own |
| `location` | string | – | Location text, e.g. `Sydney NSW`, combined with `searchTerm` |
| `state` | string (select) | – (none) | Australian state: `NSW`, `VIC`, `QLD`, `WA`, `SA`, `TAS`, `ACT`, `NT` |
| `postCode` | string | – | Australian 4-digit postcode, appended to the location |
| `radius` | integer | – | Search radius in kilometres around the location (0–100) |
| `salaryType` | string (select) | `any` | `any`, `AnnualPackage`, `HourlyRate`, `MonthlyPackage`, `YearlyPackage` |
| `workTypes` | array | – | Keep only `Full Time`, `Part Time`, `Contract/Temp`, and/or `Casual/Vacation` jobs |
| `workArrangements` | array | – | Keep only `On-site`, `Hybrid`, and/or `Remote` jobs |
| `dateRange` | string (select) | `any` | Keep only jobs posted within `1`, `3`, `7`, `14`, or `30` days, or `any` time |
| `salaryMin` | integer | – | Keep only jobs whose parsed salary range reaches at least this value (AUD) |
| `salaryMax` | integer | – | Keep only jobs whose parsed salary range stays at or below this value (AUD) |
| `subclassifications` | array | – | Keep only jobs whose subclassification name matches one of these values |
| `includeOneInTitle` | array | – | Keep only jobs whose title contains at least one of these substrings |
| `requireEmail` | boolean | false | Keep only jobs whose description contains an email address |
| `requirePhone` | boolean | false | Keep only jobs whose description contains a phone number |
| `requireEmailPhone` | boolean | false | Keep only jobs whose description contains both an email address and a phone number |
| `sortBy` | string (select) | `KeywordRelevance` | `KeywordRelevance` or `ListedDate`, applied when a search URL is built from keywords |
| `maxItems` | integer | 3 | Maximum job listings to return (1–300) |
| `scrapeJobDetails` | boolean | true | Fetch each job's own page for the full description and metadata; off returns only listing-card fields |
| `proxyConfiguration` | object (proxy) | `{ "useApifyProxy": true }` | Apify proxy configuration |

### Example: keyword and location search

```json
{
  "searchUrls": [],
  "searchTerm": "python developer",
  "location": "Sydney NSW",
  "workTypes": ["Full Time"],
  "dateRange": "7",
  "maxItems": 50
}
```

### Example: remote jobs with a salary floor

```json
{
  "searchUrls": ["https://www.seek.com.au/jobs?keywords=data%20analyst"],
  "workArrangements": ["Remote"],
  "salaryMin": 90000,
  "sortBy": "ListedDate",
  "maxItems": 40
}
```

### Example: a specific job URL

```json
{
  "searchUrls": ["https://www.seek.com.au/job/91572959"],
  "scrapeJobDetails": true
}
```

## Use cases

- **Recruitment sourcing** — pull fresh listings for a role and location before shortlisting candidates
- **Salary benchmarking** — collect disclosed salary ranges across a classification to gauge market rates
- **Competitive hiring intelligence** — track which companies are actively hiring in a region or field
- **Job-alert pipelines** — run on a schedule with `dateRange` set to surface only newly posted roles
- **Lead generation for recruiters** — use `requireEmail`/`requirePhone` to find listings with direct contact details

## FAQ

**Is this affiliated with Seek?**
No. This is an independent data extraction tool and has no connection to Seek Limited.

**Do I need to log in or use cookies?**
No — job listings are publicly accessible without an account.

**Does this need a proxy?**
A proxy input is included and enabled by default, since direct requests from some networks get blocked; leave the default `proxyConfiguration` in place rather than removing it.

**What happens if my search matches no jobs?**
The run still emits one record with `type: "job_seek_blocked"` so downstream pipelines never receive a completely empty dataset.

**Why is `salary` or `salaryDetails` missing from some jobs?**
Many advertisers don't disclose a salary on Seek at all; when that's the case the actor leaves those fields out rather than guessing a value.

**What's the difference between `workTypes` and `workArrangements`?**
`workTypes` filters on employment basis (full time, part time, contract, casual); `workArrangements` filters on where the work happens (on-site, hybrid, remote). They can be combined.

**What does turning off `scrapeJobDetails` change?**
With it off, you get only the fields already present on the search-results page (title, company, location, salary label, posting date); turning it on adds a second fetch per job for the full description, apply link and extra metadata.

**Does this cover New Zealand listings on seek.co.nz?**
No — this actor reads seek.com.au only.
