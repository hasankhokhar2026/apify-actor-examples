# Naukri.com Job Listings Extractor with Salary & Skills

Extract **Naukri.com** job listings as structured data. Search by keyword and Indian city, pull jobs by ID, or monitor a company — then get the full job description, raw and parsed salary, experience bounds, skills, work mode, education requirements, role taxonomy, company ratings and walk-in details. No Naukri login, cookies or API key required.

## What this actor does

- **Three ways to find jobs:** keyword and city searches, direct job IDs, or company IDs.
- **Up to 10,000 records per run**, with a 3,000-job ceiling per individual query (Naukri returns 20 jobs per page and allows 150 pages).
- **Full detail per job:** not just the search card — the actor fetches each posting to return the complete description, salary fields, education, role taxonomy, company profile and walk-in information.
- **Filters:** experience in years, salary band, remote or hybrid mode, job age, date or salary sort, internships and walk-in drives.
- **Incremental runs:** `onlyNew` stores emitted job IDs in actor state, so scheduled runs can return only postings you have not seen before.
- **Honest salary data:** every record carries the raw salary string and a `salaryDisclosed` flag. Numeric `salaryMin` and `salaryMax` appear only when Naukri discloses a figure.
- **Empty fields are omitted** — records never contain `null`, blank strings or empty arrays.

## Output per job

| Field | Description |
|---|---|
| `id` | Naukri job ID. |
| `title` | Job title as posted. |
| `url` | Naukri job listing URL. |
| `companyName` | Hiring company name. |
| `companyId` | Naukri company ID. |
| `companyLogoUrl` | Company logo image URL. |
| `logoUrl` | Company logo URL (legacy field, same value as `companyLogoUrl`). |
| `companyProfileUrl` | Naukri company profile URL. |
| `companyWebsite` | Company website when Naukri publishes one (sparse). |
| `companyDescription` | Company profile description as plain text. |
| `companyAddress` | Company address. |
| `companyRating` | AmbitionBox rating out of 5. |
| `companyReviewCount` | Number of AmbitionBox reviews behind the rating. |
| `companyReviews` | Up to three review snippets when `includeCompanyReviews` is on. |
| `companyApplyUrl` | Naukri company-apply gateway URL when present. |
| `applyRedirectUrl` | External apply URL when Naukri exposes one; may be ad-wrapped. |
| `applyUrl` | Best available apply link: company gateway, external redirect, or the Naukri listing. |
| `salary` | Raw salary string exactly as displayed, including `Not Disclosed`. |
| `salaryMin` | Parsed minimum salary in INR for `salaryPeriod`; omitted when not disclosed. |
| `salaryMax` | Parsed maximum salary in INR for `salaryPeriod`; omitted when not disclosed. |
| `salaryCurrency` | ISO currency code, normally `INR`. |
| `salaryPeriod` | `year` or `month`; internship stipends are reported per month. |
| `salaryDisclosed` | `false` when Naukri hides the salary. |
| `salaryVariablePct` | Variable pay percentage when Naukri supplies one. |
| `experience` | Raw experience range, e.g. `5-7 Yrs`. |
| `experienceMinYears` | Parsed minimum years. |
| `experienceMaxYears` | Parsed maximum years. |
| `skills` | Skill tags, preferred skills first. |
| `skillsPreferred` | Preferred skill tags. |
| `skillsOther` | Other skill tags. |
| `description` | Full job description as plain text (`includeDescription`). |
| `descriptionHtml` | Raw HTML description (`includeDescriptionHtml`). |
| `locations` | Structured list of job locations. |
| `location` | Job locations joined into one string (legacy field). |
| `workMode` | `office`, `remote` or `hybrid`. |
| `employmentType` | Employment type, e.g. `Full Time, Permanent`. |
| `jobType` | Naukri job type, e.g. `fulltime` or `internship`. |
| `educationUG` | Undergraduate education requirements. |
| `educationPG` | Postgraduate education requirements. |
| `educationPPG` | Post-postgraduate education requirements. |
| `industry` | Industry. |
| `functionalArea` | Functional area. |
| `roleCategory` | Role category. |
| `role` | Job role. |
| `postedAt` | Posting time in ISO 8601 with a `+05:30` offset. |
| `postedDate` | Relative posting label from search, e.g. `2 Days Ago`. |
| `vacancies` | Number of openings; omitted when Naukri reports 0. |
| `applyCount` | Applicant count; omitted when 0. |
| `viewCount` | View count; omitted when 0. |
| `walkIn` | Walk-in interview flag. |
| `walkInDetails` | Venue and contact block when Naukri publishes it. Contains `venueAddress`, `startDate`, `endDate`, `dailyTiming`, `contactName`, `contactPhone`, `mapUrl`, `embedMapUrl`, `saturdayWorking` and `sundayWorking`. |
| `jobTypeFlags` | Badges such as `premium`, `easy_apply` and `walk_in` (legacy field). |
| `scrapedAt` | UTC timestamp when the record was scraped. |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searches` | array | one keyword search | Search configurations. Each entry has `keywords[]`, `locations[]`, `experienceYears`, `salaryBucket`, `workMode`, `jobAge`, `sort`, `companyId`, `internship` and `walkIn`. Every keyword is combined with every location. |
| `jobIds` | array | one example ID | Naukri job IDs or job URLs to fetch directly. Processed before searches. |
| `companyIds` | array | `[]` | Naukri company IDs. When searches are also supplied, each company is combined with every search. |
| `maxItems` | integer | `100` | Total records to return, 1–10,000. |
| `onlyNew` | boolean | `false` | Emit only jobs not emitted by an earlier run with the same state key. |
| `resetState` | boolean | `false` | Clear saved incremental state before this run. |
| `stateKey` | string | auto | Optional state name. Defaults to a hash of the search configuration. |
| `includeDescription` | boolean | `true` | Include the full job description text. |
| `includeDescriptionHtml` | boolean | `false` | Include the raw HTML description too. |
| `includeCompanyReviews` | boolean | `false` | Include up to three AmbitionBox review snippets. |
| `strictJobAge` | boolean | `true` | Drop promoted jobs older than the selected job age. |
| `timeBudgetSecs` | integer | `0` | Stop gracefully after this many seconds; `0` means no limit. |
| `failOnEmpty` | boolean | `false` | Mark the run as failed when no jobs are returned. |
| `browserFallback` | boolean | `false` | Retry through a browser session if the normal connection is blocked. Slower and uses more memory. |
| `proxyConfiguration` | object | India Apify proxy | Optional connection override. The actor selects an India-based connection automatically. |

Salary bands are `0-3`, `3-6`, `6-10`, `10-15`, `15-25` and `25+` lakhs per year. Job-age values are `1`, `3`, `7`, `15` and `30` days. Work modes are `any`, `remote` and `hybrid`; Naukri does not expose an office-only filter.

### Example: software engineer jobs in Bangalore

```json
{
  "searches": [
    {
      "keywords": ["software engineer"],
      "locations": ["bangalore"],
      "experienceYears": 3,
      "jobAge": "7",
      "sort": "date"
    }
  ],
  "maxItems": 100
}
```

### Example: fetch specific jobs

```json
{
  "jobIds": ["221026015762", "191026012479"],
  "includeDescription": true,
  "maxItems": 2
}
```

### Example: monitor a company for new postings

```json
{
  "companyIds": ["10111"],
  "searches": [
    {
      "keywords": ["python developer"],
      "locations": ["hyderabad", "pune"],
      "sort": "date"
    }
  ],
  "onlyNew": true,
  "stateKey": "infosys-python",
  "maxItems": 200
}
```

### Example: remote internships and walk-in drives

```json
{
  "searches": [
    {
      "keywords": ["machine learning intern"],
      "workMode": "remote",
      "internship": true
    },
    {
      "locations": ["mumbai"],
      "walkIn": true
    }
  ],
  "maxItems": 50
}
```

## Use cases

- **Recruitment agencies** — build talent pipelines and track which employers are hiring for a role or city.
- **Job seekers** — schedule a daily monitor that returns only newly posted jobs matching a skill set.
- **Compensation teams** — collect salary bands and disclosure rates for a role across companies and cities.
- **Market researchers** — measure hiring volume by location, industry, role or work mode over time.
- **Sales teams** — detect companies ramping up hiring as a buying signal.
- **Data teams** — build an India job-market dataset with full descriptions, skills and company profiles.

## FAQ

**Do I need a Naukri account, cookies or an API key?** No. The actor reads publicly available Naukri job data without a login.

**Why is `salaryMin` missing for most jobs?** Naukri hides salary on most postings. In a 24-job sample, only 16.7% disclosed a numeric range. Every record still includes the raw `salary` string and `salaryDisclosed` so you can separate disclosed jobs from hidden ones.

**Why do some records lack `description`?** `description` is on by default. If Naukri does not return a detail page for a posting, the record falls back to the shorter description from the search result rather than dropping the job.

**How many jobs can one run return?** `maxItems` supports up to 10,000. Each individual query is capped by Naukri at 3,000 jobs, so a single keyword-and-city combination tops out there. Add more keywords, cities or companies to reach higher totals.

**Does the work-mode filter include office jobs?** Naukri only exposes remote and hybrid filters. Use `any` to return every mode; the output `workMode` tells you which one each job has.

**Can I filter full-time, part-time or contractual jobs?** No. Naukri does not honour those filters reliably. The supported job-type filters are internships and walk-in drives. The output `jobType` and `employmentType` still describe each posting.

**Are benefits, localities or recruiter details included?** No. Naukri does not expose benefits, locality lists or recruiter names on these postings, so they are not fabricated or promised.

**Why are `companyRating` and `companyAddress` missing on some jobs?** These come from the employer's AmbitionBox profile and company page. Smaller or newer employers often do not have them.

**Why is `applyRedirectUrl` missing on most records?** Naukri only exposes an external apply link for some postings, and those links can be ad-wrapped. `applyUrl` always gives you a usable link: the company gateway or external redirect when present, otherwise the Naukri listing.

**Can I get walk-in venue and contact details?** Yes, when Naukri publishes them. They are returned in `walkInDetails`; not every walk-in posting includes a venue or phone number.

**How fresh is the data?** Every run queries Naukri live, so results reflect the listings available at run time.

**Do I need to set up a proxy?** No. The actor chooses a working connection to Naukri automatically.

**Is this affiliated with Naukri.com?** No. This is an independent third-party tool and is not affiliated with, endorsed by or sponsored by Naukri.com.

## Limitations

- Salary is disclosed on a minority of postings. Numeric salary fields are therefore conditional, not guaranteed.
- Benefits, locality lists and recruiter names are not available from Naukri's public job data.
- External apply links are partial and can be ad-wrapped; `applyUrl` always provides a fallback.
- Walk-in venue and contact details are present only when the employer publishes them.
- The actor covers Naukri's India job market. Gulf listings on other domains are out of scope.
- A single query returns at most 3,000 jobs (150 pages of 20). Split broad searches by city, keyword or company to collect more.

## Notes on coverage

Naukri exposes different amounts of detail per posting. The actor returns what the public job record contains and omits fields that are not published; it does not infer salary, benefits, or recruiter details.
