# GOC Optician & Optometrist Register Scraper

Search the General Optical Council's (GOC) public **Specialist Register** at [str.optical.org](https://str.optical.org) — the official, legally-mandated register of every optometrist, dispensing optician, optometry/dispensing student, and registered optical business ("body corporate") permitted to practise in the UK. No login, no API key, no cookies required — the register is public.

## What this actor does

- **Two search modes:** individual registrants (`registrant`) or optical businesses (`bodyCorporate`)
- **Search by name** — surname (with optional phonetic "sounds-like" matching) and first name
- **Search by exact GOC number(s)** — one or many, comma-separated
- **Filter by registration category** — Optometrist, Dispensing Optician, Student (+ dual categories)
- **Filter by specialty** — Contact lens, Independent prescribing, Supplementary prescribing, Additional supply
- **Postcode radius search** — find every registrant/business within N miles of a UK postcode
- **Full-profile enrichment** — optionally visits each result's detail page to also capture qualifications, town, practice address, and fitness-to-practise decisions
- **Empty fields are always omitted** — every emitted field is real, non-null data

## Output fields

### Registrant records (`recordType: "registrant"`)

| Field | Description |
|---|---|
| `gocNumber` | Official GOC registration number, e.g. `01-12294`, `D-9396` |
| `name` | Full registered name |
| `registerType` | `Optometrist`, `Dispensing Optician`, `Student Optometrist`, etc. |
| `registrationStatus` | e.g. `Registered` |
| `registrationDate` | Date of most recent registration, ISO `yyyy-mm-dd` |
| `specialities` | Specialty annotation, when held (e.g. `Contact Lens Specialty`) |
| `qualifications` | Professional qualifications abbreviation (detail page only) |
| `town` | Registered town (detail page only) |
| `practiceAddresses` | Practice address, when published (detail page only) |
| `ftpDecisions` | Fitness-to-practise decision text, when one exists (detail page only) |
| `sourceUrl` | Canonical GOC register profile URL |
| `recordType` | `"registrant"` |
| `scrapedAt` | UTC ISO timestamp |

### Body corporate records (`recordType: "bodyCorporate"`)

| Field | Description |
|---|---|
| `gocNumber` | Official GOC business registration number, e.g. `CO-4310` |
| `companyName` | Registered business name |
| `registrationStatus` | e.g. `Registered` |
| `registrationDate` | ISO `yyyy-mm-dd` |
| `town` | Registered town (detail page only) |
| `practiceAddresses` | Practice address (detail page only) |
| `ftpDecisions` | Fitness-to-practise decision text, when one exists (detail page only) |
| `sourceUrl` | Canonical GOC register profile URL |
| `recordType` | `"bodyCorporate"` |
| `scrapedAt` | UTC ISO timestamp |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `registrant` | `registrant` or `bodyCorporate` |
| `surname` | string | `Smith` | (mode=registrant) Surname contains |
| `soundsLikeSurname` | bool | `false` | (mode=registrant) Match `surname` phonetically |
| `forename` | string | – | (mode=registrant) First name contains |
| `registerType` | select | – | (mode=registrant) Registration category |
| `speciality` | select | – | (mode=registrant) Specialty annotation |
| `address` | string | – | (mode=registrant) Address contains |
| `sortBy` | select | – | (mode=registrant) Sort by surname A-Z / Z-A |
| `companyName` | string | – | (mode=bodyCorporate) Company name contains |
| `gocNumbers` | array | – | Exact GOC number(s); overrides name search |
| `postcode` | string | – | UK postcode for a radius search (both modes) |
| `radiusMiles` | int | `50` | Radius in miles from `postcode` (1–100) |
| `fetchDetails` | bool | `true` | Fetch each profile's detail page for extra fields |
| `maxItems` | int | `50` | Hard cap on returned records (1–2000) |

At least one search criterion (`surname`, `forename`, `registerType`, `speciality`, `address`, `companyName`, `gocNumbers`, or `postcode`) is required per mode — the register does not support an unfiltered "list everyone" query.

### Example: find all Smiths on the register

```json
{
  "mode": "registrant",
  "surname": "Smith",
  "maxItems": 50
}
```

### Example: registered contact lens specialists

```json
{
  "mode": "registrant",
  "speciality": "Contact lens",
  "maxItems": 100
}
```

### Example: optical businesses near a postcode

```json
{
  "mode": "bodyCorporate",
  "postcode": "SW1A 1AA",
  "radiusMiles": 10,
  "maxItems": 50
}
```

### Example: exact GOC number lookup

```json
{
  "mode": "registrant",
  "gocNumbers": ["01-12294", "D-9396"]
}
```

## Use cases

- **Employer / recruiter verification** — confirm an optometrist or dispensing optician holds a current, valid GOC registration before hiring
- **Compliance & due diligence** — check an optical business's registration status before a partnership or supply agreement
- **Market research** — map optical practices and specialists by postcode/region
- **Patient safety** — verify a practitioner's registered specialty (e.g. contact lens fitting, independent prescribing)
- **Directory building** — populate a "find an optician near you" tool with verified GOC data

## FAQ

**What is the GOC Specialist Register?** The UK General Optical Council is the statutory regulator for optometry and dispensing opticians. Its public "Specialist Register" (branded `str.optical.org`) lets anyone verify whether an individual or business is currently permitted to practise/trade.

**Do I need cookies, a login, or an API key?** No. The register is a public search tool; this actor talks to the same public search endpoint the website itself uses.

**Why do some records have fewer fields than others?** `qualifications`, `town`, `practiceAddresses`, and `ftpDecisions` are only published for some registrants/businesses, and only appear when `fetchDetails` is enabled (visits the individual profile page). Fields the register doesn't publish for a given record are omitted rather than emitted as blank/null.

**What does `ftpDecisions` mean?** "Fitness to Practise" — any published regulatory decision against that registrant/business. Most registrants show no decision, so the field is simply absent.

**Can I search by both name and postcode at once?** Yes — all provided filters are combined (AND logic) by the register's own search, e.g. `surname=Smith` + `postcode=SW1A 1AA` finds only Smiths near that postcode.

**What's the difference between `registrant` and `bodyCorporate` mode?** `registrant` searches individual practitioners (optometrists, dispensing opticians, students). `bodyCorporate` searches registered optical businesses/companies — a separate GOC register requirement for any entity providing optical services.

**How current is the data?** The GOC register is the live, authoritative source — the same one used for official verification — so results reflect the register's current state at the time of the run.

**Does it support non-Latin characters in name searches?** UK optician names are virtually always Latin-script, so this is rarely a practical limitation. Note that the GOC's own search backend silently ignores non-Latin/CJK text in `surname`/`forename`/`address`/`companyName` (it returns its default unfiltered result set rather than zero matches) — this is upstream behavior on the register itself, not something this actor can change. Stick to Latin-script queries for predictable results.

**Why does a record's `sourceUrl` occasionally return a server error when I click it?** The GOC's register (str.optical.org) is a known-flaky public government site — its own detail pages intermittently return HTTP 500 (roughly 1 in 5 requests, independent of query), even for a plain browser visit. The actor retries its own detail-page fetches automatically (3 attempts with backoff) so this rarely affects scraped output, but the emitted `sourceUrl` itself points at the live GOC page and inherits that same intermittent flakiness — simply reload the link if it happens.
