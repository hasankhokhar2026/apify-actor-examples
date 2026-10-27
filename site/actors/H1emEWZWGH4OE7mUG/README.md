# Wellfound Startup Jobs Finder with Pay & Remote Filters

Pull live startup job listings from Wellfound (formerly AngelList Talent) and narrow them down by title, keyword, location, remote status, job type, experience level, salary range, and company name — all in one run.

## What this actor does

- Reads Wellfound's public jobs pages (the default `/jobs` feed, or any URLs you supply) and extracts the jobs embedded in each page; it does not click through to further result pages
- Filters the collected jobs by title/keyword text, location, remote-only, job type, experience level, salary range, and company name lists
- Sorts results by posting date (newest or oldest first) when requested
- Links every job back to its startup, including the company's logo and Wellfound profile URL
- Omits any field Wellfound didn't provide for a given job, so records only contain data that was actually found

## Output per job

| Field | Description |
|---|---|
| `type` | Always `"wellfound_job"` |
| `jobId` | Wellfound's internal job listing ID |
| `title` | Job title |
| `slug` | Job's URL slug |
| `jobUrl` | Direct link to the job listing on Wellfound |
| `compensation` | Compensation text as published (salary range and/or equity) |
| `remote` | `true`/`false` when Wellfound flags the job as remote or not |
| `locations` | List of location names for the role |
| `companyId` | Startup's internal Wellfound ID |
| `companyName` | Startup name |
| `companySlug` | Startup's URL slug |
| `companyUrl` | Link to the startup's Wellfound profile |
| `companyLogo` | URL of the startup's logo image |
| `postedAt` | When the listing went live, when Wellfound exposes it |
| `scrapedAt` | Timestamp when the record was scraped |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `startUrls` | array | – | Wellfound URLs to read; `https://wellfound.com/jobs` is used when empty. Supports query params such as `?remote=true`. Each URL contributes the jobs on that one page; duplicates across URLs are removed. |
| `jobTitle` | string | – | Only keep jobs whose title contains this phrase (case-insensitive) |
| `keyword` | string | – | Only keep jobs matching this keyword across title, company, location and compensation text |
| `location` | string | – | Only keep jobs whose location list contains this text (case-insensitive) |
| `remoteOnly` | boolean | `false` | Only keep jobs flagged as remote. Also adds `remote=true` to `/jobs` URLs that don't already mention remote |
| `jobType` | string | `any` | `any`, `full-time`, `part-time`, `contract` or `internship`, matched as keywords in the job's text (see FAQ) |
| `experience` | string | `any` | `any`, `junior`, `mid`, `senior` or `executive`, matched as keywords in the job's text (see FAQ) |
| `minSalary` | integer | `0` | Keep jobs whose parsed pay range reaches at least this amount (0 = no minimum) |
| `maxSalary` | integer | `0` | Keep jobs whose parsed pay range starts at or below this amount (0 = no maximum) |
| `includeNoSalary` | boolean | `true` | When false, jobs with no parseable dollar amount are dropped once a salary bound is set |
| `companyCategories` | array | – | Keep jobs whose company name or slug contains one of these words. This is a text match on the company name, not a Wellfound industry category |
| `includeCompanies` | array | – | Only keep jobs whose company name or slug contains one of these values |
| `excludeCompanies` | array | – | Drop jobs whose company name or slug contains one of these values |
| `sort` | string | `none` | Order results by posted date: `newest`, `oldest`, or `none` (page order). Jobs without a posted date sort last for `newest` and first for `oldest` |
| `maxItems` | integer | `50` | Maximum number of jobs to return after filtering (1–500) |

### Example: remote engineering roles with a salary floor

```json
{
  "jobTitle": "engineer",
  "remoteOnly": true,
  "minSalary": 120000,
  "includeNoSalary": false,
  "maxItems": 50
}
```

### Example: senior roles at specific startups

```json
{
  "experience": "senior",
  "includeCompanies": ["ramp", "vercel"],
  "sort": "newest",
  "maxItems": 30
}
```

### Example: minimal run against the default feed

```json
{
  "maxItems": 10
}
```

## Use cases

- **Startup job hunting** — filter by remote status, seniority and salary to shortlist relevant roles fast
- **Compensation research** — compare published salary and equity ranges across companies and roles
- **Recruiter sourcing** — find startups actively hiring for a specific role or skill set
- **Market tracking** — watch hiring volume at a list of target companies over time
- **Company-name scouting** — surface jobs from startups whose name contains a word such as "labs" or "ai"

## FAQ

**Do I need to log in to Wellfound?**
No. The actor reads Wellfound's public jobs pages; no account or cookies are required.

**Why are `postedAt` or `compensation` missing on some jobs?**
Not every listing publishes a posting date or compensation figure. When Wellfound doesn't show a value, that field is left out of the record instead of being filled with a placeholder.

**How are `jobType` and `experience` matched if Wellfound doesn't expose structured fields for them?**
The actor looks for keywords (for example "senior", "lead" or "staff" for `senior`, or "contract" and "freelance" for `contract`) in the job's title, company name, locations and compensation text. A job is only dropped when it mentions another level or type and not the one you picked; jobs that mention none of them are kept. Treat these as loose filters, not Wellfound categories.

**What does `includeNoSalary` control?**
It only applies once you set `minSalary` or `maxSalary`. With it left on (default), jobs without a dollar amount in their compensation text still pass through; turn it off to require one. Amounts are read from text such as `$120k – $150k`; figures under 10,000 are treated as thousands.

**Can I combine multiple filters?**
Yes — all filters in the input are applied together, so a run can combine remote-only, a salary floor, and a company allow-list in one go.

**Is this affiliated with Wellfound?**
No. This actor is an independent tool that reads Wellfound's public pages and is not affiliated with, endorsed by, or sponsored by Wellfound or AngelList.

**Why might results be fewer than `maxItems`?**
Each URL contributes only the jobs embedded in that single page, which is a limited set. If your filters are narrow, fewer jobs qualify. Add more Wellfound URLs (for example different query parameters) to widen the pool; the actor returns everything that qualifies rather than padding the output.
