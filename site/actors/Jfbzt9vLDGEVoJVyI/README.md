# Naukri.com Job Listings Extractor with Salary & Skills

Naukri.com is one of India's best-known job boards, and this actor turns any search on it into structured data. Paste a search URL or fill in keyword/location/salary filters, and get back one record per job posting with company, pay, skills and recruiter detail.

## What this actor does

- Scrapes job listings either from a pasted Naukri search URL or from structured filter fields (keyword, location, experience, salary, job age, job type, work mode).
- Returns company detail alongside each job, including AmbitionBox rating and review count when Naukri publishes one for that employer.
- Pulls the skill tags Naukri attaches to each posting, along with industry and role category.
- Captures posting freshness (Naukri's relative label plus an absolute creation timestamp when Naukri provides one), vacancy count, and application count.
- Omits any field Naukri didn't supply for a given listing, so records never carry empty placeholders.

## Output per job

| Field | Description |
|---|---|
| `id` | Naukri's internal job ID. |
| `title` | Job title as posted. |
| `url` | Full URL of the job listing on Naukri. |
| `companyName` | Hiring company's name. |
| `companyId` | Naukri's internal company ID. |
| `companyRating` | AmbitionBox rating out of 5, when available for the company. |
| `companyReviewCount` | Number of AmbitionBox reviews behind that rating. |
| `location` | Job location(s); may list several cities. |
| `experience` | Required experience range, as shown on Naukri. |
| `salary` | Salary range as displayed on the listing. |
| `description` | Job description snippet. |
| `skills` | Skill tags attached to the posting. |
| `industry` | Industry category. |
| `role` | Job role category/sub-function. |
| `jobTypeFlags` | Badges such as `premium`, `easy_apply`, or `walk_in`. |
| `postedDate` | Relative posting age as shown on Naukri (e.g. "2 days ago"). |
| `postedAt` | Absolute posting timestamp (UTC), taken from Naukri's own creation time for the job when it is provided. |
| `logoUrl` | Company logo image URL. |
| `vacancies` | Number of open vacancies on the posting. |
| `applyCount` | Number of applicants shown on the posting. |
| `recruiterName` | Recruiter's name, when Naukri lists one. |
| `scrapedAt` | UTC timestamp of when the record was scraped (always present). |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchUrl` | String | – | A Naukri.com search URL to scrape; its job-title/location slug and `k`/`l`/`experience`/`jobAge` query parameters are parsed automatically. Salary, job type, work mode and sort are not read from the URL — set those via their own fields below. |
| `maxItems` | Integer | `50` | Maximum number of job listings to return. |
| `keyword` | String | – | Job title or keyword. If `searchUrl` is also set, this overrides the keyword parsed from the URL. |
| `location` | String | – | City name (e.g. `bangalore`, `delhi-ncr`). If `searchUrl` is also set, this overrides the location parsed from the URL. |
| `experienceYears` | Integer | – | Years of experience required (0–30). |
| `salaryLakhs` | String (select) | – | Annual salary band in lakhs INR: `0-3`, `3-6`, `6-10`, `10-15`, `15-25`, `25+`. |
| `jobAge` | String (select) | – | Only jobs posted within the last N days: `1`, `3`, `7`, `15`, `30`. |
| `jobType` | String (select) | – | `full-time`, `part-time`, `internship`, or `contractual`. |
| `workMode` | String (select) | – | `remote` or `hybrid`. There is no office-only option: leaving it empty returns jobs of every work mode. |
| `sortBy` | String (select) | `relevance` | `relevance`, `date` (newest first), or `salary` (highest first). |

### Example: search URL

```json
{
  "searchUrl": "https://www.naukri.com/python-developer-jobs-in-bangalore",
  "maxItems": 50
}
```

### Example: structured filters

```json
{
  "keyword": "data scientist",
  "location": "hyderabad",
  "experienceYears": 3,
  "salaryLakhs": "10-15",
  "jobAge": "7",
  "sortBy": "date",
  "maxItems": 100
}
```

### Example: remote internships

```json
{
  "keyword": "machine learning intern",
  "workMode": "remote",
  "jobType": "internship",
  "maxItems": 30
}
```

## Use cases

- **Recruitment agencies** building talent pipelines or tracking which roles competitors are hiring for.
- **Job seekers** automating discovery of new postings that match a skill set or city.
- **HR and compensation teams** benchmarking salary ranges for a role across companies and cities.
- **Market researchers** tracking hiring volume by industry or location over time.
- **Data teams** building a dataset of India's job market for analysis or model training.

## FAQ

**Do I need a Naukri account to use this?** No. It reads Naukri's public job search results; no login or cookies are required.

**What's the difference between pasting a URL and using the filter fields?** Pasting a `searchUrl` lets you reuse a search you already built on Naukri's site — its keyword, location, experience and job-age are read back out of the URL. The filter fields build an equivalent search from scratch when you'd rather not construct the URL yourself. If both are given, the filter fields (`keyword`, `location`, `experienceYears`, `jobAge`) override the matching value parsed from the URL; `salaryLakhs`, `jobType`, `workMode` and `sortBy` are never read from the URL, so set those directly regardless of whether `searchUrl` is used.

**How many jobs can I get in one run?** Up to the `maxItems` cap you set (maximum 800). For broader coverage than that, split your search by city, keyword, or salary band and run multiple inputs.

**Why is `companyRating` missing for some jobs?** Only companies with an AmbitionBox rating on Naukri carry this field; smaller or newer employers often don't have one yet.

**Why is `postedAt` missing when `postedDate` is present?** The two come from different values in Naukri's listing data: `postedDate` is the relative label shown on the card ("2 days ago"), while `postedAt` is Naukri's creation timestamp for the job. When Naukri omits that timestamp, only the relative label is returned.

**Can I combine multiple filters, like experience and salary and job type?** Yes — all the filter fields apply together, whether or not `searchUrl` is also set.

**How fresh is the data?** Each run queries Naukri live, so results reflect whatever is currently listed on the site at run time.

**Is this affiliated with Naukri.com?** No. This is an independent tool and is not affiliated with, endorsed by, or sponsored by Naukri.com or its owner.
