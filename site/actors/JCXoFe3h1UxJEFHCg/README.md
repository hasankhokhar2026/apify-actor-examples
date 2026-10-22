# Indeed Global Job Scraper with Company Salary Reports

Scrape **Indeed** jobs from 62 country sites by keyword, location, company and Indeed's own filters. Every row includes the full description, normalized salary, location with coordinates, benefits, recruiter contacts, freshness signals and the employer's Indeed rating report — with no Indeed account, login, cookies or proxy setup.

## What this actor does

- **Search, URLs and filters:** search by position, location and company, or paste Indeed search URLs, company job pages, job URLs and bare job IDs; apply date, salary, job type, workplace, easy apply, experience, education, radius and sort, with every result re-checked before saving
- **Salary that compares:** hourly, daily, weekly and monthly pay is converted to a yearly figure, with the original text, currency, period and source kept
- **Company report in the same row:** app-API ratings (overall, five category ratings, review count) always; optional HTML report adds CEO approval, founding year, wellbeing scores, industry fallback and average pay by job title
- **Freshness and coverage signals:** `displayTitle`, `refNum`, `isRepost`, `isLatestPost`, `isSponsored` and retrieved-vs-reported counts so a short run is visible instead of silent
- **Empty fields are omitted:** a value Indeed does not have for a job is left out of that row, never replaced with `null` or a guess

## Output per job

| Group | Fields |
|---|---|
| Job | `id`, `positionName`, `displayTitle`, `normalizedTitle`, `refNum`, `url`, `description`, `descriptionHtml` (when `includeDescriptionHtml` is on), `jobType`, `jobTypes`, `remoteWorkType`, `experienceLevel`, `educationLevels`, `workSchedule` (rare), `occupations`, `attributes`, `language`, `source`, `sourceEmployerName` |
| Salary | `salary` (as shown on Indeed), `salaryMin`, `salaryMax`, `salaryPeriod`, `salaryCurrency`, `salaryAnnualMin`, `salaryAnnualMax`, `salarySource`, `payTypes` |
| Benefits & schedule | `benefits`, `schedules` |
| Location | `location`, `streetAddress`, `neighborhood`, `city`, `county`, `state`, `stateName`, `postalCode`, `countryCode`, `countryName`, `latitude`, `longitude` |
| Dates & freshness | `postedAt`, `postingDateParsed`, `datePostedISO`, `datePublishedISO`, `isRepost`, `isLatestPost`, `isExpired`, `validThrough` (rare) |
| Applying & signals | `easyApply`, `externalApplyLink`, `isSponsored`, `emails`, `phoneNumbers` (international format), `urgentlyHiring`, `highVolumeHiring` |
| Coverage | `searchFacetTotal` (Indeed-reported upper bound), `searchRetrieved` (unique jobs retrieved by that search when the row was saved; the last row carries the final run count), `searchCoverage` (retrieved ÷ reported) |
| Company ratings (always, when the employer has reviews) | `rating`, `reviewsCount`, `companyRatings` (work-life balance, compensation and benefits, job security and advancement, management, culture) |
| Company report (when `includeCompanyRatings` is on) | `companyCeoApproval`, `companyFounded`, `companySalaries` (average pay by title with category, period and reported-salary count), `companyWorkWellbeing` (happiness, purpose, satisfaction, stress-free and more 0–100 scores) |
| Company | `company`, `companyId`, `companyUrl`, `companyLogo`, `companySize`, `companyRevenue`, `companyIndustry`, `companyWebsite`, `companyDescription`, `companyCeo`, `companyHeadquarters`, `companyInfo` (addresses, stock symbol, social links and more) |
| Context | `searchQuery`, `searchLocation`, `searchCompany`, `country`, `scrapedAt` |

If a pasted job URL can no longer be loaded from Indeed's job API or the mobile fallback, the run saves a truthful error row with `recordType: "error"`, `jobKey`, `error`, `country` and `scrapedAt` instead of a fabricated job.

### Fields Indeed does not return

The app API does not expose `estimatedSalary`/`estimated`, `detailedSalary`, `expiry` or `isPlacement` for this key, so they are omitted rather than guessed. `expirationDate` is not output separately; it is normalized to `validThrough` only when present. `workSchedule` is rare free text (not a structured object); both rare fields are copied when present and left out otherwise.

### Sample output row

```json
{
  "id": "6b86092e2a95d2c2",
  "positionName": "Sr. Machine Learning Engineer",
  "displayTitle": "Senior Machine Learning Engineer",
  "refNum": "2605",
  "company": "DocuSign",
  "url": "https://www.indeed.com/viewjob?jk=6b86092e2a95d2c2",
  "city": "Seattle",
  "state": "WA",
  "salary": "$178,900 - $262,825 a year",
  "salaryAnnualMin": 178900,
  "salaryAnnualMax": 262825,
  "salaryCurrency": "USD",
  "salaryPeriod": "YEARLY",
  "salarySource": "EMPLOYER",
  "jobTypes": ["Permanent", "Full-time"],
  "remoteWorkType": "Hybrid",
  "isRepost": false,
  "isLatestPost": true,
  "benefits": ["Paid parental leave", "Health insurance", "Paid time off"],
  "rating": 3.5,
  "reviewsCount": 139,
  "companyRatings": {
    "workLifeBalance": 3.8,
    "compensationAndBenefits": 4.0,
    "jobSecurityAndAdvancement": 3.1,
    "management": 3.1,
    "culture": 3.5
  },
  "companySalaries": [
    { "title": "Software Engineer", "salary": "$170,461", "amount": 170461, "period": "YEARLY", "reportedSalaries": 17 }
  ],
  "searchFacetTotal": 9615,
  "searchRetrieved": 808,
  "searchCoverage": 0.084,
  "scrapedAt": "2026-10-08T06:59:29Z"
}
```

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `position` | string | – | Job title, skill or keywords. Supports `company:Name`, `title:(…)`, quotes, `OR` and `-exclusions` |
| `location` | string | – | City, region or postal code; leave empty to search the whole country. `remote` (or `anywhere`, `work from home`) becomes the remote workplace filter |
| `company` | string | – | Only jobs from one employer. The name is resolved to Indeed's employer key and verified per job |
| `locationShards` | array | – | Extra city/region searches with the same keywords and filters. Deduplicated; the reliable way past the per-search ceiling |
| `country` | string | `US` | Indeed country site to search (62 countries) |
| `maxItemsPerSearch` | integer | `100` | Max jobs saved per search, i.e. the keyword search and each search URL |
| `maxItems` | integer | – | Optional hard cap for the whole run, across every search and pasted job URL |
| `shardByDate` | boolean | `false` | Run each keyword search for the last 1, 3, 7, 14 and 30 days and deduplicate |
| `jobType` | string | `""` (any) | `fulltime`, `parttime`, `contract`, `temporary`, `internship`, `permanent`, `seasonal`, `perdiem`, `freelance`, `apprenticeship`, `volunteer` |
| `workplaceType` | string | `""` (any) | `remote`, `hybrid` or `inPerson` |
| `datePosted` | string | `""` (any time) | `1`, `3`, `7`, `14` or `30` days |
| `experienceLevel` | string | `""` (any) | `noExperience`, `entry`, `mid` or `senior` |
| `educationLevel` | string | `""` (any) | `noDegree`, `highSchool`, `associate`, `bachelor`, `master` or `doctoral` |
| `salaryMin` | integer | – | Minimum yearly salary in the country's currency; jobs with no salary are excluded when set |
| `easyApplyOnly` | boolean | `false` | Only jobs you can apply to directly on Indeed |
| `radius` | integer | – | Search radius around `location` (Indeed's own default is 25); ignored without a location |
| `radiusUnit` | string | `miles` | `miles` or `kilometers` |
| `sort` | string | `relevance` | `relevance` or `date` (newest first) |
| `startUrls` | array | – | Indeed search URLs, company job pages (`/cmp/Name/jobs`), job URLs or job IDs. The filters above are added to search URLs that do not set their own |
| `includeCompanyRatings` | boolean | `true` | Add the HTML company report: CEO approval, founded, wellbeing, salary by title and industry fallback. Core ratings are always included |
| `includeSponsored` | boolean | `true` | Add `isSponsored` from Indeed's mobile results page where the job appears |
| `includeDescriptionHtml` | boolean | `false` | Also save `descriptionHtml`; the plain-text `description` is always included |
| `saveOnlyUniqueItems` | boolean | `true` | Save each job once even when several searches find it |

Date, salary, job type, workplace, easy apply and company filters are applied natively by Indeed's search API. Salary, date, job type, workplace, easy apply and company are then re-checked on each job, so a loose native match is not saved as a false positive. Indeed's easy-apply filter changes the result set but not the reported facet total.

### Example: remote full-time data analyst jobs from the last week

```json
{
  "position": "data analyst",
  "country": "US",
  "workplaceType": "remote",
  "jobType": "fulltime",
  "datePosted": "7",
  "maxItemsPerSearch": 200
}
```

### Example: senior engineering jobs paying at least $150,000 in Seattle

```json
{
  "position": "software engineer",
  "location": "Seattle, WA",
  "experienceLevel": "senior",
  "salaryMin": 150000,
  "maxItemsPerSearch": 500,
  "maxItems": 1000
}
```

### Example: all current Visa jobs with the full company report

```json
{
  "company": "Visa",
  "country": "US",
  "datePosted": "14",
  "maxItemsPerSearch": 100,
  "includeCompanyRatings": true
}
```

### Example: several city shards plus one specific job

```json
{
  "position": "electrician",
  "locationShards": ["Denver, CO", "Boulder, CO", "Colorado Springs, CO"],
  "startUrls": ["https://www.indeed.com/viewjob?jk=6b86092e2a95d2c2"],
  "maxItemsPerSearch": 300
}
```

## Use cases

- **Job market and salary research** — compare pay by title, city and country with yearly-normalized salary fields and employer salary reports
- **Recruiter and staffing lead generation** — find companies hiring now, with size, revenue, industry and contact details written in the posting
- **Employer reputation research** — compare employers by Indeed rating, review count, category ratings and CEO approval
- **Job board aggregation** — pull deduplicated listings with full descriptions and apply links
- **Competitor hiring intelligence** — track the roles one employer opens with `company`, or paste their company jobs page
- **Remote-work, benefits and freshness analysis** — measure remote share, benefits, reposts and sponsored placements by role or region

## FAQ

**How many jobs can I get from one search?**
Indeed's cursor returns roughly 1,000 fetched rows and then stops, including duplicates; the unique yield is usually lower. `maxItemsPerSearch` is a save cap, not a promise that Indeed has that many reachable rows. To go deeper, add `locationShards` or separate search URLs and keep deduplication on. The run reports `searchFacetTotal`, `searchRetrieved` and `searchCoverage`; the facet number is an upper bound, not the reachable count.

**Why is `searchFacetTotal` much larger than what I received?**
It is Indeed's own count for the search, and its API exposes only the first cursor window of that set. A search reporting 100,000 matches may still return only a few hundred unique jobs. The actor states this in the run status instead of presenting the facet count as delivered data. Per-row coverage is a save-time snapshot, except the last row of each search, which carries the final retrieved count and coverage.

**Why do some jobs have no salary?**
Many employers do not publish pay on Indeed. Salary fields appear only when the employer publishes them, and coverage varies by country: the United States and United Kingdom are usually well covered, Germany much less. `salaryAnnualMin` and `salaryAnnualMax` convert hourly, daily, weekly and monthly pay to a yearly figure. Indeed's own estimated salary is not returned because the app API does not populate it.

**How does the minimum salary filter work?**
Indeed filters natively on the annual salary field, but it also keeps jobs with no salary at all. The actor then re-checks every job and keeps only those whose published range reaches your minimum. Jobs without salary data are excluded when `salaryMin` is set.

**How do I get all jobs from one company?**
Use the `company` input, or search `company:CompanyName` as the position, or paste the company's Indeed jobs page URL. The actor resolves the company name to Indeed's employer key so the filter is native, then verifies the employer on each saved job.

**Does it extract contact details?**
Emails and phone numbers that the employer wrote directly into the job description are saved in `emails` and `phoneNumbers` (international format). Most employers ask candidates to apply through Indeed or their careers site, so only a minority of jobs contain contact details this way.

**Which countries are supported?**
62 Indeed sites, including the United States, United Kingdom, Canada, Australia, India, Germany, France, Japan, Brazil and Mexico. Results come back in the local language with salaries in the local currency, and the locale is pinned to the job's country so salary data is not dropped.

**Why is `isSponsored` missing on some rows?**
Sponsored placement is not part of Indeed's app job API. The actor reads it from the mobile results page, where about 47 jobs are visible per request; a job outside that window keeps the field omitted rather than guessed. Turn `includeSponsored` off for the cheapest run.

**What happens if a pasted job URL is expired or removed?**
The actor first retries the job API, then tries Indeed's mobile job page. If both fail, it saves an error row (`recordType: "error"`) with the job key, URL and reason, so the dataset tells you what happened instead of silently dropping the URL.

**Is this affiliated with Indeed?**
No. This is an independent, third-party actor that reads publicly available job listings. It is not operated by or affiliated with Indeed.
