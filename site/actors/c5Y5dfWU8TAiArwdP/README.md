# LinkedIn Public Profile Credentials & Company Lookup

Turn a list of public LinkedIn profile URLs or usernames into structured records: identity, work history with per-role detail, education, skills, languages, certifications, publications, recommendations, courses, honors, recent posts, and the current employer's own company page. Everything is read from the logged-out public view, so no LinkedIn account or cookie is ever needed.

## What this actor does

- **Profile lookup by URL or username** — paste full profile links, `linkedin.com/in/...` paths, `in/...`, or bare usernames; each input gets one row
- **Deep public sections** — per-role title, employer, dates, duration, employment type, location and description; education degree and field of study; skills; languages; certifications with credential IDs; publications; recommendations; courses; honors; projects; volunteer work; organizations; websites
- **Current-company intelligence** — followers, offices, affiliated pages, similar pages, recent updates, founded year, tagline, employee count, size, industry, website, headquarters, type, logo and specialties
- **Honest data quality** — `missingFields`, `dataQuality`, `pageVariant`, and a truthful error row for every input that cannot be read
- **Empty fields are omitted** — a row contains only fields the profile actually exposes; it never contains `null`, blank strings, or asterisk placeholders

## Output per profile

- `name`, `headline`, `location`, `summary`
- `profileUrl`, `profilePicture`, `publicIdentifier`
- `profileUrn`, `profileId` — stable member URN and numeric member ID for joins and de-duplication
- `currentTitle`, `allTitles`
- `currentCompany` — `name`, `url`, `slug` and, when readable, `companyId`, `employeeCount`, `size`, `industry`, `website`, `headquarters`, `organizationType`, `logoUrl`, `specialties`, `description`, `tagline`, `founded`, `followersCount`, `locations`, `affiliatedPages`, `similarPages`, `updates`. If enrichment still fails after retries on alternate company URLs, the row carries `enrichmentStatus: "failed"` and `enrichmentError` instead of silently emitting a name-only company.
- `currentPositions`, `pastPositions` — each with `company`, `companyUrl`, `title`, `startDate`, `endDate`, `duration`, `employmentType`, `location`, `description`
- `experiences` — current and past positions combined
- `education` and `educations` — the same list under both keys, with `school`, `schoolUrl`, `degree`, `fieldOfStudy`, `startDate`, `endDate`
- `followersCount`, `connectionsCount` — connections is the coarse public band, such as `500+`
- `badges`, `isCreator`, `isTopVoice`
- `skills` — skill names in the order shown on the profile
- `languages` — `name`, `proficiency`
- `publications` — `title`, `publisher`, `date`, `description`, `url`
- `recommendations` — `recommender`, `recommenderUrl`, `text`
- `courses` — `title`, `url`, `instructor`, `duration`, `viewers`
- `recentPosts` — `text`, `url`, `postedAgo`, `reactions`, `comments`, plus `author`/`authorUrl`; shares and reposts add `isRepost` and `repostedBy` while keeping the original author distinct
- `recentArticles` — genuine `/pulse/` articles only, with `title`, `url`, `publishedDate`, `text`, `likes`; posts never appear here
- `certifications` — `name`, `issuer`, `issuerUrl`, `issueDate`, `credentialId`, `credentialUrl`
- `honorsAndAwards` — `title`, `issuer`, `date`, `description`
- `testScores` — `name`, `score`, `date`
- `organizations` — `name`, `position`, `description`
- `volunteerExperience` — `role`, `organization`, `description`
- `projects` — `title`, `dateRange`, `description`
- `websites` — `label`, `url`
- `pageVariant`, `dataQuality`, `missingFields`, `partialFields`
- `inputUrl`, `order`, `scrapedAt`

### Run status rows

- A profile that cannot be read gets its own error row with `_status: "error"`, `_reason` (`blocked`, `not_found`, `auth_wall`, `wrong_identity`, `invalid_url`, or `error`), `_message`, `inputUrl`, `profileUrl`, `order` and `scrapedAt`. `wrong_identity` means LinkedIn served a page whose canonical profile slug did not match the requested slug; no data from that page is emitted.
- A partial run adds one `_status: "partial_results"` row with `_reason`, `_failureBreakdown` and `_message` beside the successful rows.
- A run with no readable profile adds one `_status: "no_data"` row with `_reason`, `_message`, `_help` and `scrapedAt`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `profileUrls` | array | – | LinkedIn profile URLs or bare usernames to look up. Required, 1–1000 entries. |
| `enrichCompany` | boolean | `true` | Attach the current employer's public company page. One request per unique company, cached within the run. |
| `maxPosts` | integer | `10` | Maximum recent posts **and** recent articles per profile (0–50). Set `0` to skip both. |
| `pacing` | string | `balanced` | Delay between profiles: `fast` (0.5–1.5s), `balanced` (3–7s), or `cautious` (8–15s). |
| `useUnblocker` | boolean | `true` | Allow the stronger fallback after LinkedIn refuses a request. Profiles that load directly never use it. |
| `proxyConfiguration` | object | – | Optional Apify proxy used before the stronger fallback. Leave empty for direct-first requests. |

Accepted entry formats: `https://www.linkedin.com/in/username`, `linkedin.com/in/username`, `in/username`, or a bare `username`.

### Example: one public profile with company context

```json
{
  "profileUrls": ["https://www.linkedin.com/in/jeffweiner08"],
  "enrichCompany": true,
  "maxPosts": 5,
  "pacing": "balanced"
}
```

### Example: a shortlist without company enrichment

```json
{
  "profileUrls": [
    "https://www.linkedin.com/in/adammgrant",
    "https://www.linkedin.com/in/patrickcollison"
  ],
  "enrichCompany": false,
  "maxPosts": 0
}
```

### Example: mixed valid and invalid entries

```json
{
  "profileUrls": [
    "williamhgates",
    "https://twitter.com/example",
    "not a profile"
  ],
  "enrichCompany": false,
  "useUnblocker": true
}
```

### Example: a large cautious run

```json
{
  "profileUrls": [
    "https://www.linkedin.com/in/jeffweiner08",
    "https://www.linkedin.com/in/melindagates",
    "https://www.linkedin.com/in/garyvaynerchuk"
  ],
  "enrichCompany": true,
  "maxPosts": 3,
  "pacing": "cautious",
  "useUnblocker": true
}
```

## Use cases

- **Recruiting and candidate sourcing** — collect titles, employers, education, skills and languages for a shortlist of public profiles
- **Sales and lead enrichment** — attach current-company size, industry, headquarters and followers to a contact list
- **Credential and claim verification** — check certifications, credential IDs, honors and published work on a profile
- **Research datasets** — build a structured sample of career histories, skills and public activity across many profiles
- **Founder and executive mapping** — identify current roles, affiliated companies and similar pages around a target company
- **Content and GTM research** — review recent public posts and articles alongside a decision-maker's role and company

## Limitations

- LinkedIn does not show every section to logged-out visitors. Skills, languages, publications, recommendations, certifications, honors, courses, projects, volunteer work and websites appear only when the profile exposes them; absent sections are listed in `missingFields`.
- `connectionsCount` is a coarse public band (for example `500+`), not an exact count.
- Email addresses and phone numbers are not available on the logged-out profile view. This actor never fabricates or guesses them.
- Experience titles, dates and descriptions can be masked or withheld for some profiles and some networks. A masked page is returned with `pageVariant: "masked"` and the masked values are omitted.
- Ordinary (non-public-figure) profiles are often refused by LinkedIn after a small number of guest views. The actor retries and can use a stronger fallback, but some profiles remain unreadable on a given run; they appear as `blocked` error rows.
- Company pages usually include followers, offices, affiliated pages and similar pages, but `founded` and `tagline` are only present for some companies.
- Recent posts and articles reflect what the public page renders, which may be a subset of the member's activity.

## FAQ

**Is a LinkedIn login or cookie required?**
No. Every page is read the way a logged-out visitor sees it. No credentials, session cookies, or member account are used.

**What do `missingFields` and `dataQuality` mean?**
`missingFields` lists the high-value fields the public page did not expose for that profile. `dataQuality` is `full` when the core identity, experience, education and recent-articles fields are present, `partial` when some of them are absent (for example a profile with posts but zero genuine articles), and `masked` when LinkedIn returned a redacted/limited view. `partialFields` flags values that were present but incomplete (such as a truncated summary on a masked page).

**Why is `connectionsCount` a string like `500+`?**
LinkedIn shows logged-out visitors a coarse connection band rather than an exact number. The band is returned as-is instead of inventing a precise count.

**Can this return an email address or phone number?**
No. Those details are not on the public profile page. The actor does not guess, infer, or fabricate contact data.

**Why did one profile return an error row instead of a profile row?**
The row's `_reason` tells you what happened. `not_found` means LinkedIn confirmed the URL does not exist. `blocked` means every attempt was refused on that run and the profile may succeed later. `wrong_identity` means every page LinkedIn served resolved to a different canonical profile slug than the one requested, so the actor refused to emit it. `invalid_url` means the entry was not a LinkedIn profile URL or username. `auth_wall` means the page showed no profile data to guests.

**Does `enrichCompany` cover past employers?**
No. It enriches the current employer only. Each unique company page is fetched once per run and reused for profiles that share that employer.

**Why are some experience or education fields missing on an otherwise complete profile?**
LinkedIn can withhold titles, dates, or descriptions for a specific profile and viewer combination. Masked values are dropped rather than returned as asterisks, and the row is marked `masked` or `partial`.

**Do I need to configure a proxy?**
No. The actor starts with a direct request and only tries a stronger connection after a real refusal. The optional `proxyConfiguration` adds a middle step if you already have a proxy preference.

**Does input order matter?**
Each row carries `order`, matching its position in `profileUrls`, so results can be lined up with the original input even when requests finish out of order.

**Is this affiliated with LinkedIn?**
No. This is an independent, third-party actor that reads publicly available LinkedIn pages. It is not operated by or affiliated with LinkedIn.
