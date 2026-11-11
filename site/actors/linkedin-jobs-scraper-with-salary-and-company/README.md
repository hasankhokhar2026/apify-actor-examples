# LinkedIn Jobs Scraper with Salary & Company Enrichment

Pull job listings from LinkedIn's public job search without logging in. Enter keywords and a location, apply optional filters, and get back structured job data with parsed salary ranges, inferred seniority, visa-sponsorship mentions, and hiring-company details — ready for analysis, lead generation, or job market research.

## What this actor does

This actor extracts job listings from LinkedIn's public job search. Simply enter keywords and a location, apply optional filters, and it returns structured job data ready for analysis, lead generation, or job market research.

## Features

- **Search by keywords and location** — Find jobs matching any title, skill, or company name
- **Full job descriptions** — Get both HTML and plain text versions for NLP or analysis
- **Rich metadata** — Seniority level, employment type, job function, industry, salary, applicant count
- **Advanced filters** — Time posted, experience level, job type, remote/hybrid/on-site, Easy Apply, company, salary band, and more
- **Salary normalization** — Structured min/max/currency/interval plus a normalized yearly figure, with false-positive sanity-checking
- **Inferred seniority & years of experience** — Falls back to a title/description heuristic (clearly flagged as inferred) when LinkedIn's own seniority field is missing
- **Visa sponsorship & ATS detection** — Flags whether a posting mentions visa sponsorship (negation-aware) and which applicant-tracking platform the apply link resolves to
- **Incremental-run friendly** — Exclude previously-seen job IDs or filter by title keywords without re-scraping everything
- **Direct URL support** — Paste LinkedIn search URLs with your own custom filters
- **Automatic deduplication** — No duplicate listings when combining multiple searches
- **No login required** — Uses LinkedIn's public job search, no account or cookies needed
- **Proxy included by default** — Requests route through Apify's proxy automatically; no extra setup needed on your part

## Use Cases

- **Job market research** — Analyze hiring trends, salary ranges, and in-demand skills
- **Lead generation** — Find companies actively hiring in your target industry
- **Competitive analysis** — Monitor competitor hiring patterns and open roles
- **Career monitoring** — Track new job postings matching your criteria
- **Recruitment intelligence** — Identify companies expanding in specific locations or functions
- **Salary benchmarking** — Compare compensation data across companies and locations

## Input

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `keywords` | String | – | Job title, skills, or company to search (e.g., "software engineer", "data scientist") |
| `location` | String | – | City, state, country, or "remote". **Always in English** — e.g. "Germany", not "Deutschland" — LinkedIn does not resolve non-English place names. Ignored if `locations` (plural) is set. |
| `locations` | Array | – | Run the same `keywords` against several locations in one go (e.g. `["California", "Texas", "New York"]`) and combine the deduplicated results — the way to get more than LinkedIn's ~1,000-result cap for one keyword. Overrides `location`. |
| `maxItems` | Integer | `100` | Max job listings to scrape (1-1000). LinkedIn limits ~1000 results per query — use `locations` to combine multiple queries for more. |
| `scrapeJobDetails` | Boolean | `true` | Fetch full descriptions, seniority, employment type, etc. Disable for faster runs. |
| `enrichmentDepth` | String (select) | `standard` | `standard` is fast and covers everything above. `full` also fetches similar jobs, related searches, and cleaner company/industry IDs, but is ~5-7x slower per job and doesn't include the Apply URL. |
| `timePosted` | String (select) | `""` | Filter: Past 24 hours (`r86400`), Past week (`r604800`), Past month (`r2592000`). Applied directly by LinkedIn. |
| `experienceLevel` | String (select) | `""` | Filter: Internship, Entry, Associate, Mid-Senior, Director, Executive. Applied by this actor after fetching each job's detail page (LinkedIn no longer filters this server-side) — may increase run time. |
| `jobType` | String (select) | `""` | Filter: Full-time, Part-time, Contract, Temporary, Internship, Volunteer, Other. Same as above — applied after detail fetch. |
| `workType` | String (select) | `""` | Filter: On-site, Remote, Hybrid. Best-effort only — LinkedIn no longer exposes a reliable on-site/remote/hybrid signal on public pages, so this rarely narrows results; check the job title/description for the real work arrangement. |
| `easyApply` | Boolean | `false` | Only show jobs with LinkedIn Easy Apply. Applied directly by LinkedIn. |
| `industry` | Array (multi-select) | `[]` | Dropdown covering all of LinkedIn's official industry categories — select one or more. Applied by this actor after fetching job details and company data (LinkedIn no longer honors this filter server-side) — matched against each job's real company industry, so it genuinely narrows results rather than being decorative. |
| `companyIds` | Array | `[]` | Restrict to specific LinkedIn company IDs. Applied directly by LinkedIn. |
| `function` | String (select) | `""` | Dropdown covering all 36 of LinkedIn's official job-function categories (Engineering, Sales, Accounting/Auditing, etc). Applied by this actor after fetching each job's detail page — may increase run time. |
| `salaryMin` | Integer | `0` | LinkedIn salary band (1=$40k+ ... 9=$200k+). Applied after detail fetch, only for jobs with a posted yearly salary. |
| `under10Applicants` | Boolean | `false` | Only show jobs with fewer than 10 applicants. Applied directly by LinkedIn. |
| `language` | String (select) | `en` | Accept-Language for LinkedIn's response — does not translate the `location` field. |
| `searchUrls` | Array | – | Direct LinkedIn job search URLs with filters pre-applied. Overrides `keywords` and `location`. |
| `excludeJobIds` | Array | – | Skip specific job IDs (e.g. from a previous run's `id` field) — useful for incremental scraping. |
| `includeTitleKeywords` | Array | – | Only keep jobs whose title contains at least one of these keywords (case-insensitive). |
| `excludeTitleKeywords` | Array | – | Skip jobs whose title contains any of these keywords (case-insensitive). |
| `proxyConfiguration` | Object | `{"useApifyProxy": true}` | Used for every request by default — LinkedIn's guest job pages block requests from an unproxied IP on nearly every attempt. |

**Note:** At least one of `keywords` or `searchUrls` must be provided.

### Example input — Basic search

```json
{
    "keywords": "software engineer",
    "location": "United States",
    "maxItems": 50
}
```

### Example input — Filtered search

```json
{
    "keywords": "data scientist",
    "location": "New York",
    "jobType": "F",
    "workType": "2",
    "experienceLevel": "4",
    "timePosted": "r604800",
    "maxItems": 100
}
```

### Example input — Direct URL

```json
{
    "searchUrls": [
        { "url": "https://www.linkedin.com/jobs/search/?keywords=python%20developer&location=London&f_JT=F&f_WT=2" }
    ],
    "maxItems": 50
}
```

## Output

Each job listing produces one item in the output dataset. Empty/unavailable fields are omitted rather than returned as `null`.

| Field | Type | Description |
|-------|------|-------------|
| id | String | LinkedIn's unique job identifier |
| title | String | Job position title |
| companyName | String | Hiring company name |
| companyUrl, companyId, companyLogo | String | Company page, LinkedIn company ID, and logo URL |
| companyIndustry, companyFollowersCount, companySize | String/Number | Company metadata, fetched directly from each unique company's own LinkedIn page (see below) |
| companyWebsite, companyType, companyHeadquarters, companySpecialties, companyDescription | String/Array | Fetched directly from each unique company's own LinkedIn page — see below |
| location, workplaceType, remoteAllowed | String/Boolean | Job location and remote/hybrid/on-site signal |
| salary | String | Raw salary text as shown by LinkedIn (e.g., "$150,000.00/yr - $200,000.00/yr") |
| salaryRange | Object | Structured `{min, max, currency, interval, minYearly, maxYearly}` parsed from `salary`, sanity-checked to reject implausible parses |
| postedDate, postedAt, postedDateText | String | Posting date (ISO where available) and relative text (e.g., "3 days ago") |
| applicantCount, applicantInsights | String/Array | Applicant count text and any early-applicant/recent-activity insights |
| easyApply, isReposted | Boolean | Easy Apply and reposted-listing flags |
| jobUrl, applyUrl | String | LinkedIn job page and apply destination. `applyUrl` is only available with the default Standard enrichment depth. |
| atsPlatform | String | Applicant-tracking platform resolved from `applyUrl` (Workday, Greenhouse, Lever, etc.), when detectable |
| descriptionHtml, descriptionText | String | Full job description, HTML and plain text |
| seniorityLevel, employmentType, jobFunction(s), industries/industriesList | String/Array | Criteria as LinkedIn presents them |
| inferredSeniorityLevel | String | LinkedIn's own seniority when available, otherwise a title-based inference |
| experienceYearsMin, experienceYearsMax | Number | Years of experience parsed from the description text (e.g., "5+ years"), when stated |
| visaSponsorshipMentioned, visaSponsorshipPhrase | Boolean/String | Whether the description mentions visa sponsorship — `true` if offered, `false` if explicitly **not** offered, omitted if not mentioned |
| responsibilities, qualifications, preferredQualifications | Array | Bulleted description sections, when the posting uses a recognizable "What You'll Do"/"Qualifications"-style heading — best-effort, present on most but not all postings |
| skillsRequired, benefits | Array | Listed skills and benefits, when present |
| recruiter | Object | Recruiter/poster card `{name, title, profileUrl}`, when shown |
| industryIds, titleId, similarJobs, peopleAlsoViewed, similarSearches, titleCategoryLabel, titleCategoryUrl | — | Only present with **Detail Enrichment Depth = Full** — see below |
| scrapedAt | String | ISO timestamp when data was collected |

### Full enrichment depth: extra fields

Setting **Detail Enrichment Depth** to `full` fetches LinkedIn's richer job page and adds:

- `similarJobs[]` / `peopleAlsoViewed[]` — related job cards `{jobId, title, companyName, location, postedDateText, jobUrl}`
- `similarSearches[]` — related search terms with live open-job counts `{searchTerm, searchUrl, openJobsCount}`
- `industryIds`, `titleId` — LinkedIn's own internal taxonomy IDs, cleaner than the URL-derived `companyId`
- `titleCategoryLabel` / `titleCategoryUrl` — LinkedIn's own normalized title-category grouping for this posting

This mode does not include `applyUrl` (LinkedIn's Apply button there is a client-side action with no static link) and is roughly 5-7x slower per job — use it only when you need the extra fields.

### Company page enrichment

Every run fetches each unique company's own LinkedIn page (once per company — jobs from the same employer share one fetch, run concurrently) and adds:

- `companyWebsite` — the company's real external website (unwrapped from LinkedIn's redirect link)
- `companyType` — e.g. "Public Company", "Privately Held"
- `companyHeadquarters` — the company's stated HQ location
- `companySpecialties[]` — the list of specialties LinkedIn shows on the company page
- `companyDescription` — the company's tagline
- Reliable `companyIndustry`, `companyFollowersCount`, `companySize`, and `companyLogo`, taken directly from the company page rather than scraped incidentally off the job page

This adds one extra request per unique company in your results, so a run with many different employers takes longer than one dominated by a few large companies.

### Sample output

```json
{
    "id": "3876543210",
    "title": "Senior Software Engineer",
    "companyName": "Google",
    "companyUrl": "https://www.linkedin.com/company/google",
    "companyId": "1441",
    "location": "Mountain View, CA",
    "salary": "$150,000.00/yr - $200,000.00/yr",
    "salaryRange": {
        "min": 150000,
        "max": 200000,
        "currency": "USD",
        "interval": "yearly",
        "minYearly": 150000,
        "maxYearly": 200000
    },
    "postedDate": "2026-03-20",
    "postedDateText": "4 days ago",
    "applicantCount": "Over 200 applicants",
    "jobUrl": "https://www.linkedin.com/jobs/view/3876543210",
    "applyUrl": "https://www.linkedin.com/jobs/view/3876543210",
    "descriptionHtml": "<p>We are looking for a Senior Software Engineer...</p>",
    "descriptionText": "We are looking for a Senior Software Engineer to join our team...",
    "seniorityLevel": "Mid-Senior level",
    "inferredSeniorityLevel": "Mid-Senior level",
    "experienceYearsMin": 5,
    "employmentType": "Full-time",
    "jobFunction": "Engineering and Information Technology",
    "industries": "Technology, Information and Internet",
    "scrapedAt": "2026-03-24T10:30:00.000000+00:00"
}
```

## How to use

### Quick start

1. Enter a job title or keyword in the **Search Keywords** field
2. Enter a location (city, country, or "remote")
3. Set **Maximum Jobs** to control how many listings to scrape
4. Click **Start** and wait for results

### Use filters for targeted results

Apply filters like **Job Type** (Full-time), **Experience Level** (Mid-Senior), or **Time Posted** (Past week) to narrow your search. This mirrors the filters available on LinkedIn's job search page.

### Use LinkedIn search URLs

1. Go to [LinkedIn Jobs](https://www.linkedin.com/jobs/) in your browser
2. Search for jobs and apply any filters you want
3. Copy the URL from your browser's address bar
4. Paste it into the **Search URLs** field

### Combine both modes

You can provide both keywords and search URLs. The scraper processes all searches and deduplicates results automatically.

## How many jobs can I scrape?

LinkedIn limits public search results to approximately **1,000 jobs per unique search query**. To get more results:

- Use **Locations (multiple)** to run the same keywords against several locations in one run (e.g. `["California", "Texas", "New York"]`) — results are combined and deduplicated automatically, the single best way to beat the cap
- Use different keyword variations (e.g., "software engineer" and "software developer")
- Apply different filters to get distinct result sets
- Use multiple search URLs with different parameters

## Tips

- **Start small** — Use `maxItems: 10` for your first run to verify the output format
- **Disable details for speed** — Set `scrapeJobDetails: false` for a 5-10x faster run when you only need titles, companies, and locations
- **Use specific keywords** — Narrow keywords produce more relevant results
- **Combine with location** — Adding a location improves result quality significantly

## FAQ

**Do I need a LinkedIn account?**
No. The scraper uses LinkedIn's public job search which is accessible without any login.

**Do I need a proxy?**
No setup needed — Apify's proxy is used automatically for every run, since LinkedIn's guest job pages block most requests from an unproxied IP. If a request still gets blocked, the actor escalates to a stronger proxy tier and retries automatically.

**How fast is the scraper?**
With job details enabled: approximately 25 jobs per 15-20 seconds. Without details: 25 jobs per 3-5 seconds.

**Why are some fields empty?**
Fields like `salary` and `applicantCount` depend on whether the employer provided that information. LinkedIn only shows salary when the employer explicitly includes a pay range in the listing.

**What is "Scrape Full Job Details"?**
When enabled (default), the scraper visits each job's detail page to get the full description, seniority level, employment type, job function, and industry. Disabling it returns only the data visible in search results (title, company, location, date, salary).

**Can I scrape jobs from a specific company?**
Yes. Search for the company name as a keyword, or use the **Company IDs** input with the company's numeric LinkedIn ID (found in its `/company/{id}/` URL) — this filter is applied directly by LinkedIn, so it's exact.

**Can I run this repeatedly without re-scraping the same jobs?**
Yes. Save the `id` values from a previous run and pass them as **Exclude Job IDs** on the next run to only fetch newly-posted jobs. Combine with **Include/Exclude Title Keywords** to narrow further without needing a full LinkedIn filter.

**Why did I get fewer jobs than maxItems?**
LinkedIn may have fewer matching jobs than your limit, or the search may have hit LinkedIn's ~1000 result cap. Try broader keywords or different locations. If you set **Experience Level**, **Job Type**, **Work Type**, **Job Function**, **Industry**, or **Minimum Salary**, this is also expected more often than with other filters — LinkedIn no longer applies these server-side, so this actor fetches extra candidates and filters them itself; if very few jobs match, fewer than your limit may be genuinely available within a reasonable fetch window.

**Are `companyFollowersCount` and `companySize` reliable?**
Yes. Every run fetches each unique company's own LinkedIn page directly (once per company, not per job) and returns the real numbers, plus website, headquarters, company type, and specialties.

**How do I get more than 1,000 jobs for one search?**
LinkedIn caps any single keyword+location query at roughly 1,000 results. Use **Locations (multiple)** to run the same **Job Keywords** against several locations in one run (e.g. `["California", "Texas", "New York"]`) — results are combined and deduplicated automatically, the same way multiple **LinkedIn Search URLs** already work.

**Are the salary/experience/seniority/visa fields exact, or inferred?**
`salary` and `seniorityLevel` (etc.) are LinkedIn's own stated values when the employer provided them. `salaryRange` is a structured parse of that same text with sanity-checking (implausible values are dropped rather than returned wrong) plus a normalized `minYearly`/`maxYearly` for cross-comparison across pay periods. `inferredSeniorityLevel` uses LinkedIn's own field when available and only falls back to a job-title keyword heuristic when it's missing — compare it against `seniorityLevel` if you need to know which. `experienceYearsMin`/`Max` and `visaSponsorshipMentioned` are both parsed from the job description text with pattern matching, including explicit negation-handling for visa sponsorship (a posting that says it will **not** sponsor visas is never reported the same as one that will) — they're omitted, not guessed, when the description doesn't mention either topic.

**What does "Detail Enrichment Depth: Full" add, and is it worth the extra time?**
It's worth it only if you specifically need related-jobs data, related searches, or the cleanest possible company/industry IDs — otherwise stick with Standard. Full fetches a much larger page per job (roughly 7x the data, 5-7x the time) to add `similarJobs`, `peopleAlsoViewed`, `similarSearches`, and `titleCategory` fields, and it does not return `applyUrl` (LinkedIn doesn't expose a static apply link on that page).

**Why are `salary`, `benefits`, `skillsRequired`, and `visaSponsorshipMentioned` empty on most jobs?**
Because most employers genuinely don't include that information in the posting — LinkedIn itself only shows salary on a minority of listings outside pay-transparency-mandated regions, and most postings never mention benefits, a skills list, or visa sponsorship at all. This actor never fabricates a value for these — they're omitted rather than guessed, so an empty field means the data wasn't there to extract, not a scraping failure. `responsibilities`/`qualifications`/`preferredQualifications` and `inferredSeniorityLevel`, by contrast, are actively-extracted fields with retry/fallback logic behind them — genuinely absent far less often.

**How does the Industry filter actually work?**
LinkedIn's own industry search parameter is dead server-side (confirmed live — it no longer narrows results at all), so this actor re-implements it itself: after fetching each job's details and company page, it matches your selected industries against that job's real company industry. This means the Industry filter always requires **Scrape Job Details** (enabled automatically if you set it) and takes longer than a plain search, but it genuinely narrows results using real company data instead of a non-functional LinkedIn parameter.
