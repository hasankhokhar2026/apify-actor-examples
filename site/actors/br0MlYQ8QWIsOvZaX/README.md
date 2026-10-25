# B2B Lead Discovery by Job Title & Location

Find public LinkedIn profiles by job title, location, and company using cookieless Yahoo search. No login, cookies, or API keys are required.

## What this actor does

- Builds `site:linkedin.com/in` queries from one or more job titles, optionally combined with locations and company names.
- Parses public search-result snippets into lead records and deduplicates by canonical LinkedIn profile URL.
- Adds honest data-quality flags instead of presenting inferred values as verified facts.
- Optionally adds an explicitly unverified email-pattern guess. It never claims a mailbox was verified.

## Output per lead

| Field | Description |
|---|---|
| `name` | Profile name. |
| `title` | Current headline/title when the card or snippet exposes it. |
| `company` | Company when exposed by the card, snippet, or title. |
| `location` | Location when exposed by the card, snippet, or title. |
| `linkedinUrl` | Canonical `https://www.linkedin.com/in/<slug>` URL. |
| `snippet` | Public Yahoo search snippet (truncated). |
| `sourceQuery` | Query that produced the lead. |
| `position` | Position on the results page (stable ordering). |
| `scrapedAt` | ISO 8601 UTC timestamp. |
| `dataQuality` | `title`, `company`, and `location` are `verified`, `inferred`, `missing`, or `mismatch`; `partial` is added when the query plan was capped or a query failed. |
| `emailGuess` / `emailGuessStatus` / `emailGuessNote` | Only with `includeEmailGuess`; a pattern guess whose domain has MX records. **Not verified.** |

Fields that cannot be resolved are omitted rather than filled with placeholders.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `jobTitles` | array | required | Titles to search, e.g. `["CEO", "VP of Marketing"]` (max 10). |
| `locations` | array | `[]` | Locations such as `"Austin, Texas"` (max 10). |
| `companyNames` | array | `[]` | Companies to target (max 5). |
| `maxLeads` | integer | `25` | Maximum leads to return (1-100). |
| `includeEmailGuess` | boolean | `false` | Add unverified name/domain email guesses. |
| `proxyConfiguration` | object | none | Optional Apify proxy. Yahoo may block datacenter IPs. |

Hard limits: 24 queries per run, 3 pages per query, 5 leads per company.

## Example

```json
{
  "jobTitles": ["CEO"],
  "locations": ["Austin, Texas"],
  "maxLeads": 25
}
```

## Data quality and limits

- Yahoo Search is an unofficial, cookieless source and may block or throttle requests. The actor retries and can use Apify proxy, but runs can return partial results.
- Location fill is roughly 50% and location precision among filled rows is about 75%; some snippets omit location entirely.
- Titles/companies can be inferred from headlines. Check `dataQuality` before using a row for outreach.
- Verified email and phone are not available from public search alone; email guesses are unverified pattern guesses, not mailbox checks.

## Use cases

- Recruiting and sourcing by title and region.
- Market/account mapping across named companies.
- Building shortlists for manual review before outreach.

## Backward-compatible fields

The pre-revamp snake_case output is preserved alongside the new fields: `full_name`, `first_name`, `last_name`, `linkedin_url`, `company_name`, `company_domain`, `email`, and `scraped_at`. They are emitted only when a value exists; `email` is the same unverified guess as `emailGuess`.
