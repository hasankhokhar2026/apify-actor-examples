# LinkedIn Company Headcount & Team Directory Scraper

List the people who work at a LinkedIn company page, narrowed by role keyword, seniority, job function, connection degree, or current-versus-past employment, so you get a usable team directory instead of scrolling through LinkedIn's own people-search results by hand.

## What this actor does

- Lists employees for one or more LinkedIn company pages in a single run
- Narrows results by keyword, connection degree, seniority level, job function, current-vs-past employment, and profile language (location is best-effort, see the FAQ)
- Returns each person's headline, current title, department, location, tenure, and profile picture when LinkedIn exposes them
- Flags Open to Work and Premium badges on each profile
- Fields a profile doesn't show (e.g. no tenure, no verified badge) are left out of that record

## Output per employee

- `name`, `headline`, `profileUrl`, `profilePicture`/`profileImageUrl`
- `location`, `industryName`
- `currentTitle`, `currentDepartment` — parsed from the profile headline
- `currentCompanyLogo`
- `tenure` — years at the company, when derivable from the profile
- `connectionDegree` — `DISTANCE_1`, `DISTANCE_2`, `DISTANCE_3`, or `OUT_OF_NETWORK`
- `openToWork` — `true` when the profile shows the Open to Work badge
- `premium` — `true` when the profile shows a LinkedIn Premium badge
- `verifiedStatus` — `true` when the profile shows a verified badge
- `currentCompany` — a display name built from the company slug (e.g. `hubspot` becomes `Hubspot`)
- `companySlug` — normalized LinkedIn company slug
- `scrapedAt` — ISO 8601 timestamp

If the cookie is missing, or LinkedIn rejects it before any company is read, the dataset instead gets a single status row rather than employee records: `_status: "no_data"`, `_reason` (`cookie-missing` or `cookie-invalid`), `_message`, `_help` and `scrapedAt`. If the session expires part-way through, the run stops and keeps the employees already saved.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `companyUrls` | array | – | LinkedIn company page URLs or slugs. Required. |
| `cookie` | string | – | Your LinkedIn session cookie (`li_at` value or full cookies JSON array). Required. |
| `maxEmployees` | integer | `50` | Maximum employee profiles to collect per company (1–1000) |
| `keywords` | string | – | Free-text filter matched against role/headline (e.g. `Software Engineer`, `VP Sales`) |
| `location` | string | – | Location filter (e.g. `New York`, `London`). Only applied when LinkedIn's main people search is unavailable and an older search is used, so usually it has no effect |
| `connectionDegree` | string | `""` (all) | `F` (1st-degree), `S` (2nd-degree), or `O` (3rd-degree+) |
| `seniorityLevel` | string | `""` (all) | `Entry`, `Associate`, `Mid-Senior`, `Director`, or `Executive` |
| `function` | string | `""` (all) | Job function such as `Engineering`, `Sales`, `Marketing`, `Product` |
| `currentCompany` | boolean | `true` | When `true`, search current employees; when `false`, search past employees instead |
| `language` | string | `""` (any) | Filter by profile language: `en`, `es`, `fr`, `de`, `pt`, `it`, `nl`, `zh`, `ja` |
| `proxyConfiguration` | object | – | Optional Apify proxy configuration; a residential proxy is recommended |

### Example: engineers at a company

```json
{
  "companyUrls": ["https://www.linkedin.com/company/hubspot/"],
  "cookie": "YOUR_LI_AT_COOKIE",
  "keywords": "Software Engineer",
  "maxEmployees": 100
}
```

### Example: senior sales leaders, current employees only

```json
{
  "companyUrls": ["microsoft"],
  "cookie": "YOUR_LI_AT_COOKIE",
  "function": "Sales",
  "seniorityLevel": "Director",
  "currentCompany": true
}
```

### Example: employees across multiple companies

```json
{
  "companyUrls": ["https://www.linkedin.com/company/hubspot/", "stripe"],
  "cookie": "YOUR_LI_AT_COOKIE",
  "keywords": "London",
  "maxEmployees": 200
}
```

## Use cases

- **Recruiting** — find engineers, designers, or executives currently working at a target company
- **Sales prospecting** — build a contact list of decision-makers at prospective accounts
- **Org mapping** — understand how a company's workforce is distributed by function and seniority
- **Competitive intelligence** — track who a competitor employs in a given department
- **Alumni tracking** — set `currentCompany: false` to list people who previously worked there

## FAQ

**How many employees can I get per company?**
Up to 1,000 via `maxEmployees`, though LinkedIn typically surfaces a few hundred to around a thousand visible profiles for large companies — very large employers may show a partial sample rather than every employee.

**Do I need a LinkedIn session cookie?**
Yes. Listing a company's employees requires an authenticated LinkedIn session, so `cookie` is required.

**What's the difference between `keywords` and `seniorityLevel`/`function`?**
`keywords` is a free-text match against the profile's role/headline text. `seniorityLevel` and `function` are structured filters with a fixed set of values, which tend to return more consistent results than a keyword guess.

**Why is `tenure` missing for some employees?**
Tenure is derived from what LinkedIn exposes on the profile; when that information isn't shown, the field is left out instead of guessed.

**Can I get people who used to work at the company?**
Yes — set `currentCompany` to `false` to search the company's past employees.

**Are the filters always applied?**
`keywords`, `connectionDegree`, `seniorityLevel`, `function`, `currentCompany` and `language` are sent with LinkedIn's people search. `location` is only used by an older search the actor falls back to, so it usually doesn't narrow results; add the city to `keywords` instead if location matters. When the people search returns nothing at all, the actor reads LinkedIn's general search results or the company's People page as a last resort, and those rows only honour `keywords`. If the company's LinkedIn ID can't be looked up, results come from a plain keyword search and may include people from other companies.

**Will results include people outside my network?**
Yes, `connectionDegree` defaults to showing everyone found; use the `F`/`S`/`O` filter if you want to narrow to a specific connection degree.

**Is this affiliated with LinkedIn?**
No. This is an independent, third-party actor; it isn't operated by or affiliated with LinkedIn.
