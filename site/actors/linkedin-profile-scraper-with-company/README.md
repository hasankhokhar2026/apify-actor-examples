# LinkedIn Profile Scraper with Company & Credential Data

Give this actor a list of public LinkedIn profile URLs or plain usernames and get back one structured record per person. It reads only what LinkedIn serves to a logged-out visitor: identity and About text, current employer and school links, work and education history, recent posts and articles, self-authored sections such as certifications, recommendations, languages, publications, patents, courses, honors, volunteering, projects, skills and badges, plus optional firmographics from the current employer's own public company page.

No LinkedIn account, cookie, API key, or proxy setup is required.

## What this actor does

- Accepts profile URLs (`https://www.linkedin.com/in/name`), `linkedin.com/in/name`, `in/name`, regional subdomains, URLs with tracking parameters, or a bare username.
- Normalizes and deduplicates the input list, then reads each profile through the cheapest working public access path.
- Extracts the full public section surface, not just the top card.
- Optionally reads the current employer's public company page for headcount, size band, industry, headquarters, address, website, logo, description, tagline, type, specialties, followers, offices, affiliated/similar pages and recent updates.
- Omits any field it could not confirm from the public page. It never pushes `null`, blank, masked, or placeholder values.

## Output per profile

| Field | Description |
|---|---|
| `name` | Full name on the profile |
| `headline` | Real public headline, when LinkedIn exposes one for a logged-out visitor |
| `headlineRedacted` | `true` when LinkedIn replaced the headline with the current company instead of showing it |
| `location` | Profile location |
| `summary` | About/bio text |
| `profileUrl` | Canonical profile URL |
| `profilePicture` | Profile photo URL |
| `profileUrn` / `profileId` | Stable member identifier (`urn:li:member:<id>` and its numeric part) |
| `publicIdentifier` | Public profile slug |
| `currentTitle` | Current job title, only when LinkedIn exposes it publicly |
| `currentCompany` | Current employer: `name`, `url`, `slug`, `companyId`, plus the enriched company fields below |
| `currentSchool` | School shown on the top card: `name`, `url` |
| `allTitles` | Job titles LinkedIn publishes in the profile's structured data |
| `currentPositions` / `pastPositions` | Work entries: `company`, `companyUrl`, `title`, `startDate`, `endDate`, `dateRange`, `duration`, `employmentType`, `location`, `description` (only the fields the public page actually renders) |
| `experiences` | `currentPositions` and `pastPositions` combined into one list |
| `education` / `educations` | School entries: `school`, `schoolUrl`, `degree`, `fieldOfStudy`, `gpa`, `startDate`, `endDate`, `dateRange` (the same list under both keys) |
| `followersCount` | Follower count |
| `connectionsCount` | Exact connection count when LinkedIn publishes one |
| `connectionsText` | Public connections band (for example `"500+"`) when only the capped form is shown |
| `recentPosts` | Recent public posts and reposts by the profile owner: `text`, `url`, `postedAgo`, `reactions`, `comments`, `author`, `authorUrl`, and `isRepost`/`repostedBy` when applicable |
| `recentArticles` | Recent LinkedIn Pulse articles: `title`, `url`, `publishedDate`, `text`, `likes` |
| `certifications` | Licenses and certifications: `name`, `issuer`, `issuerUrl`, `issueDate`, `credentialId`, `credentialUrl` |
| `recommendations` | Recommendations received: `recommender`, `recommenderUrl`, `text` |
| `languages` | Languages: `name`, `proficiency` |
| `services` | Services offered: `name`, `url` |
| `publications` | Publications: `title`, `url`, `publisher`, `date`, `description` |
| `patents` | Patents: `title`, `url`, `filedDate`, `number`, `description` |
| `courses` | Courses: `title`, `number` |
| `instructorCourses` | LinkedIn Learning courses authored: `title`, `url`, `duration` |
| `honorsAndAwards` | Honors and awards: `title`, `issuer`, `date`, `description` |
| `organizations` | Organization memberships: `name`, `position`, `description` |
| `volunteerExperience` | Volunteer roles: `role`, `organization`, `description` |
| `projects` | Projects: `title`, `dateRange`, `description` |
| `testScores` | Test scores: `name`, `score`, `date` |
| `skills` | Public skill names, when the profile exposes them |
| `badges` / `isTopVoice` / `isCreator` | Public profile badges |
| `websites` | Personal website and portfolio links: `label`, `url` |
| `inputUrl` | The exact URL or handle you supplied for this row |
| `order` | Zero-based position in the deduplicated input list |
| `scrapedAt` | ISO-8601 UTC timestamp |

Enriched `currentCompany` fields: `employeeCount`, `size`, `industry`, `headquarters`, `address`, `website`, `logoUrl`, `description`, `tagline`, `organizationType`, `specialties`, `followersCount`, `foundedYear`, `locations`, `affiliatedPages`, `similarPages`, `updates`.

Empty or unavailable fields are omitted. Fields that cannot be confirmed for a profile are left out of that record rather than returned as empty placeholders. A profile that cannot be read at all produces no row; the run status message explains why (not found, privacy-restricted, blocked, invalid URL, or identity mismatch).

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `profileUrls` | array of strings | – | Required. LinkedIn profile URLs or bare usernames, one per profile to scrape (up to 1,000) |
| `enrichCompany` | boolean | `true` | Read the current employer's public company page for firmographics. One request per unique company per run |
| `maxPosts` | integer (0-50) | `10` | Maximum recent posts per profile. Set `0` to skip posts. No extra request |

### Example: one profile

```json
{
  "profileUrls": ["https://www.linkedin.com/in/williamhgates"]
}
```

### Example: a short batch without company enrichment

```json
{
  "profileUrls": ["satyanadella", "in/reidhoffman", "https://www.linkedin.com/in/jeffweiner08"],
  "enrichCompany": false,
  "maxPosts": 5
}
```

### Example: profile plus company firmographics

```json
{
  "profileUrls": ["https://www.linkedin.com/in/satyanadella"],
  "enrichCompany": true
}
```

## Use cases

- **Sales prospecting** - turn known profile URLs into structured records with current employer context.
- **Recruiting and talent sourcing** - compare schools, employers, certifications, languages and public work links across a shortlist.
- **CRM enrichment** - append public job, company and education fields to existing contacts.
- **Account research** - pull current-employer size, industry, headquarters and website for key people.
- **Academic and market research** - study career paths, credentials, publications, patents and project history.
- **Due diligence** - cross-reference public certifications, honors, volunteer history and company affiliations.

## FAQ

**Do I need a LinkedIn login, cookies, or a proxy?**
No. The actor reads the public page LinkedIn serves to logged-out visitors and link-preview crawlers. It selects its own access path and needs no account, cookie, token, or proxy configuration.

**Why is `headline` missing from most records?**
LinkedIn withholds the real headline from anonymous visitors for most ordinary profiles and shows the current company or location instead. The actor omits that substitution; when it detects a company substitution it sets `headlineRedacted: true`. Profiles that LinkedIn leaves fully public still get a real headline.

**Why are experience titles, experience dates, or degree/field missing?**
Those details are login-gated for most profiles. The public page exposes employer names, company links, locations, school names, school dates and sometimes GPA, so those are shipped. The actor never guesses the rest.

**Why is `connectionsCount` sometimes a band like `500+`?**
LinkedIn caps the public connection count for most profiles. The exact number is shipped when present; the band is shipped as `connectionsText`.

**Can this return email addresses or phone numbers?**
No. LinkedIn does not show contact details on the public profile page, and the actor does not use third-party enrichment or fabricate them.

**Are posts complete?**
No. `recentPosts` covers the recent activity block LinkedIn renders on the public profile, not the member's full post history.

**Does `enrichCompany` work for every profile?**
It applies only to the current employer, and only when that employer has a public LinkedIn company page. Past employers are not enriched.

**What happens to old saved inputs?**
Legacy keys such as `profileUrl`, `profiles`, `maxSkills`, `language`, `maxArticles`, `cookie`, `proxyConfiguration`, `maxConcurrency`, `includeContactInfo`, `includeRecommendations` and `includeActivity` are still accepted. The meaningful ones are mapped in code; tuning and credential-shaped keys are ignored with a log message. They are not visible fields in the current input schema.

**What does a partial run look like?**
The dataset contains the records that were read. The run status message lists how many profiles were returned and why the rest were skipped. No diagnostic or sentinel row is added to the dataset.

**Is this affiliated with LinkedIn?**
No. This is an independent tool that reads public LinkedIn pages and is not affiliated with, endorsed by, or connected to LinkedIn Corporation.

## Data source and limitations

The actor uses LinkedIn's public guest surface. LinkedIn may temporarily block an IP or return its sign-up page; the actor retries the free paths on a fresh request and uses a server-side anti-bot fallback only when both free paths are blocked. A profile whose owner hides it from logged-out visitors cannot be read, and a vanity URL that LinkedIn has reassigned to another member is detected and skipped rather than returned as the wrong person.

Public data can lag the logged-in view, the recent-activity block is bounded, and sections such as skills, patents or test scores appear only on profiles where the owner filled them in and left them public.

Very large input lists can run close to the platform's run timeout because each profile is a full page read. If a large batch times out, split it into smaller batches; records already emitted stay in the dataset.

LinkedIn profile and company page URLs are canonical, but LinkedIn may answer an automated client with HTTP 999 or 403 and ask for a sign-in. That is LinkedIn's anti-bot behavior, not a broken URL; the URLs open normally in a browser. Profile photos and company logos are served from LinkedIn's public CDN and load without a login.
