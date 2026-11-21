# Jobicy Remote Tech and IT Jobs Scraper

Jobicy is a curated remote-jobs board focused on development, data, design, marketing and support roles that can be done from anywhere. This actor queries Jobicy's public job feed and returns clean, structured records — keyword search or direct lookup by job ID/slug — with salary, sector, seniority and geography fields filled in whenever the employer disclosed them.

Note: this actor was built against Jobicy because the original JobServe.com board does not expose a public data feed; Jobicy covers the same remote IT/tech job niche with richer structured data (salary bands, seniority levels, sector tags).

## What this actor does

- Searches the current remote-jobs feed by keyword/tag, geographic region, sector, employment type, seniority level and minimum salary
- Fetches specific jobs directly by their Jobicy ID or slug instead of searching
- Strips HTML from job descriptions and excerpts so you get clean plain text
- Normalizes multi-value sector and job-type tags into a primary field plus a full list when more than one applies
- Stamps every record with a record type and a UTC scrape timestamp
- Omits any field the source job posting didn't provide — no empty strings or nulls in the output

## Output per job

- `jobId` — Jobicy's numeric job identifier
- `jobSlug` — URL-friendly slug used in the listing link
- `title`, `companyName`, `companyLogo`
- `sector` — primary industry sector; `sectors` — full list when a job spans more than one
- `jobType` — employment type (e.g. full-time, contract)
- `location` — geographic location requirement as stated by the employer
- `level` — seniority level
- `excerpt` — short plain-text summary
- `description` — full plain-text job description
- `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod` — only present when the posting discloses pay
- `datePosted` — publication date
- `jobUrl`, `applyUrl`, `sourceUrl` — link to the listing (apply and source currently point to the same URL)
- `recordType` — always `"job"`
- `scrapedAt` — UTC timestamp of the scrape

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` (keyword + filters) or `getJob` (fetch by ID/slug) |
| `query` | string | – | Keyword to match against job title and tags (mode=search) |
| `geo` | string | – | Geographic region filter (e.g. `usa`, `uk`, `europe`, `worldwide`) |
| `location` | string | – | Additional text filter applied to the location field after fetching |
| `sector` | string | – | Industry sector filter (e.g. `dev`, `data-science`, `marketing`) |
| `jobType` | string | – | Employment type filter (`full-time`, `part-time`, `contract`, `freelance`, `internship`) |
| `level` | string | – | Seniority level filter |
| `minSalary` | integer | – | Only include jobs whose maximum salary is at least this (USD/year); jobs without salary data always pass |
| `jobIds` | array | – | Jobicy job IDs or slugs to fetch directly (mode=getJob) |
| `maxItems` | integer | `100` | Maximum number of job records to return (1–10000) |

### Example: search remote Python development roles

```json
{
  "mode": "search",
  "query": "python",
  "sector": "dev",
  "geo": "worldwide",
  "maxItems": 50
}
```

### Example: senior remote jobs in Europe with a salary floor

```json
{
  "mode": "search",
  "geo": "europe",
  "level": "senior",
  "minSalary": 70000,
  "maxItems": 30
}
```

### Example: fetch specific jobs by slug

```json
{
  "mode": "getJob",
  "jobIds": ["42001-senior-python-developer", "12345-react-engineer"]
}
```

## Use cases

- **Remote-work job boards** mirror or supplement their listings with Jobicy's tech-focused feed
- **Salary research** compare disclosed remote salary bands across sectors and seniority levels
- **Recruiters** build a shortlist of currently-open remote roles matching a tech stack keyword
- **Labour-market analysts** track how many remote dev/data/design roles are posted by region over time
- **Candidates** set up keyword and salary-floor filters to monitor new openings in their field

## FAQ

**Is this the same as JobServe.com?**
No. JobServe.com does not expose a public data feed, so this actor targets Jobicy, a remote-jobs board covering the same IT/tech niche with richer structured salary and sector data. It is not affiliated with either site.

**Why do some jobs have no salary fields?**
Jobicy only shows salary data when the employer disclosed it. Jobs without a stated range simply omit `salaryMin`/`salaryMax` rather than showing a null or zero.

**What's the difference between `sector` and `sectors`?**
`sector` is always the primary sector for the job. `sectors` only appears when the posting is tagged with more than one sector, listing all of them.

**How do I fetch a specific job I already know about?**
Switch `mode` to `getJob` and list its ID or slug in `jobIds` to fetch those jobs directly instead of running a keyword search. Any `query`/`location`/`jobType`/`level`/`minSalary` filters you've also set still apply to the matched jobs, so leave them blank if you just want the listed IDs returned unconditionally.

**Does the `location` filter duplicate `geo`?**
No — `geo` selects one of Jobicy's own region categories server-side, while `location` is an extra free-text filter applied afterward against whatever location string the job actually displays.

**How current are the listings?**
Every run re-queries the live feed, so results reflect whatever is posted on Jobicy at run time.
