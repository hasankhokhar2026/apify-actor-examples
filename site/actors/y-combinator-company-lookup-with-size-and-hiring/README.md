# Y Combinator Company Lookup with Size & Hiring Filters

Y Combinator's directory makes you pick one filter at a time. This actor lets you ask for "active fintech companies launched after 2020 with 10+ employees that have open engineering roles" in one run, or look up a known list of companies by profile URL or slug. It returns clean, consistent company records with founders, the complete open-job list, news, founder Q&A and permanent media URLs.

## What this actor does

- Searches the full YC company directory by free-text query, batch, industry, sub-industry, status, stage, region or tag
- Filters by team-size range, launch-year range, hiring badge, live open jobs, top-company / nonprofit badges, and founder social presence
- Isolates companies from YC's official Black-founded, women-founded and Hispanic/Latino-founded lists
- Looks up specific companies directly by profile URL or slug, with the same enrichment and filters
- Adds founders, complete open-job lists, news, Launch YC posts, founder Q&A, company photos and canonical image URLs
- Optionally adds each founder's directory profile (schools, previous roles, previous YC companies) and each job's full description and hiring manager
- Returns more than 1,000 rows: the directory is fetched batch by batch and de-duplicated, so the whole index is available
- Omits a field instead of inventing a value when YC has no data for it

## Data source

The directory search uses the public Algolia index behind `ycombinator.com/companies`. YC rotates the search key, so the actor reads the current key from the page and refreshes it automatically if Algolia rejects it. Company details, founders, jobs, news, launches and Q&A come from the Inertia data embedded in each profile page. Founder schools and previous roles come from `/founders/<id>`; job descriptions and hiring managers come from `/companies/<slug>/jobs/<token>`. No cookies, login, proxy or API key are needed.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `directoryUrl` | string | `https://www.ycombinator.com/companies` | Directory URL. Query-string filters in a pasted URL (`batch`, `industry`, `status`, `stage`, `region`, `tag`, `q`) are applied. |
| `companyUrls` | array | `[]` | Direct YC company profile URLs, fetched independently of the directory search |
| `companySlugs` | array | `[]` | Direct YC company slugs, e.g. `airbnb`, `stripe` |
| `query` | string | – | Free-text search across names, descriptions and tags |
| `batches` | array | `[]` | Batch short codes or full names (`S24`, `W24`, `SP25`, `Summer 2024`). Empty means every batch. |
| `industries` | array | `[]` | Exact YC industry values, e.g. `B2B`, `Consumer`, `Fintech`, `Healthcare` |
| `subIndustries` | array | `[]` | Exact or leaf sub-industry values, e.g. `Infrastructure`, `Travel, Leisure and Tourism` |
| `statuses` | array | `[]` | `Active`, `Inactive`, `Acquired`, `Public` |
| `stages` | array | `[]` | `Early` or `Growth` (YC does not expose stage as a facet, so this is applied client-side) |
| `regions` | array | `[]` | Exact YC region values (`Europe`, `America / Canada`, `Remote`, `Fully Remote`, …) or a free-text location |
| `tags` | array | `[]` | Exact YC tags (`AI`, `B2B`, `SaaS`, …); any one match is enough |
| `teamSizeMin` | integer | – | Drop companies with fewer employees |
| `teamSizeMax` | integer | – | Drop companies with more employees |
| `foundedAfterYear` | integer | – | Keep companies launched in or after this year |
| `foundedBeforeYear` | integer | – | Keep companies launched in or before this year |
| `hiringOnly` | boolean | false | Keep only companies carrying YC's hiring badge |
| `onlyWithOpenJobs` | boolean | false | Keep only companies whose profile actually lists at least one open job |
| `requireFounderSocial` | boolean | false | Keep only companies where at least one founder has a social or website link |
| `topCompaniesOnly` | boolean | false | Keep only YC top companies |
| `nonprofitOnly` | boolean | false | Keep only YC nonprofits |
| `highlightBlackFounders` | boolean | false | Keep only companies on YC's official Black-founded list |
| `highlightWomenFounders` | boolean | false | Keep only companies on YC's official women-founded list |
| `highlightHispanicFounders` | boolean | false | Keep only companies on YC's official Hispanic/Latino-founded list |
| `scrapeFounders` | boolean | true | Add founders from each company profile |
| `scrapeFounderProfiles` | boolean | false | Add founder-directory data (schools, previous roles, previous YC companies, profile URL) |
| `scrapeOpenJobs` | boolean | true | Add each company's complete open-job list |
| `includeJobDetails` | boolean | false | Add each job's description, interview process and hiring manager |
| `includeNews` | boolean | true | Add news items linked from the company profile |
| `includeLaunchPosts` | boolean | false | Add Launch YC posts, including the full post body |
| `includeQa` | boolean | true | Add founder Q&A answers |
| `includeVideos` | boolean | false | Add YC library / YouTube videos and app or demo-day videos |
| `sortBy` | select | `launchDateDesc` | `launchDateDesc`, `launchDateAsc`, `nameAsc`, `teamSizeDesc`, `teamSizeAsc` |
| `maxItems` | integer | 3 | Maximum companies to return. `0` returns every match (capped at 10,000 per run). |
| `maxConcurrency` | integer | 8 | Parallel profile / job / founder page fetches (1–32) |
| `emitErrorRecord` | boolean | true | Push one diagnostic record when nothing matches. Upstream failures always fail the run. |

### Legacy input compatibility

Older saved tasks use `batch`, `industry` and `status` instead of `batches`, `industries` and `statuses`. Those keys are no longer shown in the form, but the actor still reads them and maps them onto the new fields.

### Example: active fintechs launched after 2020 with open jobs

```json
{
  "directoryUrl": "https://www.ycombinator.com/companies",
  "industries": ["Fintech"],
  "statuses": ["Active"],
  "foundedAfterYear": 2020,
  "teamSizeMin": 10,
  "onlyWithOpenJobs": true,
  "maxItems": 100
}
```

### Example: whole directory

```json
{
  "directoryUrl": "https://www.ycombinator.com/companies",
  "maxItems": 0,
  "sortBy": "launchDateDesc",
  "scrapeFounders": true,
  "scrapeOpenJobs": true,
  "includeNews": true,
  "includeQa": true
}
```

### Example: direct lookup with founder profiles and job details

```json
{
  "companySlugs": ["airbnb", "stripe", "whatnot"],
  "scrapeFounderProfiles": true,
  "includeJobDetails": true
}
```

## Output per company

| Field | Description |
|---|---|
| `type` / `recordType` | `yc_company` for a company, `y_combinator_scraper_pro_error` for a diagnostic record |
| `id` / `slug` / `url` | Company slug and YC profile URL |
| `name` | Company name |
| `shortDescription` / `longDescription` | One-line and long descriptions from YC |
| `batch` / `batchLong` | Short batch code (`W09`) and full batch name (`Winter 2009`) |
| `industry` / `industries` / `subIndustry` | YC's primary industry, full industry list and leaf sub-industry |
| `status` / `stage` | Operating status and Early/Growth stage |
| `location` / `allLocations` / `city` / `country` / `regions` | Every location YC lists, plus structured city/country and region facets |
| `foundingYear` / `launchedAt` / `launchedAtIso` / `companyAge` | Founding year, launch timestamp (Unix and ISO) and age in years |
| `teamSize` | Employee count (omitted when YC reports 0/unknown) |
| `website` / `linkedin` / `twitter` / `facebook` / `crunchbase` / `github` | Real company links from the profile |
| `logo` / `logoThumb` / `companyPhotos` | Permanent, non-expiring image URLs (signatures stripped) |
| `isHiring` / `topCompany` / `nonprofit` | YC badges, present only when true |
| `hasOpenJobs` / `jobCount` / `jobLocations` | Whether the profile lists jobs, how many, and the de-duplicated locations |
| `tags` / `formerNames` | Tags and previous company names |
| `ycdcStatus` / `ycInternalId` | YC's own status and numeric company id |
| `primaryPartner` | `{ name, title, url, linkedin, avatarUrl }` for the YC partner on the company |
| `questionsAndAnswers` | `{ qaId, question, answer }` founder Q&A blocks |
| `news` | `{ title, url, date }` news items |
| `launchPosts` | `{ launchId, title, url, date, dateIso, tagline, voteCount, body }` when enabled |
| `videos` | `{ videoId, title, videoUrl, libraryUrl, date }` for permanent video links |
| `highlightBlackFounders` / `highlightWomenFounders` / `highlightHispanicFounders` | Present and `true` when the company is on the corresponding official list (lists are fetched only when a diversity filter is active) |
| `founders` | `{ name, title, bio, linkedin, twitter, hackerNews, github, instagram, avatarUrl, ycUserId, isActive, email, latestYcCompany, previousCompanies, education }` plus `founderProfileUrl`, `schools`, `previousRoles`, `previousYcCompanies`, `website`, `substack`, `bluesky` when founder profiles are enabled |
| `openJobs` | `{ jobId, title, url, applyUrl, location, remote, remoteFriendly, type, role, roleSpecificType, team, yearsExperience, salaryMin, salaryMax, compensationCurrency, equity, equityRange, skills, experience, minSchoolYear, visa, visaSupported, englishFluent, askUs, hiringManager, postedAtRelative, lastActiveRelative }` plus `description` and `interviewProcess` when job details are enabled |
| `scrapedAt` | UTC timestamp when the record was produced |

Every nested object follows the same omit-empty rule: a key appears only when YC actually supplies a value.

## How the directory is fetched

A single YC search query stops at 1,000 results, no matter how many batches match. The actor instead queries all 51 batch facets in one multi-query, merges the results and de-duplicates by slug. That currently covers the entire index (about 6,400 companies), and `maxItems: 0` returns all of them. Runs are capped at 10,000 rows.

## Limitations

- YC's search index currently contains about 6,400 public companies. That is the source's own ceiling, not a cap in this actor.
- Stage (`Early` / `Growth`) is not a searchable facet, so stage filtering happens after records are fetched.
- The diversity filters use YC's official opt-in lists. A company absent from a list is not evidence about its founders; it only means YC does not publish that company on that list.
- `onlyWithOpenJobs` and `requireFounderSocial` need the company profile page, so they add one request per candidate.
- `scrapeFounderProfiles` adds one request per founder and `includeJobDetails` adds one request per open job. Large hiring companies can have 100+ jobs.
- App and demo-day videos are served with one-hour signatures. When `includeVideos` is on, those files are re-hosted in the run's key-value store and both the permanent URL and the original URL are returned. Without `includeVideos`, expiring video URLs are omitted rather than returned broken.
- If a YC profile page is temporarily unavailable, its record is returned with search-index fields only and the run log lists the failure. Upstream search failures fail the run instead of returning a partial directory.
- YC changes its markup and keys from time to time. This actor reads structured Inertia JSON and the public Algolia configuration rather than scraping HTML classes, which keeps it stable across layout changes.

## Use cases

- **VC and angel sourcing** — shortlist companies in a size, batch and stage window
- **Recruiting pipelines** — pull companies with live open roles and their complete job lists
- **Founder outreach** — filter to companies whose founders already have a public social profile
- **Diversity-focused sourcing** — use YC's official Black-founded, women-founded and Hispanic/Latino-founded lists
- **Market research** — export the full directory with industry, region and hiring signals

## FAQ

**Is this affiliated with Y Combinator?**
No. This is an independent data extraction tool with no connection to Y Combinator.

**How is this different from browsing the directory?**
It combines filters the directory cannot apply together, covers the whole index instead of a single page, and attaches founders, jobs, news and Q&A in the same run.

**What happens if nothing matches?**
With `emitErrorRecord` on, the run pushes one record explaining why the dataset is empty. Upstream failures fail the run and never produce a success record.

**Do I need a proxy or cookies?**
No.

**Can I get more than 1,000 companies?**
Yes. The actor fans out across every batch and de-duplicates, so the full index is available. Set `maxItems` to `0`.

**Why does `jobCount` differ from the badge?**
`isHiring` is YC's badge. `jobCount` is the number of jobs actually listed on the profile; a company can carry the badge with no currently open postings.
