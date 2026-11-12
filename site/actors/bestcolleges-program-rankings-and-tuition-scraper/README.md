# BestColleges Program Rankings & Tuition Scraper

Scrape **BestColleges** — the US college rankings and school-data site at [bestcolleges.com](https://www.bestcolleges.com). Fetch ranked schools from any program ranking page (computer science, nursing, business, psychology, and 60+ more), pull detailed school profiles, and enumerate program pages from subject hubs. No auth, no proxy.

## What this actor does

- **Three modes:** `byProgram` (ranked schools), `bySchool` (profile), `bySubject` (program enumeration)
- **Ranking data:** rank, superlative ("Best for…"), program links, ranking year
- **School stats:** in/out-of-state tuition (undergrad + grad), admission rate, retention rate, earnings after 6 years, online-enrollment share, accreditation
- **Filters:** rank range, US state codes, ranking school year
- **Empty fields are omitted**

## Output per ranked school (mode=byProgram)

- `rank` — position in the ranking
- `schoolId`, `rankingId`
- `schoolName`, `city`, `stateName`, `stateCode`
- `schoolUrl`, `programUrl`, `programName`
- `superlativeTitle` — e.g. "Best for Personalized Portfolio-Building"
- `undergradTuitionInState`, `undergradTuitionOutOfState`, `gradTuitionInState`, `gradTuitionOutOfState`
- `admissionRate`, `retentionRate`, `earningsAfterSixYears`, `totalStudentsEnrolled`
- `percentOnlineEnrollment`, `percentOnlinePrograms`
- `schoolLevel`, `accreditation`, `isPrivate`
- `blurb` — editor's summary
- `rankingName`, `schoolYear`, `rankingType`, `rankingStatus`
- `sourceUrl`
- `recordType`, `scrapedAt`

### Output per school profile (mode=bySchool)

- `schoolId`, `title`, `blurb`, `image`
- `city`, `state`, `stateCode`, `url`
- `inStateTuitionUndergrad`, `outOfStateTuitionUndergrad`, `inStateTuitionGrad`, `outOfStateTuitionGrad`
- `totalEnrollmentUndergrad`, `totalEnrollmentGrad`, `percentAdmittedUndergrad`
- `totalBachelorsPrograms`, `graduationRateTotalCohort`, `studentFacultyRatio`, `fulltimeRetentionRate`
- `percentOnlineEnrollment`
- `isPremium`, `isPrivate`, `notForProfit`, `isHbcu`, `militaryFriendly`
- `religiousAffiliation`, `generalizedReligiousTerm`, `accreditorStatus`, `admissionTestScores`, `openAdmissionPolicy`, `hasHlf`
- `sourceUrl`
- `recordType`, `scrapedAt`

### Output per program page (mode=bySubject)

- `uri`, `title`, `sourceUrl`
- `recordType`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `byProgram` | `byProgram` / `bySchool` / `bySubject` |
| `programUri` | string | `computer-science/bachelors` | Ranking page path (mode=byProgram) |
| `schoolUri` | string | – | School profile path (mode=bySchool) |
| `subjectUri` | string | – | Subject hub path (mode=bySubject) |
| `rankMin` | int | – | Keep ranks ≥ this |
| `rankMax` | int | – | Keep ranks ≤ this (top-N) |
| `stateCodes` | array | – | US state codes, e.g. `["NY","CA"]` |
| `schoolYear` | int | – | Ranking year, e.g. `2026` |
| `maxItems` | int | `50` | Hard cap (1–1000) |

### Example: top-20 online CS bachelor's programs

```json
{
  "mode": "byProgram",
  "programUri": "computer-science/bachelors",
  "rankMax": 20
}
```

### Example: all ranked nursing schools in NY and CA

```json
{
  "mode": "byProgram",
  "programUri": "nursing/bachelors",
  "stateCodes": ["NY", "CA"]
}
```

### Example: school profile

```json
{
  "mode": "bySchool",
  "schoolUri": "university-of-colorado-boulder"
}
```

### Example: enumerate finance programs from a subject hub

```json
{
  "mode": "bySubject",
  "subjectUri": "business/bachelors"
}
```

## Use cases

- **Higher-ed research** — compare program rankings and school stats side by side
- **Counseling / advising** — shortlist schools by cost, admission rate, and outcomes
- **Market analysis** — track tuition and enrollment trends across ranking years
- **Content pipelines** — feed ranking pages into guides and comparison tools
- **Prospective students** — filter ranked schools by state and affordability

## FAQ

**What is BestColleges?** An independent publisher of US college rankings, program guides, and school profiles (bestcolleges.com).

**Do I need an account or API key?** No. All modes read public page data.

**Where does the data come from?** Each ranking page embeds its full ranking JSON (schools, ranks, stats) directly in the page; school profiles embed their stats the same way. The actor reads those embedded payloads.

**How do I find ranking page paths?** Browse bestcolleges.com — e.g. `/computer-science/bachelors/`, `/nursing/masters/`, `/business/bachelors/finance/`. Use `bySubject` on a hub like `/business/bachelors/` to enumerate the program pages in that section.

**Why are some tuition fields missing?** Schools that don't report a figure simply omit it; empty fields are always dropped.

**What does `superlativeTitle` mean?** BestColleges' editors tag each ranked school with a reason it was chosen, e.g. "Best for Working Adults".

**How fresh is the data?** BestColleges publishes annual rankings; each page carries its ranking year (`schoolYear`) so you can filter by edition.

**Is this affiliated with BestColleges?** No, this is a third-party actor using the public website.

## Limitations

- Only pages that carry embedded rankings work with `byProgram` (program ranking pages). State resource pages and blog articles contain no ranking data.
- `bySubject` enumerates links from the hub page's HTML; deep program pages under other sections may need their own hub paths.
- The internal school-search API (`api.mobius.highereducation.com`) requires a session token from the site and is not used; school discovery happens through ranking pages and subject hubs instead.
- `bySchool` currently returns 0 records for most school slugs: bestcolleges.com's `/schools/{slug}/` pages are served as a client-side-rendered shell (a site-side server error — the HTTP 200 page carries no profile data). The actor reports a status message in that case. School data remains fully available through `byProgram` (which carries tuition, admission rate, earnings, and accreditation per school).
- Some program hubs (e.g. `business/bachelors`) intermittently serve the same empty shell from datacenter IPs; the actor retries those fetches automatically, and pages that stay broken produce a clean 0 with a status message.
