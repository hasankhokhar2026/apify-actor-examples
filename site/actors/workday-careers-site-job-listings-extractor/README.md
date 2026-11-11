# Workday Careers Site Job Listings Extractor

Workday powers the careers sites of thousands of employers, all at URLs ending in `myworkdayjobs.com` or `myworkdaysite.com`. Point this actor at any of them and get every open role as structured records: exact posting dates, requisition IDs, all locations, job family, remote or hybrid status, time type, published salary ranges, full descriptions and apply links. No login, no API key and no proxy setup.

## What this actor does

- **Works with any public Workday careers site** - paste a careers URL, a direct job URL, or use a tenant name (its career-site ID is discovered automatically when omitted). Both `myworkdayjobs.com` and `myworkdaysite.com` URL families are supported.
- **Filters at the source** by keyword, location, job family and remote work, then applies posting-date and start-date cutoffs.
- **Enriches every job** with the full HTML and plain-text description, exact posting date, employment type, work model, every location the role is open to, and a published salary range when the employer states one.
- **Reads the whole site** - pages through all results, removes duplicates across pages and URLs, and splits large sites by job family, then by one small secondary facet such as time type or location when one family is still over Workday's per-query limit.
- **Empty fields are omitted** - a missing salary, remote type or end date is omitted from that job's record instead of being sent empty.

## Output per job

**Identity and links**

- `type` - `job_workday` for every real job record
- `title` - job title
- `id`, `requisitionId` - the requisition identifier, when the employer publishes one
- `jobPostingId` - Workday's internal posting identifier
- `url` - public job page
- `applyUrl` - the posting page where the Apply button lives
- `jobRequisitionUrl` - the employer's canonical posting URL
- `externalPath` - the job's path on its careers site

**Employer and source**

- `hiringOrganization` - the legal entity name published on the posting; the Workday tenant slug when details are off or the posting page cannot be read, and omitted when a fetched posting publishes no organization name
- `tenant`, `site`, `region` - the Workday tenant, career-site ID and data-center region the job came from

**Locations**

- `location` - primary location text
- `locations` - every location the role is open to, when the posting lists more than one
- `primaryLocation` - structured primary location, including country details
- `additionalLocations` - other locations listed on the posting
- `country`, `countryCode` - country of the primary location and its two-letter code

**Work model**

- `timeType` - full-time or part-time designation
- `employmentType` - standardized employment type such as `FULL_TIME`
- `remoteType` - the employer's own remote/hybrid label
- `workplaceType` - normalized `remote`, `hybrid`, `onsite` or `field`
- `jobLocationType` - `TELECOMMUTE` when the posting is marked remote

**Dates**

- `postedOn` - how the careers site displays the posting age
- `postingDate` - exact posting date in ISO 8601 form
- `startDate` - role start date, when published
- `endDate`, `applicationCloseDate` - application close date, when published
- `endDateText` - the employer's own end-date wording
- `applicationTimeRemaining` - time left to apply, when shown

**Description and pay**

- `jobDescription` - full HTML description
- `descriptionText` - plain-text version of the description
- `compensationRangeMin`, `compensationRangeMax` - published pay range; when a posting lists several location-specific ranges, the range for the job's primary location is used
- `compensationCurrency`, `compensationFrequency` - pay currency and hourly/monthly/yearly period
- `compensationText` - the sentence the range was read from
- `compensationType` - `range` or `single`

**Classification and extras**

- `jobFamily` - job family or category, when the site publishes one
- `canApply`, `isPosted` - whether the posting is open to applicants
- `questionnaireId`, `secondaryQuestionnaireId` - application questionnaire references, when present
- `similarJobs` - related roles, each with `title`, `url`, and available listing details
- `logoImage` - employer logo URL, when the site exposes one
- `videoInfo` - embedded recruiting video details, when present
- `scrapedAt` - ISO 8601 timestamp of the scrape

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `careerSite` | `careerSite` (careers/job URLs), `tenant` (tenant + site), or `jobDetail` (specific `/job/...` URLs). |
| `startUrls` | array | ["https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"] | Workday careers-site or job URLs (mode=careerSite or jobDetail). |
| `tenant` | string | - | Workday tenant name, for example `nvidia` (mode=tenant). |
| `site` | string | - | Optional career-site ID from the URL, for example `NVIDIAExternalCareerSite` (mode=tenant). Leave it blank to discover the tenant's first public site automatically. |
| `region` | string | `auto` | Workday data-center region; `auto` detects it (mode=tenant). |
| `searchText` | string | - | Keyword passed to the site's own job search. |
| `locations` | array | `[]` | Location names such as `United States`, `New York` or `Remote`. |
| `jobFamilies` | array | `[]` | Job family names such as `Engineering` or `Sales`. |
| `remoteOnly` | boolean | `false` | Keep only postings explicitly marked remote. |
| `postedWithin` | string | `any` | `any`, `1 day`, `3 days`, `7 days`, `14 days`, `30 days`, `60 days` or `90 days`. |
| `postedAfter` | string | - | Exact cutoff date in `YYYY-MM-DD` form. |
| `startDateFrom` | string | - | Keep roles starting on or after this `YYYY-MM-DD` date. |
| `scrapeDetails` | boolean | `true` | Fetch the full description, exact date, work model and all locations. |
| `includeJobFamily` | boolean | `true` | Add the job family/category to each record. |
| `maxItems` | integer | `50` | Maximum jobs to save across all URLs (1-10,000). Jobs are returned in URL order, so a large first site can use the whole cap. |
| `proxyConfiguration` | object | proxy off | Optional. The actor works without a proxy. |

### Example: every open role at one company

```json
{
    "mode": "careerSite",
    "startUrls": [
        "https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite"
    ],
    "maxItems": 500
}
```

### Example: engineering roles in the United States

```json
{
    "mode": "careerSite",
    "startUrls": [
        "https://salesforce.wd12.myworkdayjobs.com/External_Career_Site"
    ],
    "searchText": "engineer",
    "locations": ["United States"],
    "jobFamilies": ["Engineering"],
    "postedWithin": "14 days",
    "maxItems": 200
}
```

### Example: by tenant name, no URL

```json
{
    "mode": "tenant",
    "tenant": "workday",
    "site": "Workday",
    "locations": ["Remote"],
    "scrapeDetails": true,
    "maxItems": 50
}
```

`site` is optional. When it is omitted, the actor reads the tenant's public `robots.txt` and uses the first career site that responds.

### Example: one specific posting

```json
{
    "mode": "jobDetail",
    "startUrls": [
        "https://salesforce.wd12.myworkdayjobs.com/External_Career_Site/job/Spain---Madrid/Deployment-Strategist---Spanish-Speaker_JR366417"
    ],
    "scrapeDetails": true
}
```

### Example: a myworkdaysite.com careers site

```json
{
    "mode": "careerSite",
    "startUrls": [
        "https://wd1.myworkdaysite.com/en-US/recruiting/fmr/FidelityCareers"
    ],
    "searchText": "planning",
    "maxItems": 100
}
```

## Use cases

- **Talent sourcing** - collect every open role at target employers, with locations and apply links, for outreach or a CRM.
- **Competitive hiring intelligence** - track which teams, offices and job families a competitor is expanding.
- **Compensation benchmarking** - gather published salary ranges by title, family and location.
- **Job-board aggregation** - feed Workday postings from many employers into your own listings or alerts.
- **Labor-market research** - measure remote/hybrid share, time type and posting velocity across companies.
- **Recruiting operations** - monitor a company's careers site on a schedule and diff by requisition ID.

## FAQ

**Does this work with any company that uses Workday?**
Yes. Any public careers site on `myworkdayjobs.com` or `myworkdaysite.com` works the same way. Paste that careers URL, or use `tenant` with an optional `site`.

**How do I find the tenant and career-site ID?**
Both are in the careers URL. In `https://nvidia.wd5.myworkdayjobs.com/NVIDIAExternalCareerSite`, the tenant is `nvidia`, the region is `wd5` and the site is `NVIDIAExternalCareerSite`. The site ID is case-sensitive, but you can omit it: the actor discovers the tenant's first public site from its `robots.txt`.

**Why did I get fewer jobs than the company lists?**
Workday returns at most about 2,000 results for a single search. The actor splits a capped site by job family, and splits a single large family again by one small secondary facet (usually time type) so most sites are read fully. If one slice is still above the cap, narrow the run with `searchText`, `locations` or `postedWithin` and run it more than once.

**Why are some fields missing from a job?**
Employers publish different details. Salary ranges, remote or hybrid labels, end dates, logos and similar jobs appear only when the posting includes them. Missing fields are omitted, never sent as null.

**Why is `jobFamily` missing on some sites?**
A few employers do not publish a job-family/category filter at all. For those sites there is no reliable source for the field, so it is omitted rather than guessed. Setting `includeJobFamily` to `false` also omits it, including on large sites that are split by job family to get past the 2,000-result limit.

**Which salary range is used when a posting lists several?**
When the posting labels ranges by location, the actor uses the range that matches the job's primary location. If no location-specific range applies, it uses the posting's typical/base range. Values are never estimated.

**What is the difference between `scrapeDetails` on and off?**
With it on, each job's public page is read for the full description, the exact posting date, employment type, work model and every location. With it off, you get the fast listing fields: title, location, requisition ID, posting age and URL. A `30+ Days Ago` posting has no exact date until details are on.

**How do I scrape several companies in one run?**
Paste all of their careers URLs and set `maxItems` large enough to cover the total. Jobs are returned in URL order, so a site with more jobs than `maxItems` can use the whole cap; split the run by company if you need equal coverage.

**Why did a very old date cutoff return fewer jobs than expected?**
Workday has no server-side date filter, so dates are checked on the postings the site returns, newest first. To avoid reading an entire large site for a sparse cutoff, the actor stops after 30 pages with no match. Narrow the run with `searchText`, `locations` or `jobFamilies` so the matching roles are reached sooner.

**Can I collect only new jobs?**
Schedule the actor and compare `requisitionId` (or `externalPath`) between runs. The actor returns the current postings each time; it does not keep state between runs.

**Does it return localized job text?**
Job titles and descriptions are the employer's own text. Workday's public API serves the site's default language and ignores locale headers or query parameters, so the actor does not offer a language switch.

**Does it work with remote-only searches?**
Yes. `remoteOnly` keeps postings the employer explicitly marks remote. Hybrid and onsite postings are excluded.

**Do I need a proxy, login or API key?**
No. The actor reads public careers pages and works without any of them. Leave the proxy setting off unless you need a specific connection setup.

**Why is `hiringOrganization` sometimes a legal entity name?**
That is the employer name Workday publishes on the posting. Some companies use a legal subsidiary name rather than the consumer brand. When a fetched posting publishes no organization name, the field is omitted instead of guessing a brand; listing-only runs use the Workday tenant slug.

**Is this affiliated with Workday or the employers whose jobs it returns?**
No. This is an independent, third-party actor that reads each company's own public careers site. It is not affiliated with or endorsed by Workday, Inc. or any employer listed.
