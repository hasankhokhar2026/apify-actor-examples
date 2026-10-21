# LinkedIn Public Profile Credentials & Company Lookup

Look up a batch of LinkedIn profile URLs or usernames and get back their public credentials — certifications, honors, test scores, volunteer work, and projects — alongside standard work and education history, with the current employer's own LinkedIn company page attached for context. Everything is read from the logged-out public profile view, so no LinkedIn account or cookie is ever needed.

## What this actor does

- Looks up each profile from a plain list of URLs or usernames, no login or session cookie involved
- Pulls name, headline, location, summary, current and past employers, and schools
- Reads the credential sections a profile shows to guests: certifications (with credential ID and verification link), honors & awards, test scores, organization memberships, volunteer experience, projects, and listed websites
- Attaches the current employer's own company page (size, industry, headquarters, website, logo) when `enrichCompany` is on
- Checks that the profile returned actually matches the one requested, and drops any text LinkedIn has redacted instead of passing along masked placeholder characters
- A profile's row only contains the sections that profile actually has filled in — missing sections are left out rather than returned empty

## Output per profile

- `name`, `headline`, `location`, `summary`
- `profileUrl`, `profilePicture`
- `currentTitle`, `allTitles`
- `currentCompany` — always `name`, `url` and `slug` (plus `companyId` for numeric company links) when the profile shows a current employer; with `enrichCompany: true` and a readable company page, also `employeeCount`, `size`, `industry`, `website`, `headquarters`, `organizationType`, `logoUrl`, `specialties`
- `currentPositions`, `pastPositions` — `company`, `companyUrl`, `startDate`, `endDate`, `location` (per-position job titles aren't in the logged-out view; titles are collected in `allTitles`)
- `experiences` — `currentPositions` and `pastPositions` combined into a single list
- `education` (and `educations`, the same list under both keys) — `school`, `schoolUrl`, `startDate`, `endDate`
- `certifications` — `name`, `issuer`, `issuerUrl`, `issueDate`, `credentialId`, `credentialUrl`
- `honorsAndAwards` — `title`, `issuer`, `date`, `description`
- `testScores` — `name`, `score`, `date`
- `organizations` — `name`, `position`, `description`
- `volunteerExperience` — `role`, `organization`, `description`
- `projects` — `title`, `dateRange`, `description`
- `websites` — `label`, `url`
- `followersCount`
- `recentArticles` — `title`, `url`, `publishedDate`, `text`, `likes`
- `inputUrl`, `order` — the value you supplied and its zero-based position in the input list
- `scrapedAt` — ISO 8601 timestamp

Some profiles only expose LinkedIn's sign-up preview to logged-out visitors. For those, the row holds just `name`, `headline`, `summary`, `profileUrl` and `profilePicture`, plus `inputUrl`, `order` and `scrapedAt`.

### Run status rows

Besides profile rows, the dataset may hold one status row:

- `_status: "no_data"` with `_reason: "no_results"`, `_message`, `_help` and `scrapedAt` — when no requested profile could be read.
- `_status: "partial_results"` with `_reason` (a single cause or `mixed`), `_failureBreakdown` (counts keyed by `auth_wall`, `not_found`, `blocked`, `identity_mismatch`, `invalid_url` or `error`), `_message` and `scrapedAt` — when some profiles failed; it sits alongside the successful rows.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `profileUrls` | array | – | LinkedIn profile URLs or bare usernames to look up. Required, at least one. |
| `enrichCompany` | boolean | `true` | Attach the current employer's own LinkedIn company page details. Adds one extra request per unique company. |
| `proxyConfiguration` | object | – | Not used by the actor; any value here is ignored |

Accepted formats for each list entry: `https://www.linkedin.com/in/username`, `linkedin.com/in/username`, `in/username`, or a bare `username`.

### Example: batch lookup with company data

```json
{
  "profileUrls": [
    "https://www.linkedin.com/in/williamhgates",
    "https://www.linkedin.com/in/satyanadella"
  ],
  "enrichCompany": true
}
```

### Example: usernames only, no company enrichment

```json
{
  "profileUrls": ["williamhgates", "reidhoffman"],
  "enrichCompany": false
}
```

## Use cases

- **Credential verification** — confirm listed certifications, honors, and test scores before a hiring decision
- **Recruiting pipelines** — pull work history and education for a shortlist of candidate profile URLs in one batch
- **Vendor and partner vetting** — check a contact's current role and employer company profile before a deal
- **Sales enablement** — attach company size, industry, and HQ to a contact list automatically
- **Research datasets** — build a structured sample of career and credential data across many profiles

## FAQ

**Is a LinkedIn login or cookie required?**
No. Every profile is read the way a logged-out visitor would see it; no credentials or session cookie are used.

**What exactly does `enrichCompany` add?**
It fetches the current employer's own LinkedIn company page and attaches `currentCompany` fields like headcount, industry, headquarters, website, and logo. It only covers the current employer, not past employers.

**Why are some certification or honor fields missing?**
Those sections only appear when the profile owner filled them in on LinkedIn. If a profile has no listed certifications, for example, the `certifications` field is left out of that row entirely.

**Can this return a person's email or phone number?**
No. Contact details aren't shown on the logged-out public profile page, so the actor can't extract them and never fabricates a value.

**Why might `currentTitle` be blank while `currentCompany.name` is filled in?**
LinkedIn sometimes withholds job-title text from logged-out viewers for a specific profile while still showing the employer name. When the title is withheld, it's omitted rather than replaced with placeholder text.

**Does input order matter?**
Each row carries `order`, matching its position in your `profileUrls` list, so you can line results back up with your original input even if requests complete out of order.

**What happens for a profile that's fully private?**
No profile row is returned for it; it is counted in the run's status row instead. That's the profile owner's own privacy setting, not something this actor can work around. Profiles counted as `blocked` were refused by LinkedIn on that run and often succeed when retried later.

**Is this the same as scraping LinkedIn's authenticated member API?**
No — skills, languages, and anything else gated behind a logged-in LinkedIn session are not available here, since only the public profile page is read.

**Is this affiliated with LinkedIn?**
No. This is an independent, third-party actor that reads publicly available LinkedIn pages; it is not operated by or affiliated with LinkedIn.
