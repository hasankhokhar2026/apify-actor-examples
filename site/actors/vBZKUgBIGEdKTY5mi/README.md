# Workday Careers Site Job Listings Extractor

Thousands of employers run their careers site on Workday, at URLs ending in `myworkdayjobs.com`. Every one of those sites exposes the same underlying job data, so this actor can point at any Workday tenant's careers URL — Salesforce, NVIDIA, Citi, Capital One and many more — and return its open roles as structured records, with no login required.

## What this actor does

- **Works with any Workday tenant** — give it a careers-site URL (or a direct job URL) and it discovers the tenant automatically
- **Filters at the source** by keyword, location facet or posting/start-date cutoff, so you only pull the jobs you need
- **Optionally enriches each job** with the full HTML/plain-text description, country, time type, remote status and apply eligibility by fetching its detail page
- **De-duplicates jobs by URL** across pages of results within a run
- **Signals blocked tenants clearly** — if a careers site returns zero jobs or Workday's maintenance page, the run emits a single marker record instead of silently returning nothing
- Fields a given tenant doesn't publish (such as compensation or remote type) are left out of that job's record rather than sent empty

## Output per job

- `id`, `requisitionId`, `jobPostingId` — the job's requisition/posting identifiers
- `title` — job title
- `url`, `jobRequisitionUrl` — public link(s) to the posting
- `externalPath` — the job's path on the tenant's site, relative to its domain
- `jobDescription` — full HTML description (when `scrapeDetails` is on)
- `descriptionText` — plain-text version of the description
- `location` — primary location text
- `primaryLocation` — structured location descriptor including country
- `additionalLocations` — other locations the role is open to, when the posting lists more than one
- `country`, `countryCode` — country of the primary location
- `postedOn`, `postingDate` — how Workday displays the posting date, and its parsed ISO form
- `startDate`, `endDate`, `endDateText` — role start date and application end date, when published
- `applicationCloseDate`, `applicationTimeRemaining` — how long the posting stays open, when published
- `timeType` — full-time / part-time designation
- `remoteType` — remote/hybrid/onsite designation, when the tenant publishes one
- `compensationRangeMin`, `compensationRangeMax`, `compensationCurrency`, `compensationFrequency` — pay range, parsed from the posting when it states one
- `canApply` — whether the posting is currently open to applicants
- `hiringOrganization` — employer name
- `questionnaireId`, `secondaryQuestionnaireId` — Workday's internal application questionnaire references
- `similarJobs` — other roles Workday lists as similar, each with `title` and `url`
- `logoImage` — employer logo URL, when the tenant exposes one
- `videoInfo` — embedded recruiting video details, when present
- `tenant`, `site` — the Workday tenant and career-site identifiers the job came from
- `scrapedAt` — ISO 8601 timestamp of the scrape
- `type` — set to `job_workday` for every real job record (a sentinel record with `job_workday_blocked` is emitted instead when a tenant returns no jobs)

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `startUrls` | array | `["https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"]` | Workday careers-site URLs to scrape, or direct job URLs containing `/job/...`. |
| `searchText` | string | – | Optional keyword filter passed to the Workday job search. |
| `locations` | array | – | Optional list of Workday location facet UUIDs (returned by the careers site's own location filter). |
| `postedAt` | string | – | Optional cutoff: an ISO date (`2026-04-01`) or a relative string like `7 days`. Skips jobs posted before it. |
| `startAt` | string | – | Optional start-date cutoff in the same format, applied to the job's `startDate`. |
| `scrapeDetails` | boolean | `true` | Fetch each job's detail page for the full description, country, time type and apply status. Turn off for a faster, listing-only run. |
| `maxItems` | integer | `3` | Maximum number of jobs to return (1–10,000). |
| `proxyConfiguration` | object | `{"useApifyProxy": true}` | Apify proxy configuration used to fetch the careers site. |

### Example: all open roles at one tenant

```json
{
    "startUrls": ["https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"],
    "maxItems": 100
}
```

### Example: keyword filter, listing-only (fast)

```json
{
    "startUrls": ["https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"],
    "searchText": "engineer",
    "scrapeDetails": false,
    "maxItems": 50
}
```

### Example: jobs posted in the last two weeks

```json
{
    "startUrls": ["https://citi.wd5.myworkdayjobs.com/citi"],
    "postedAt": "14 days",
    "maxItems": 200
}
```

## Use cases

- **Recruitment market research** — track how many and what kind of roles a company is hiring for over time
- **Talent-pool sourcing** — pull all open roles at a target employer's Workday site for sourcing or outreach
- **Compensation benchmarking** — collect published pay ranges across similar titles at multiple employers
- **Competitive hiring intelligence** — watch which teams or locations a competitor is expanding
- **Job-board aggregation** — feed Workday postings from many companies into your own listings site or alert system

## FAQ

**Does this work for any company that uses Workday?**
Yes — any tenant on `*.myworkdayjobs.com` works the same way; just give it that tenant's careers-site URL.

**Why does a run sometimes return only one record with `type: job_workday_blocked`?**
That's a sentinel: either the URL matched zero jobs, or the tenant was showing Workday's maintenance page at the time of the run. It lets your pipeline detect the situation and retry instead of treating an empty dataset as a silent failure.

**What's a location facet UUID, and where do I get one?**
It's the internal ID Workday assigns to each entry in a careers site's own Locations filter. The simplest way to find one is to open the careers site in a browser, check the Locations filter, and use the corresponding ID; the actor also accepts them from the API's own `facets` data if you've captured it previously.

**Why are some fields like `compensationRangeMin` or `remoteType` missing from a job?**
Not every employer publishes pay ranges or a remote-work designation on their Workday postings. When a tenant doesn't include that information, the field is simply left out of the record.

**What's the difference between `scrapeDetails: true` and `false`?**
With it on, each job's own detail page is fetched for the full description, country, time type and current apply status. With it off, you get the faster listing-level fields only, without descriptions.

**How fresh are the results?**
Every run queries the careers site live, so results reflect whatever is currently posted at run time.

**Is this affiliated with Workday or the companies whose jobs it returns?**
No, this is an independent, third-party actor that reads each company's own public Workday careers site. It is not affiliated with or endorsed by Workday, Inc. or any employer listed.
