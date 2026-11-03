# Bar Standards Board Barrister Register Scraper

Scrape the **Bar Standards Board's** official public register for England & Wales — search the Barristers' Register by name or chambers, filter by practising status / area of practice / Public Access, browse past disciplinary findings, check barristers currently under interim suspension, look up BSB-regulated entities (chambers / legal-services businesses), or enrich specific barrister/finding URLs directly. Data comes straight from [barstandardsboard.org.uk](https://www.barstandardsboard.org.uk), the statutory regulator of barristers in England and Wales. No auth, no proxy, no cookies required.

## What this actor does

- **Five modes:**
  - `search` — search the live Barristers' Register by name or chambers/organisation
  - `disciplinaryFindings` — browse the public register of past disciplinary findings
  - `interimSuspensions` — list barristers currently subject to interim suspension or interim conditions
  - `entities` — BSB-regulated legal-services businesses ("entities"): authorised bodies, licensed bodies (ABS), and previously-authorised bodies
  - `byUrl` — fetch specific barrister-register or disciplinary-finding URLs directly
- **Rich filters** on `search`: practising status, area of practice (27 categories), Public Access registration, authorisation to conduct litigation, and register view (practising vs. sanctioned/disbarred)
- **Rich filters** on `disciplinaryFindings`: finding status, disciplinary action/sanction type, hearing type, and a decision-date window (past month / past year / custom range)
- **Full profile enrichment** — optionally fetches each barrister's/finding's detail page for chambers address, call date, Inn of Court, rights of audience, areas of practice, disciplinary history, breach/offence details, and more
- **Empty fields are always omitted** — every field on every record is real, extracted data (no `null`/`N/A` placeholders)

## Output fields

### Barrister records (`recordType: "barrister"`)

`barristerName`, `barristerUrl` / `sourceUrl`, `practisingStatusBadge`, `primaryPracticeAddress`, and `barristerId` come straight from the register's listing page. Every other field below is only added when `fetchFullProfile` is on (the default) — turning it off gives you just those five fields plus `registerView`, `recordType` and `scrapedAt`.

| Field | Description |
|---|---|
| `barristerName` | Full name as shown on the register |
| `barristerId` | Bar Standards Board's internal register ID |
| `barristerUrl` / `sourceUrl` | Canonical register URL for this barrister |
| `practisingStatusBadge` | Register badge, e.g. `Practising`, `Disbarred` |
| `currentPractisingStatus` | `Employed`, `Self Employed`, `Dual Capacity`, `Disbarred`, etc. — requires `fetchFullProfile` |
| `dateOfCall` | Month/year called to the Bar — requires `fetchFullProfile` |
| `innOfCourt` | Inn of Court membership — requires `fetchFullProfile` |
| `practisingCertificateValid` | Practising certificate validity period — requires `fetchFullProfile` |
| `primaryPracticeAddress` | Chambers / employer address |
| `primaryPracticeSwitchboardNumber` | Chambers switchboard phone number — requires `fetchFullProfile` |
| `rightsOfAudience` | List of rights of audience granted — requires `fetchFullProfile` |
| `publicAccessRegistered` | Whether registered for the Public Access scheme (bool) — requires `fetchFullProfile` |
| `authorisedToConductLitigation` | Whether authorised to conduct litigation (bool) — requires `fetchFullProfile` |
| `areasOfPractice` | List of declared practice areas — requires `fetchFullProfile` |
| `otherEntitlements` | Other regulatory entitlements (e.g. Immigration Work, Probate) — requires `fetchFullProfile` |
| `youthCourtsRegistered` | Whether registered to work in Youth Courts (bool) — requires `fetchFullProfile` |
| `disciplinaryFindings` | List of `{findingDate, hearingType, findingUrl, findingId}` if any exist — requires `fetchFullProfile` |
| `registerView` | `practising` or `sanctionedNonPractising` |
| `recordType`, `scrapedAt` | Always present |

### Disciplinary finding records (`recordType: "disciplinaryFinding"`)

`barristerName`, `findingUrl` / `findingId` / `sourceUrl`, `sanction`, `hearingType`, and `findingDate` come straight from the findings listing page. `barristerRegisterUrl` / `barristerId`, `currentPractisingStatus`, `dateOfCall`, `innOfCourt`, `breachDetails`, and `offenceDetails` are only added when `fetchFullProfile` is on (the default).

| Field | Description |
|---|---|
| `barristerName` | Name of the barrister subject to the finding |
| `barristerRegisterUrl` / `barristerId` | Link back to the barrister's register entry — requires `fetchFullProfile` |
| `findingUrl` / `findingId` / `sourceUrl` | Canonical finding URL and ID |
| `sanction` | Sanction imposed |
| `hearingType` | Tribunal/hearing type |
| `findingDate` | Date of the finding |
| `currentPractisingStatus`, `dateOfCall`, `innOfCourt` | Barrister's status at time of finding — requires `fetchFullProfile` |
| `breachDetails` | Rules/Code of Conduct provisions breached — requires `fetchFullProfile` |
| `offenceDetails` | Narrative description of the misconduct — requires `fetchFullProfile` |

### Interim suspension records (`recordType: "interimSuspension"`)

| Field | Description |
|---|---|
| `barristerName` | Name of the suspended barrister |
| `details` | Full text describing the suspension/conditions |
| `sourceUrl` | Link to the listing (with anchor) |

### Entity records (`recordType: "entity"`)

| Field | Description |
|---|---|
| `entityName` | Name of the BSB-regulated entity |
| `tradingNameOf` | Underlying company name, if the entity trades under a different name |
| `entityStatus` | `authorised` / `licensed` / `previouslyAuthorised` |
| `entityType` | Legal structure, e.g. `Limited Liability Partnership`, `Private Limited Company` |
| `authorisationValidFrom` | Date authorisation/licence took effect (`YYYY-MM-DD`) |
| `renewalDate` | Next renewal date (authorised/licensed entities only) |
| `authorisationValidTo` | Date authorisation ended (previously-authorised entities only) |
| `practisingAddress` / `practisingAddressSecondary` | Registered practising address(es) |
| `telephone` | Contact telephone number, where published |
| `managers` | List of named managers/partners |
| `headOfLegalPractice` | Head of Legal Practice (HOLP) |
| `headOfFinanceAndAdministration` | Head of Finance and Administration (HOFA) |
| `administrationOfOaths` | Whether authorised to administer oaths (bool) |
| `authorisedToConductLitigation` | Whether authorised to conduct litigation (bool) |
| `sourceUrl` | The BSB entities-register download URL this record was extracted from |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `search` | `search` / `disciplinaryFindings` / `interimSuspensions` / `entities` / `byUrl` |
| `searchQuery` | string | – | Name/chambers (mode=search, required) or optional name filter (mode=disciplinaryFindings, entities) |
| `searchField` | select | `name` | `name` or `organisation` (mode=search) |
| `registerView` | select | `practising` | `practising` or `sanctionedNonPractising` (mode=search) |
| `practisingStatus` | multi-select | – | Filter by `Dual Capacity` / `Employed` / `Self Employed` (mode=search) |
| `areasOfPractice` | multi-select | – | Filter by one or more of 27 practice areas (mode=search) |
| `publicAccessRegistered` | select | `any` | `any` / `yes` / `no` (mode=search) |
| `authorisedToConductLitigation` | select | `any` | `any` / `yes` / `no` (mode=search) |
| `sortOrder` | select | `recent` | `recent` or `relevance` (mode=disciplinaryFindings) |
| `findingStatus` | multi-select | – | Filter by `Final` / `Open to Appeal` / `Appeal Pending` (mode=disciplinaryFindings) |
| `disciplinaryActionType` | multi-select | – | Filter by `Disbarment` / `Fine` / `Other` / `Suspension` (mode=disciplinaryFindings) |
| `findingType` | multi-select | – | Filter by hearing type, e.g. Disciplinary Tribunal (3/5 person) (mode=disciplinaryFindings) |
| `findingDateRange` | select | any | `pastMonth` / `pastYear` / `custom` (mode=disciplinaryFindings) |
| `findingDateFrom` / `findingDateTo` | string | – | Custom decision-date range boundaries, format `YYYY-MM-DD` (findingDateRange=custom) |
| `entityStatus` | multi-select | – | Filter by `authorised` / `licensed` / `previouslyAuthorised` (mode=entities) |
| `startUrls` | array | – | Barrister/finding URLs to fetch directly (mode=byUrl) |
| `fetchFullProfile` | boolean | `true` | Fetch each record's detail page for extra fields |
| `maxItems` | integer | `30` | Hard cap on emitted records (1–1000) |

### Example: search practising barristers by chambers, filtered

```json
{
  "mode": "search",
  "searchQuery": "no5",
  "searchField": "organisation",
  "areasOfPractice": ["crime", "employment"],
  "authorisedToConductLitigation": "yes",
  "maxItems": 50
}
```

### Example: browse recent disciplinary findings

```json
{
  "mode": "disciplinaryFindings",
  "sortOrder": "recent",
  "maxItems": 50
}
```

### Example: disciplinary findings, disbarment or suspension in the past year

```json
{
  "mode": "disciplinaryFindings",
  "disciplinaryActionType": ["disbarment", "suspension"],
  "findingDateRange": "pastYear",
  "maxItems": 50
}
```

### Example: disciplinary findings in a custom date range

```json
{
  "mode": "disciplinaryFindings",
  "findingDateRange": "custom",
  "findingDateFrom": "2020-01-01",
  "findingDateTo": "2020-12-31",
  "maxItems": 50
}
```

### Example: check barristers currently under interim suspension

```json
{
  "mode": "interimSuspensions",
  "maxItems": 50
}
```

### Example: currently-authorised BSB entities matching a name

```json
{
  "mode": "entities",
  "searchQuery": "law",
  "entityStatus": ["authorised", "licensed"],
  "maxItems": 100
}
```

### Example: fetch specific barrister URLs

```json
{
  "mode": "byUrl",
  "startUrls": [
    "https://www.barstandardsboard.org.uk/barristers-register/7C5DCA7B263721A6CB12F687568766BD.html"
  ]
}
```

## Use cases

- **Due diligence** — verify a barrister's practising status, Inn of Court, and disciplinary history before instructing them
- **Legal directories & comparison sites** — bulk-import chambers, practice areas, and contact details
- **Compliance monitoring** — track new disciplinary findings or interim suspensions as they're published
- **Recruitment & chambers research** — find barristers by practice area, chambers, or public-access availability
- **Journalism & legal research** — cross-reference disciplinary sanctions with case reporting

## Limitations

- The BSB also publishes a "Disqualified persons" page (people barred from working for any BSB-regulated entity). It is not a structured/searchable register — it is a single static sentence ("There are currently no persons disqualified") that is empty at the time of writing — so it is not exposed as a mode here. If the BSB later populates it with a real list, it can be added as a future mode.

## FAQ

**Is this official data?** Yes — everything comes directly from the Bar Standards Board's own public register at barstandardsboard.org.uk, the statutory regulator for barristers in England and Wales.

**What's the difference between `practising` and `sanctionedNonPractising` register views?** `practising` covers currently authorised practising barristers (Employed / Self Employed / Dual Capacity). `sanctionedNonPractising` covers barristers who have been disbarred or otherwise sanctioned and are no longer authorised to practise.

**Why do some barrister records have fewer fields than others?** The register itself only publishes certain fields for certain statuses — e.g. a disbarred barrister has no current chambers address, so that field is simply omitted rather than shown as empty.

**Does `searchQuery` support partial matches?** Yes — the register performs a substring/fuzzy match against barrister names or chambers/organisation names, same as the site's own search box.

**How far back do disciplinary findings go?** Per the Bar Standards Board's publication policy, historical findings before 2002 are not published, and findings without a suspension/disbarment are removed from the register after two years.

**Can I look up a barrister I already have a URL for?** Yes — use `mode: "byUrl"` with the full barrister-register or disciplinary_finding URL(s).

**Is `fetchFullProfile` worth the extra request?** For `search` and `disciplinaryFindings`, the listing page already includes name, status/sanction, and address/hearing-type. Turning on `fetchFullProfile` (default) fetches each individual detail page for the complete profile — Inn of Court, rights of audience, areas of practice, breach/offence details, etc. Turn it off for a faster, lighter-weight listing-only crawl.
