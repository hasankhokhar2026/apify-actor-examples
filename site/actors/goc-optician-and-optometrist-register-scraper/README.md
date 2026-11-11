# GOC Optician & Optometrist Register Scraper

Search and export the General Optical Council's (GOC) public **Specialist Register** at [str.optical.org](https://str.optical.org) — the statutory register of every optometrist, dispensing optician, student optometrist/student dispensing optician, and registered optical business permitted to practise in the UK. No login, API key, cookie, or proxy is required. The actor selects its own network route automatically; you do not configure a proxy.

## What this actor does

- **Search individual registrants** by surname, first name, register type, specialty, address/town, postcode radius, or exact GOC number.
- **Search optical businesses** by company name, GOC number, or postcode radius.
- **Check a list of exact GOC numbers** — registrants and businesses can be mixed in one list; the actor detects the prefix, batches the lookups, and reports numbers that were not found.
- **Export the full registered-business list** (~3,000 businesses) in one run.
- **Enrich with profile data** — qualifications, town, every published practice address, practice postcodes, and FTP decision PDF links.
- **Use multiple surnames, addresses, or company names** in one run; each value is searched separately and results are de-duplicated by GOC number.
- **Omit empty fields** — every emitted field carries real, non-null data.

## Modes

| Mode | Use it for |
|---|---|
| `registrant` | Individuals: name, register type, specialty, address, postcode radius, GOC number |
| `bodyCorporate` | Registered optical businesses: company name, GOC number, postcode radius |
| `byGocNumber` | Bulk verification of exact GOC numbers; registrants and businesses mixed |
| `allBusinesses` | Full registered-business export (~3,000 rows) |

`registrant` and `bodyCorporate` need at least one search filter. `byGocNumber` needs `gocNumbers`. `allBusinesses` needs no filter.

## Output fields

### Registrant records (`recordType: "registrant"`)

| Field | Description |
|---|---|
| `gocNumber` | Official GOC registration number, e.g. `01-12294`, `D-9396` |
| `name` | Full registered name |
| `registerType` | `Optometrist`, `Dispensing Optician`, `Student Optometrist`, etc. |
| `registrationStatus` | `Registered`, `Registered with Conditions`, `Suspended` |
| `registrationDate` | Date of most recent registration, ISO `yyyy-mm-dd` |
| `specialities` | Raw specialty text, e.g. `Contact Lens Specialty` |
| `specialityList` | Normalised specialty values, e.g. `["Contact lens"]` |
| `specialityCount` | Number of specialty annotations |
| `qualifications` | Professional qualifications, when published (detail page) |
| `town` | Registered town (detail page) |
| `practiceAddresses` | First published practice address (detail page) |
| `otherPracticeAddresses` | Additional practice addresses (detail page) |
| `practiceAddressCount` | Total published practice addresses |
| `practicePostcodes` | UK postcodes extracted from all practice addresses |
| `primaryPracticePostcode` | First practice postcode |
| `ftpDecisions` | FTP decision title(s), separated by `; ` |
| `ftpDecisionDocuments` | `{title, url}` for each published FTP decision PDF |
| `ftpDecisionCount` | Number of published FTP decisions |
| `hasFtpDecision` | `true` when an FTP decision is published |
| `hasConditions` | `true` when the status contains `Conditions` |
| `isSuspended` | `true` when the status contains `Suspended` |
| `isStudent` | `true` for student register types |
| `searchTerm` | The surname/address that found the record, when the run used more than one search term |
| `sourceUrl` | Canonical GOC register profile URL |
| `recordType` | `"registrant"` |
| `scrapedAt` | UTC ISO timestamp |

### Body corporate records (`recordType: "bodyCorporate"`)

The same common fields where applicable, with `companyName` instead of `name`. `registerType`, `specialities`, and `qualifications` are omitted because the GOC does not publish them for businesses.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `registrant` | `registrant`, `bodyCorporate`, `byGocNumber`, or `allBusinesses` |
| `surnames` | array | `[]` | One or more surnames (registrant mode) |
| `forename` | string | – | First-name contains filter (registrant mode) |
| `soundsLikeSurname` | bool | `false` | Phonetic surname matching |
| `registerType` | select | – | Registration category |
| `speciality` | select | – | Specialty annotation |
| `addresses` | array | `[]` | Address/town text searches (registrant mode) |
| `companyNames` | array | `[]` | Company-name searches (business mode) |
| `gocNumbers` | array | `[]` | Exact GOC numbers; mixed registrant/business in `byGocNumber` |
| `postcode` | string | – | UK postcode or outward code for a distance search |
| `radiusMiles` | int | `50` | Radius in miles (1–100) |
| `sortBy` | select | – | Surname A-Z or Z-A (registrant searches) |
| `fetchDetails` | bool | `true` | Fetch profile details; off is much faster. Ignored in `allBusinesses`, which is always list-only |
| `maxDetailedItems` | int | `2000` | Cap on records with detail enrichment |
| `maxItems` | int | `50` | Hard cap on emitted records (1–25,000) |

Legacy tasks that send `surname`, `companyName`, or `address` still work: those keys are mapped in code to the new arrays.

### Examples

Find optometrists named Smith or Jones, with full details:

```json
{
  "mode": "registrant",
  "surnames": ["Smith", "Jones"],
  "registerType": "Optometrist",
  "fetchDetails": true,
  "maxDetailedItems": 100
}
```

Check a mixed list of GOC numbers:

```json
{
  "mode": "byGocNumber",
  "gocNumbers": ["01-12294", "D-9396", "CO-4310"],
  "fetchDetails": false,
  "maxItems": 10
}
```

Find contact-lens dispensing opticians near Edinburgh:

```json
{
  "mode": "registrant",
  "speciality": "Contact lens",
  "postcode": "EH1",
  "radiusMiles": 25,
  "fetchDetails": true
}
```

Export every registered optical business:

```json
{
  "mode": "allBusinesses",
  "fetchDetails": false,
  "maxItems": 3000
}
```

## How it works

The actor sends the same JSON search request as the public register (`POST /registrant/list`) and parses the returned HTML fragment. Detail enrichment fetches `GET /Registrant/{guid}`. FTP decision links point at public PDFs on `mygoc.azurewebsites.net`.

The register returns 5 results per page. Large runs are bounded by `maxItems` and the platform timeout. The actor streams records, retries transient list errors, caps detail fetches, and falls back to list-only records when the detail pages keep failing.

## Limits and accuracy

- **The GOC register is live.** Counts and records change between runs.
- **Detail pages are flaky.** The GOC's own detail pages intermittently return HTTP 500 or take tens of seconds. The actor uses short timeouts, a circuit breaker, and list-only fallback, so a run can still complete with list-level fields for the records whose detail page failed.
- **A full registrant export does not fit one default run.** The register returned 33,359 registrants on 2026-11-05 at a fixed 5 records per page: 6,672 page requests. At the measured cloud rate of about 1.36 s/page that is roughly 151 minutes, far above the default 3,600 s timeout. Even one register type (`Optometrist`, 19,501) is 3,901 pages, about 88 minutes. Raising `maxItems` does not remove the page ceiling, and the actor does not ship a chunk/resume cursor; use narrow filters or accept a partial export. The full business register is about 2,973 rows (595 pages, roughly 13.5 minutes) and `allBusinesses` is deliberately list-only.
- **No contact details are published.** The GOC register does not expose email, phone, website, gender, languages, home visits, registration expiry, first-registration date, or conditions text. Those fields are not emitted.
- **No status filter exists upstream.** The actor returns the raw `registrationStatus` and the derived `hasConditions`/`isSuspended` flags.
- **Non-Latin search text is rejected.** The GOC search silently ignores CJK/emoji/non-Latin text and would return the whole register; the actor refuses those values before sending a request.
- **Body corporate sorting is ignored upstream.** `sortBy` affects registrant searches only.
- **Historical/erased registrants are not in the public search.** They cannot be retrieved from this source.

## FAQ

**Do I need cookies or an API key?** No. The register is public and the actor uses the same public endpoint as the website.

**Why are some fields missing?** Qualifications, town, practice addresses, and FTP decisions are published conditionally. `fetchDetails` must be on for those fields, except in `allBusinesses`, which is list-only. Detail pages can also fail; the actor then emits list-level fields for the affected records. Empty values are omitted, never emitted as `null` or `"None"`.

**What does `ftpDecisions` mean?** Fitness to Practise — a published regulatory decision against the registrant or business. Most records have none.

**Can I combine filters?** Yes. Surnames, address text, register type, specialty, and postcode are combined with AND on the register. Multiple surnames or addresses run separate searches and are merged.

**Why did my GOC number not appear?** `byGocNumber` reports missing numbers in the run status. A number that is not on the current register, or is formatted in a way the actor cannot normalise, will not return a record.

**Why does a `sourceUrl` sometimes show a server error?** It points at the live GOC page, which is intermittently unavailable. Reload it; the scraped data is unaffected.

## Data source

General Optical Council public Specialist Register: https://str.optical.org. This actor is independent and not affiliated with the GOC.
