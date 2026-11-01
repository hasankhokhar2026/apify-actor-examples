# Wellfound Startup Jobs Finder with Pay & Remote Filters

Scrape live startup jobs and startup directory profiles from Wellfound (formerly AngelList Talent). Search by role, city or remote work, pull structured salary and equity ranges, visa and relocation details, and company signals such as size, stage, YC funding and open roles. Filter everything in one run, monitor new postings with a saved state key, and export clean job and company datasets.

## What this actor does

- **Jobs and companies:** search jobs by role, location or remote, or read startup directory pages for company profiles.
- **Rich job records:** title, company, locations, remote details, structured salary and equity, description, skills, perks, visa/relocation data and application source.
- **Company context:** size, stage, high concept, description, badges, YC/growing/actively-hiring/valuation signals, funding, founders, website and social links, industry and open job counts.
- **Filter and monitor:** posting age, title/keyword, job type, experience, salary/currency, equity, company size/stage, YC, funding, open jobs, visa sponsorship and WFH flexibility; sort by newest or oldest, or emit only IDs not seen before for a saved state key.
- **Empty fields are omitted** — records only include data Wellfound actually exposes, with no `null`, empty strings or placeholders.

## Output per job

- `type` — always `wellfound_job`.
- `jobId`, `title`, `slug`, `jobUrl` — job identity and canonical Wellfound URL.
- `description`, `descriptionHtml` — plain-text and full HTML job description.
- `compensation` — raw compensation string exactly as Wellfound publishes it.
- `salaryMin`, `salaryMax`, `salaryCurrency`, `salaryPeriod` — parsed salary range, currency (`USD`, `CAD` or `INR`) and period (usually annual).
- `equityMin`, `equityMax`, `equityOffered` — equity percentage range; `equityOffered` is `false` only when the source says "No equity".
- `remote`, `remoteKind`, `remoteWfhFlexible`, `acceptedRemoteLocations`, `locations` — remote flag, remote configuration and location lists.
- `jobType`, `yearsExperienceMin`, `skills`, `primaryRoleTitle` — employment type, minimum experience and skill tags.
- `visaSponsorship`, `relocationAllowed`, `relocationAssistance` — eligibility details.
- `applyUrl`, `atsSource`, `source`, `directApply` — application URL and integration signals.
- `companyId`, `companyName`, `companySlug`, `companyUrl`, `companyLogo` — company identity and logo.
- `companyHighConcept`, `companyDescription`, `companySize`, `companySizeCode`, `companyStage`, `companyIndustry`, `companyIndustryTags`, `companyTypeTags`, `companyHq`, `companyAtGlance` — company profile and classification.
- `badges`, `companyYcFunded`, `companyGrowingFast`, `companyActivelyHiring`, `companyValuation1B`, `companyTopInvestors` — hiring and maturity signals.
- `companyFundingTotal`, `companyFundingText`, `companyFundingRounds`, `companyFounders`, `companyOpenJobsCount`, `companyJobCounts` — funding, people and open-role context.
- `companyWebsite`, `companyLinkedIn`, `companyTwitter`, `companyFacebook`, `companyBlog`, `companyProductHunt` — company links.
- `perks`, `benefits` — listed perks and benefits.
- `postedAt`, `postedAtIso`, `reposted`, `lastRespondedAt`, `autoPosted` — posting and response timing.
- `isNew`, `firstSeenAt`, `lastSeenAt` — monitoring timestamps, present only when `stateKey` is set.
- `scrapedAt` — UTC collection timestamp.

`companyJobCounts` is an object with `total` plus `roles`, `locations`, `jobTypes` and `jobSources` arrays of `{name, count}` entries when Wellfound exposes them.

## Output per company

- `type` — always `wellfound_company`.
- `companyId`, `companyName`, `companySlug`, `companyUrl`, `companyLogo` — company identity and profile link.
- `companyHighConcept`, `companyDescription` — one-line concept and plain-text description.
- `companySize`, `companySizeCode`, `companyStage` — human-readable size, raw size code and stage.
- `badges`, `companyYcFunded`, `companyGrowingFast`, `companyActivelyHiring`, `companyValuation1B`, `companyTopInvestors` — badge labels and company signals.
- `companyJobCounts`, `companyOpenJobsCount` — open-role totals, including role, location, job-type and source breakdowns when available.
- `companyIndustryTags`, `companyTypeTags`, `companyHq` — industry, company-type and headquarters tags.
- `companyWebsite` — company website.
- `isNew`, `firstSeenAt`, `lastSeenAt` — monitoring timestamps, present only when `stateKey` is set.
- `scrapedAt` — UTC collection timestamp.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `auto` | `auto` uses `startUrls` when provided, otherwise role/location search. `search` builds a role/location/remote search. `startUrls` scrapes the supplied URLs. `companies` reads the startup directory. |
| `startUrls` | array | `[]` | Wellfound URLs to scrape, including `/startups` directory URLs in companies mode. Supports an explicit `?page=N`. Example: `https://wellfound.com/jobs`. |
| `role` | string | – | Role slug for search mode, e.g. `software-engineer`, `product-manager`, `designer`. |
| `jobTitle` | string | – | Case-insensitive substring filter on the job title. |
| `keyword` | string | – | Case-insensitive substring across title, company, locations, compensation and description. |
| `location` | string | – | Used in the location path when it is a clean city slug/name, and always applied as a filter over locations plus accepted remote locations. |
| `remoteOnly` | boolean | `false` | Search remote jobs and keep only jobs flagged as remote. |
| `jobType` | string | `any` | Exact structured type: `any`, `full-time`, `part-time`, `contract` or `internship`. |
| `experience` | string | `any` | Best-effort level: `junior`, `mid`, `senior`, `executive`. Title keywords first, then minimum years (0-2 junior, 3-4 mid, 5+ senior). Unknown jobs are kept and counted. |
| `minSalary` | integer | `0` | Keep jobs whose salary range top is at or above this value in the job's listed currency. 0 = off. Range 0-10,000,000. |
| `maxSalary` | integer | `0` | Keep jobs whose salary range bottom is at or below this value. 0 = unlimited. Range 0-10,000,000. |
| `salaryCurrency` | string | `any` | `any`, `USD`, `CAD` or `INR`. No FX conversion; a different-currency salary is dropped. |
| `includeNoSalary` | boolean | `true` | Only active when `minSalary` or `maxSalary` is set. `false` drops jobs with no parsed salary. |
| `companyCategories` | array | – | Matches Wellfound market/industry/company-type tags and the company high concept. Not a company-name filter; requires `enrichDetails=true`. |
| `includeCompanies` | array | – | Keep jobs whose company name or slug contains one of these values. |
| `excludeCompanies` | array | – | Drop jobs whose company name or slug contains one of these values. Exclusions win. |
| `postedWithinDays` | integer | `0` | Keep jobs posted within the last N days. Jobs without a parsed date are dropped and counted. 0 = off. Range 0-3650. |
| `companySizes` | array | – | Keep rows matching company size values such as `11-50`, `51-200` or `SIZE_51_200`. Missing sizes are dropped and counted. |
| `companyStages` | array | – | Keep rows matching stages such as `seed`, `early-stage`, `growth-stage` or `scale-stage`. Missing stages are dropped and counted. |
| `ycOnly` | boolean | `false` | Keep rows with the YC Funded badge. |
| `minCompanyFunding` | integer | `0` | Keep jobs with parsed total funding at or above this amount. Requires `enrichDetails=true`; missing funding is dropped. Range 0-10,000,000,000. |
| `minOpenJobs` | integer | `0` | Keep rows with at least this many open company jobs. Requires `enrichDetails=true` for jobs; missing counts are dropped. Range 0-100,000. |
| `visaSponsorshipOnly` | boolean | `false` | Keep jobs whose detail page says visa sponsorship is available. Requires `enrichDetails=true`. |
| `minEquity` | number | `0` | Keep jobs whose equity range top is at or above this percentage. Jobs without equity data are dropped. Range 0-100. |
| `maxEquity` | number | `0` | Keep jobs whose equity range bottom is at or below this percentage. 0 = unlimited. Range 0-100. |
| `equityOnly` | boolean | `false` | Keep jobs that explicitly offer equity; jobs that say No equity or do not mention equity are dropped. |
| `remoteWfhFlexible` | boolean | `false` | Keep jobs whose remote configuration explicitly reports WFH flexibility. Requires `enrichDetails=true`. |
| `sort` | string | `none` | `none` keeps first-seen order; `newest`/`oldest` sort the whole run by posted date, missing dates last. |
| `pageLimit` | integer | `0` | 0 = all pages up to the available page count; N = first N pages. An explicit `?page=N` fetches only that page. Range 0-500. |
| `enrichDetails` | boolean | `true` | Fetch full detail pages for selected jobs to add description HTML, structured salary/equity, visa/relocation, skills, company funding, founders, socials and benefits. Direct job URLs are always enriched. |
| `maxItems` | integer | `50` | Maximum jobs or companies pushed after filtering and sorting. Range 1-10,000. |
| `onlyNew` | boolean | `false` | Push only IDs not seen before for `stateKey`; requires `stateKey`. |
| `stateKey` | string | – | Persistent key that remembers seen job/company IDs between runs. Changing it starts a fresh history. |
| `expandSimilar` | boolean | `false` | Add related jobs from the detail page, bounded by `similarDepth` and `similarLimit`. |
| `similarDepth` | integer | `1` | `1` emits embedded similar jobs; `2`-`3` follow additional detail pages within `similarLimit`. Range 1-3. |
| `similarLimit` | integer | `10` | Maximum additional similar jobs emitted, also bounded by `maxItems`. Range 1-100. |

### Example: software engineering roles in San Francisco

```json
{
  "mode": "search",
  "role": "software-engineer",
  "location": "san-francisco",
  "pageLimit": 2,
  "maxItems": 40
}
```

### Example: remote design roles with a salary floor

```json
{
  "mode": "search",
  "role": "designer",
  "remoteOnly": true,
  "minSalary": 100000,
  "includeNoSalary": false,
  "maxItems": 50
}
```

### Example: scrape a single job page

```json
{
  "mode": "startUrls",
  "startUrls": [
    { "url": "https://wellfound.com/jobs/4728540-software-engineer" }
  ],
  "enrichDetails": true,
  "maxItems": 1
}
```

### Example: startup directory filtered by size and stage

```json
{
  "mode": "companies",
  "startUrls": [
    { "url": "https://wellfound.com/startups" }
  ],
  "companySizes": ["11-50", "51-200"],
  "companyStages": ["seed", "early-stage"],
  "maxItems": 20
}
```

## Use cases

- **Recruiting and sourcing** — build a pipeline of startup roles by role, city and salary band.
- **Job boards and aggregators** — refresh startup listings with structured salary, equity and remote data.
- **Market research** — track startup hiring by company size, stage, YC status and funding.
- **Sales and go-to-market** — find actively hiring startups and use team size and stage as buying signals.
- **Career coaching and job seekers** — monitor new remote roles and filter by visa sponsorship or WFH flexibility.
- **Startup ecosystem analysis** — export directory profiles for regional or industry research.

## FAQ

### Do I need a Wellfound account or cookies?

No. The actor reads public Wellfound pages without cookies or a login. The login-gated `/jobs/search` page is not used.

### Why are results fewer than `maxItems`?

Wellfound search pages expose only 1-3 highlighted jobs per startup, so a role/location search reaches roughly 56-82% of Wellfound's claimed total. Use more specific role, location or remote sources, raise `pageLimit`, or relax filters to widen the pool.

### Why is a location sometimes not used in the page path?

Only clean city slugs or city names are put in the path. Free text with commas or unsupported characters falls back to a role-only or `/jobs` source and is still applied as a filter over the returned locations.

### How do salary and equity filters work?

`minSalary` compares the **top** of the job's salary range to the floor; `maxSalary` compares the **bottom** of the range to the cap. No currency conversion is performed, so a job with a salary in another currency is dropped when `salaryCurrency` is set. `includeNoSalary` only covers jobs with no parsed salary. Equity percentages are stored as percentages (`0.01` means 0.01%).

### Are company profile pages included?

No. Company profile pages (`/company/*`) return HTTP 403 to anonymous access, so the actor never fetches them. Company data comes from the startup directory and job detail pages.

### Why are investor names or the full team missing?

Investor names and the full team are not exposed by Wellfound in structured form. `companyTopInvestors` is a boolean badge, not a list of names, and `companyFounders` is limited to founders shown on a job detail page. `yearsExperienceMax` is likewise never populated; only `yearsExperienceMin` is available.

### Can I get every job at one company?

No. Company pages are unavailable and the startup directory only exposes counts, so the actor cannot enumerate every job at one company. Search pages show a subset of each startup's open roles.

### Why are some fields missing from a record?

Wellfound does not expose every field for every job or company. Conditional fields such as skills, founders, funding, socials, perks and equity appear only when the source provides them. Empty fields are omitted and never replaced with `null` or a placeholder.

### Is this affiliated with Wellfound?

No. This is an independent tool that reads Wellfound's public pages and is not affiliated with, endorsed by or sponsored by Wellfound or AngelList.
