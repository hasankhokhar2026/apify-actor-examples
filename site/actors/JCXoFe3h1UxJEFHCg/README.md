# Indeed Global Job Scraper with Company Salary Reports

Search Indeed's 62 country sites by keyword and location, by Indeed's own filters, or by pasting Indeed URLs, and get back full job descriptions, structured salaries, benefits, exact location with coordinates, recruiter contact details found in the posting, and the employer's own Indeed company profile — rating, review count, category ratings, and average salaries by job title. No Indeed account, login, or cookies needed.

## What this actor does

- Searches by position/keywords and location, or accepts Indeed search URLs, company job pages, job URLs, and bare job IDs
- Applies Indeed's own filters: job type, remote/hybrid/in-person, date posted, experience level, education level, minimum salary, easy apply, and search radius
- Returns the full job description (never a shortened snippet), with structured salary fields normalized to a yearly figure for comparison across pay periods
- Optionally enriches each employer with their Indeed rating, review count, five category ratings, CEO approval, founding year, work-wellbeing score, and average salaries by job title
- Picks out any email addresses or phone numbers an employer wrote directly into the job description
- Deduplicates jobs found by more than one search within the same run
- Fields a job or company doesn't have data for (e.g. no salary, no company rating) are left out of that record

## Output per job

| Group | Fields |
|---|---|
| Job | `id`, `positionName`, `normalizedTitle`, `url`, `description`, `descriptionHtml` (when `includeDescriptionHtml` is on), `jobType`, `jobTypes`, `remoteWorkType`, `experienceLevel`, `educationLevels`, `workSchedule`, `occupations`, `attributes`, `language`, `source` |
| Salary | `salary` (as shown on Indeed), `salaryMin`, `salaryMax`, `salaryPeriod`, `salaryCurrency`, `salaryAnnualMin`, `salaryAnnualMax`, `salarySource`, `payTypes` |
| Benefits & schedule | `benefits`, `schedules` |
| Location | `location`, `streetAddress`, `neighborhood`, `city`, `county`, `state`, `stateName`, `postalCode`, `countryCode`, `countryName`, `latitude`, `longitude` |
| Dates | `postedAt`, `postingDateParsed`, `datePostedISO`, `datePublishedISO`, `validThrough`, `isExpired` |
| Applying & contacts | `easyApply`, `externalApplyLink`, `emails`, `phoneNumbers` (international format), `urgentlyHiring`, `highVolumeHiring` |
| Company ratings (when `includeCompanyRatings` is on) | `rating`, `reviewsCount`, `companyRatings` (work-life balance, compensation and benefits, job security and advancement, management, culture), `companyCeoApproval`, `companyFounded`, `companySalaries` (average pay by job title with category, period, and reported-salary count), `companyWorkWellbeing` (happiness, purpose, satisfaction, stress-free, and more 0–100 scores) |
| Company | `company`, `companyId`, `companyUrl`, `companyLogo`, `companySize`, `companyRevenue`, `companyIndustry`, `companyWebsite`, `companyDescription`, `companyCeo`, `companyHeadquarters`, `companyInfo` (addresses, stock symbol, social links, and more) |
| Context | `searchQuery`, `searchLocation`, `country`, `scrapedAt` |

### Example output row (shortened)

```json
{
  "id": "6b86092e2a95d2c2",
  "positionName": "Sr. Machine Learning Engineer",
  "company": "DocuSign",
  "url": "https://www.indeed.com/viewjob?jk=6b86092e2a95d2c2",
  "city": "Seattle",
  "state": "WA",
  "salary": "$178,900 - $262,825 a year",
  "salaryAnnualMin": 178900,
  "salaryAnnualMax": 262825,
  "jobTypes": ["Permanent", "Full-time"],
  "remoteWorkType": "Hybrid",
  "benefits": ["Paid parental leave", "Health insurance", "Paid time off"],
  "rating": 3.5,
  "reviewsCount": 139,
  "companySalaries": [
    { "title": "Software Engineer", "salary": "$170,461", "amount": 170461, "period": "YEARLY", "reportedSalaries": 17 }
  ],
  "scrapedAt": "2026-10-08T06:59:29Z"
}
```

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `position` | string | – | Job title, skill, or keywords. Supports `company:Name`, `title:(…)`, quotes, `OR`, and `-exclusions` |
| `location` | string | – | City, region, or postal code; leave empty to search the whole country. `remote` (or `anywhere`, `work from home`) is treated as the remote workplace filter instead of a place |
| `country` | string | `US` | Indeed country site to search (62 countries) |
| `maxItemsPerSearch` | integer | `100` | Max jobs to save per search, i.e. the keyword search and each search URL (Indeed shows up to ~1,000 per search). Job URLs and IDs are always all fetched |
| `jobType` | string | `""` (any) | `fulltime`, `parttime`, `contract`, `temporary`, `internship`, `permanent`, `seasonal`, `perdiem`, `freelance`, `apprenticeship`, `volunteer` |
| `workplaceType` | string | `""` (any) | `remote`, `hybrid`, or `inPerson` |
| `datePosted` | string | `""` (any time) | `1`, `3`, `7`, `14`, or `30` (days) |
| `experienceLevel` | string | `""` (any) | `noExperience`, `entry`, `mid`, `senior` |
| `educationLevel` | string | `""` (any) | `noDegree`, `highSchool`, `associate`, `bachelor`, `master`, `doctoral` |
| `salaryMin` | integer | – | Minimum yearly salary in the country's currency; jobs with no salary are excluded when set |
| `easyApplyOnly` | boolean | `false` | Only jobs you can apply to directly on Indeed |
| `radius` | integer | – | Search radius around `location` (Indeed's own default is 25); ignored without a location |
| `radiusUnit` | string | `miles` | `miles` or `kilometers` |
| `sort` | string | `relevance` | `relevance` or `date` (newest first) |
| `startUrls` | array | – | Indeed search URLs, company job pages (`/cmp/Name/jobs`), job URLs, or job IDs. The filters chosen above are added to search URLs that don't set their own |
| `includeCompanyRatings` | boolean | `true` | Add the employer's rating, review count, category ratings, CEO approval, founding year, wellbeing score, and average salaries by job title |
| `includeDescriptionHtml` | boolean | `false` | Also save the description as HTML (the plain-text `description` is always included) |
| `saveOnlyUniqueItems` | boolean | `true` | Save each job once even when several searches find it |

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
  "maxItemsPerSearch": 500
}
```

### Example: nurse jobs on the UK site

```json
{ "position": "nurse", "location": "London", "country": "GB", "maxItemsPerSearch": 300 }
```

### Example: a filtered search URL plus one specific job

```json
{
  "startUrls": [
    "https://www.indeed.com/jobs?q=electrician&l=Denver%2C+CO&jt=contract&fromage=14",
    "https://www.indeed.com/viewjob?jk=6b86092e2a95d2c2"
  ]
}
```

## Use cases

- **Job market and salary research** — compare pay by title, city, and country using normalized yearly salaries and employer salary reports
- **Lead generation for recruiters and staffing agencies** — find companies hiring now, with size, revenue, industry, and recruiter contact details found in listings
- **Employer reputation research** — compare employers by Indeed rating, review count, category ratings, and CEO approval
- **Job board aggregation** — pull deduplicated listings with full descriptions and apply links
- **Competitor hiring intelligence** — track which roles a company is opening with a `company:Name` search
- **Remote-work and benefits analysis** — measure remote/hybrid share, benefits, and schedules by role or region

## FAQ

**How many jobs can I get per search?**
Indeed shows up to about 1,000 jobs for a single search. To collect more, run several searches with different locations, job types, date ranges, or keywords as separate entries in `startUrls` — with `saveOnlyUniqueItems` on, jobs found by more than one search are still saved once. If the run approaches its timeout, it stops starting new pages and keeps everything saved so far.

**Why do some jobs have no salary?**
Many employers don't publish pay on Indeed, so salary fields only appear when Indeed shows one for that job. `salaryAnnualMin`/`salaryAnnualMax` convert hourly, daily, weekly, and monthly pay to a yearly figure so jobs are easy to compare.

**How does the minimum salary filter work?**
Only jobs whose salary range reaches your minimum yearly amount (in the country's currency) are kept — using the employer's own salary or, when the employer gives none, Indeed's own estimate (`salarySource` tells you which). Jobs without any salary data are excluded entirely.

**How do I get all jobs from one company?**
Search `company:CompanyName` as the position (e.g. `company:Amazon`), optionally with a location, or paste the company's Indeed jobs page URL into `startUrls`. Single jobs can be added the same way, as a job URL (`…/viewjob?jk=…`, from any supported country site) or a bare job ID.

**Does it extract contact details?**
Emails and phone numbers that the employer wrote directly into the job description are saved in `emails` and `phoneNumbers` (international format). Most employers ask candidates to apply through Indeed or their own careers site, so only a minority of jobs include contact details this way.

**Which countries are supported?**
62 Indeed sites, including the United States, United Kingdom, Canada, Australia, India, Germany, France, Japan, Brazil, and Mexico. Results come back in the local language with salaries in the local currency, same as browsing the local Indeed site directly.

**Is it legal to scrape Indeed?**
This actor collects publicly available job listings. Listings can contain personal data (a recruiter's name, email, or phone number) that laws like GDPR and CCPA cover, so use that data only for a legitimate purpose and in line with Indeed's own terms. If you're unsure, consult a lawyer.

**Why might a search return nothing?**
The keywords may not match any jobs in that location, or the filters may be too strict together; the run then finishes with an empty dataset and a status message saying no jobs matched. If Indeed rejected the search or couldn't be reached and nothing at all was saved, the run is marked as failed with a message explaining which, so you can retry.

**What if I leave the input empty, or set only filters?**
With filters (or a non-US `country`) but no position, location or URLs, the actor searches every job in that country matching the filters. A completely empty input runs a small example search (`web developer` in `San Francisco`) so you can see the output format.

**Is this affiliated with Indeed?**
No. This is an independent, third-party actor that reads Indeed's publicly available job listings; it is not operated by or affiliated with Indeed.
