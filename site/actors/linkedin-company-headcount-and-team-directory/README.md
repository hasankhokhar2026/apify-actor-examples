# LinkedIn Company Headcount & Team Directory Scraper

Get a company's LinkedIn-reported headcount and firmographics without logging in — employee count, size band, followers, industry, headquarters, type, website, address, about text, specialties, and logo. Add your own LinkedIn session cookie only when you also want the optional employee roster.

## What this actor does

- **Cookieless headcount first:** one `recordType: company` row per input with LinkedIn's reported employee count, size band, followers, industry, HQ, type, website, address, specialties, and logo.
- **Domain-aware company resolution:** accepts LinkedIn URLs, company domains, and names; mixed inputs are allowed. A URL is trusted, a domain is confirmed against the page's website (including rebranded hosts such as `notion.so` → `notion.com`), and a name must match the page exactly with a matching website or enough follower authority.
- **Honest ambiguity handling:** bare-name inputs such as Notion, Linear, or Cal can collide with a different same-name LinkedIn page. Those return an explicit error row instead of a silent wrong-company match; domain forms such as `cal.com` resolve normally.
- **Optional cookie roster:** with a valid cookie, fetches up to 2,500 visible employees per company in 10-row pages, with title, location, seniority, function, connection degree, language, and resume-from-page filters.
- **Explicit coverage and confidence:** every company row carries `headcountConfidence`, `employeesReported`, `employeesReturned`, and a `coverage` block. Error rows have an `errorCode`, so a missing roster never looks like a complete one.
- **Empty fields are omitted:** missing values are left out instead of being returned as `null`.

## Output per company (`recordType: "company"`)

- `input` — the value you supplied
- `companyName`, `companySlug`, `companyUrl`
- `linkedinCompanyId` — numeric LinkedIn organization ID
- `resolutionMethod` — `provided_url`, `domain_slug`, or `name_variant`
- `resolutionConfidence`, `confidence` — `high` for a validated page
- `resolutionCandidates` — alternate slugs tried, when any
- `linkedinEmployeeCount` — LinkedIn-reported employee count
- `linkedinEmployeeCountSource` — `public_company_page`
- `companySizeRange` — LinkedIn's band, e.g. `5,001-10,000 employees`
- `headcountConfidence` — `high` when the count is inside the band or the band is open-ended; `medium` up to 2x above; `low` above 2x
- `headcount` — `{ reported, sizeBand, asOf, source, audited: false }`; the count is never described as audited
- `followerCount`, `industry`, `headquarters`, `companyType`
- `website`, `primaryAddress`, `address`
- `about`, `tagline`, `specialties[]`, `locations[]`, `logoUrl`
- `employeesReported` — LinkedIn's company count
- `employeesReturned`, `employeesCoveragePct`
- `rosterMode` — `cookieless` or `cookie`
- `rosterAvailable`, `rosterReportedTotal`, `rosterRowsReturned`, `rosterCoveragePct`, `rosterConfidence`, `rosterReason`
- `coverage` — `{ employeesReturned, employeesReported, rosterReportedTotal, rosterCoveragePct, rosterAvailable, rosterConfidence }`
- `filtersApplied` — the roster filters that were sent
- `sourceMode` — `cookieless_public_page`
- `warnings[]` — human-readable caveats
- `recordType`, `scrapedAt`

## Output per employee (`recordType: "employee"`)

- `companySlug`, `companyName`, `currentCompany`
- `name`, `firstName`, `lastName`, `publicIdentifier`
- `headline`, `currentTitle`, `currentDepartment`, `department`
- `seniority`, `senioritySource` — derived from the title when LinkedIn does not expose a seniority field
- `location`, `country`
- `profileUrl`
- `profilePicture`, `profileImageUrl`, `profilePictureUrl`
- `tenure`, `tenureYears`, `tenureSource` — only when LinkedIn exposes a duration
- `connectionDegree`
- `industryName`, `currentCompanyLogo`
- `openToWork`, `premium`, `verifiedStatus` — only when the badge is present
- `email`, `emailSource` — only if an email is explicitly visible; usually absent
- `source` — `cookie-roster`
- `sourceMode` — `cookie_voyager`
- `companyFilterApplied` — `true`; rows are only returned when the company filter was applied
- `confidence` — `high` with a headline, `medium` otherwise
- `recordType`, `scrapedAt`

## Output per error (`recordType: "error"`)

- `input`, `companySlug`, `companyName` (when known)
- `errorCode` — `ambiguous_company_name`, `company_not_found`, `company_unresolved`, `rate_limited` (the public company page returned 999/429), `cookie_missing`, `cookie_invalid`, `company_id_unresolved`, `roster_rate_limited`, `roster_request_budget_reached`, or `roster_unavailable`
- `error`, `message`, `help`
- `retryable`
- `resolutionCandidates`, `rejectedCandidates` — for resolution failures
- `recordType`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `companyUrls` | array | `[]` | LinkedIn company URLs, e.g. `https://www.linkedin.com/company/stripe/` |
| `companyDomains` | array | `[]` | Company domains, e.g. `stripe.com`, `notion.so`, or `cal.com` |
| `companyNames` | array | `[]` | Company names, e.g. `Stripe`; ambiguous names need a URL or domain |
| `includeEmployees` | boolean | `false` | Also request the optional employee roster (requires a valid cookie) |
| `maxEmployees` | integer | `100` | Roster cap per company (1–2500); ignored without `includeEmployees` |
| `maxItemsTotal` | integer | `500` | Hard cap on all dataset rows (1–10000) |
| `startPage` | integer | `1` | Resume the roster from this 10-row page (1–250) |
| `titleKeywords` | string | – | Roster filter on role/headline, e.g. `Software Engineer` |
| `location` | string | – | Best-effort roster filter on the employee's LinkedIn location |
| `seniorityLevels` | array | `[]` | `Entry`, `Associate`, `Mid-Senior`, `Director`, `Executive` |
| `functions` | array | `[]` | `Engineering`, `Sales`, `Marketing`, `Operations`, `Finance`, `Human Resources`, `Design`, `Product`, `Customer Service`, `Information Technology`, `Legal`, `Other` |
| `connectionDegree` | string | `""` | `""` (all), `F` (1st), `S` (2nd), `O` (3rd+) |
| `language` | string | `""` | Profile language: `en`, `es`, `fr`, `de`, `pt`, `it`, `nl`, `zh`, `ja` |
| `cookies` | string | – | Optional LinkedIn cookie for the roster (`li_at` or a full cookies JSON array) |
| `proxyConfiguration` | object | – | Optional advanced override; no proxy setup is required |

Provide at least one of `companyUrls`, `companyDomains`, or `companyNames`. You can mix them in one run.

### Example: cookieless headcount for mixed inputs

```json
{
  "companyUrls": ["https://www.linkedin.com/company/stripe/"],
  "companyDomains": ["notion.so", "linear.app"],
  "includeEmployees": false,
  "maxItemsTotal": 10
}
```

### Example: batch headcount by name

```json
{
  "companyNames": ["Microsoft", "HubSpot", "Figma"],
  "includeEmployees": false,
  "maxItemsTotal": 20
}
```

### Example: roster for one company with a cookie

```json
{
  "companyDomains": ["raycast.com"],
  "includeEmployees": true,
  "maxEmployees": 50,
  "titleKeywords": "Engineer",
  "seniorityLevels": ["Mid-Senior", "Director"],
  "maxItemsTotal": 100,
  "cookies": "YOUR_LI_AT_COOKIE"
}
```

### Example: resume a capped roster

```json
{
  "companyUrls": ["https://www.linkedin.com/company/microsoft/"],
  "includeEmployees": true,
  "maxEmployees": 100,
  "startPage": 26,
  "maxItemsTotal": 200,
  "cookies": "YOUR_LI_AT_COOKIE"
}
```

## Use cases

- **Account research** — capture headcount, size band, HQ, industry, and website for a list of target companies without a LinkedIn login.
- **Market mapping** — compare headcount and follower counts across a segment of public and private companies.
- **Recruiting and sourcing** — pair cookieless firmographics with an optional roster when you have a session that can see the people tab.
- **Sales operations** — enrich CRM accounts with LinkedIn-reported size and industry fields.
- **Competitive tracking** — periodically snapshot headcount, followers, and specialties for competitor pages.
- **Data quality checks** — use `headcountConfidence` to flag companies whose reported count and size band disagree.

## Limitations and caps

- **Headcount is LinkedIn-reported, not audited.** The public count can differ from LinkedIn's own size band; both fields are returned and `headcountConfidence` labels the gap. It is not a payroll, HRIS, or verified workforce count.
- **The roster is optional and cookie-gated.** Without a valid cookie only the company row is returned, with an explicit warning and no employee rows.
- **LinkedIn caps a roster query at 2,500 visible results.** Pages contain 10 rows, so a query can need up to 250 requests. The actor budgets about 250 roster requests per run to stay inside LinkedIn's daily limit; when the budget is used, the remaining companies get an explicit error row and a later run can resume with `startPage`. Large companies are samples rather than complete workforces.
- **`maxEmployees` is the per-company cap.** If LinkedIn reports more employees than the cap, the row set is a sample; `rosterReportedTotal` and `rosterCoveragePct` make the shortfall visible.
- **Filters are best-effort.** Title, seniority, function, connection degree, and language are sent to LinkedIn; location is matched against the returned location text. Missing fields are not used to exclude a row.
- **Email is not harvested.** It is returned only when an email is explicitly visible on the result; expect none. Tenure is returned only when LinkedIn exposes a duration.
- **Past employees are not supported.** The actor returns current employees when a roster is requested.
- **Name-only resolution is restricted.** Ambiguous bare names (Notion, Linear, Cal, and similar) return an error row. Pass the LinkedIn URL or the company domain instead (for example `cal.com` for Cal.com).
- **Public pages can rate-limit.** If LinkedIn throttles the company page itself, the actor emits a retryable `rate_limited` error row instead of a company row. If it throttles a roster request, the company row is still returned with a warning. Retry later or narrow the input list.

## FAQ

**Do I need a LinkedIn cookie for headcount?**
No. Company name, LinkedIn-reported employee count, size band, followers, industry, HQ, type, website, address, about, specialties, and logo come from the public company page.

**When do I need a cookie?**
Only for the employee roster. Set `includeEmployees` to `true` and add a valid `li_at` value or full cookie export. The cookie is never required for the company row.

**Why did I get an error row instead of employees?**
The run tells you which case applies: `cookie_missing` (no cookie), `cookie_invalid` (expired or rejected session), `company_id_unresolved` (the roster filter could not be mapped), `roster_rate_limited` (LinkedIn returned 999/429), or `roster_request_budget_reached` (the ~250-request run budget was used). Company headcount is still returned whenever the page resolves.

**Why does the employee count disagree with the size band?**
LinkedIn shows two independent fields. A company can report 7,000 employees while its self-selected band says 501–1,000. The actor publishes both and labels the count `high`, `medium`, or `low` confidence rather than presenting either as audited.

**Why is the roster smaller than the company's headcount?**
LinkedIn caps a single query at 2,500 visible results and serves 10 per page; the daily request limit is about 250. For a large employer, the roster is a sample. Raise `maxEmployees`, split the request with `startPage`, or narrow the filters.

**Why did my company name resolve to a different company?**
Some names are shared by several LinkedIn pages. The actor refuses the low-confidence name match and asks for a URL or domain. For example, `notion.so` resolves to the right Notion page, while the name alone is treated as ambiguous.

**Can I get email addresses?**
Only if LinkedIn explicitly shows an email in the result. The actor does not guess or construct emails, so most records have no email field.

**Can I get tenure?**
Only when LinkedIn exposes a duration for the person. Otherwise `tenure` and `tenureYears` are omitted instead of estimated.

**Does the actor return past employees?**
No. The roster is current employees only.

**Is this affiliated with LinkedIn?**
No. This is an independent, third-party actor. It uses publicly visible company pages and, when you supply one, your own LinkedIn session for the roster. You are responsible for how you use the data.
