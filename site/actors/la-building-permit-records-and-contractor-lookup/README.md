# LA Building Permit Records & Contractor Lookup

Pull Los Angeles building records directly from the Department of Building & Safety's public open data. Every run reads the live Socrata API, so a permit issued last week is in the dataset — not a copy frozen years ago. Search the whole city, follow a single address or contractor, or pull a parcel's permit history. No account, API key, cookie or proxy is required.

## Why this actor

LADBS publishes its permits as a family of datasets, not one file: building, electrical and mechanical permits, each split into issued and submitted applications and into three date eras (pre-2010, 2010–2019, 2020 to today), plus Certificates of Occupancy and an older detailed dataset. This actor hides that split:

- **Live data** — issued building permits through the latest published day (2026-11-14 at the time of the revamp), not the legacy feed that stopped in May 2023.
- **Eight record families** — issued/submitted building, issued/submitted electrical, issued/submitted mechanical, Certificate of Occupancy, and the legacy 2015–2023 detailed dataset.
- **Full history** — the pre-2010 and 2010–2019 datasets are queried automatically when you ask for older dates.
- **Five ways in** — keyword/filter search, exact permit numbers, an address, a contractor business name, or an assessor Book-Page-Parcel.
- **Contractor details where LADBS publishes them** — the live feed has no names, so the actor batch-enriches each permit from the Certificate of Occupancy plus two frozen detailed files (a 2015–2023 building-only file and a 2013–2023 all-trades file), filling contractor, applicant, licence, occupancy, stories and residential-unit fields when a matching row exists.
- **Modern LADBS fields** — use code/description, council district, APN/PIN, community plan area, neighbourhood council, square footage, construction type, height, ADU/junior-ADU/dwelling-unit change, EV and solar flags, issuing business unit, and certificate-of-occupancy dates.
- **Optional inspection summaries** — inspection count and last inspection date/type/result from the LADBS inspections dataset.
- **Empty values are omitted** — no `null`, no placeholders.

## Modes

| Mode | What it does | Required input |
|---|---|---|
| `search` | Filter the selected dataset and return matching permits | none |
| `byPermitNumbers` | Resolve exact PCIS permit numbers, searching every LADBS dataset family | `permitNumbers` |
| `byAddress` | Find permits at a street address (or anywhere on a street) | `streetName` |
| `byContractor` | Pull a contractor's permit history (CoO + legacy detailed datasets, including the 2013–2023 all-trades file, refreshed with live status) | `contractorName` |
| `byAssessorParcel` | Find permits for an LA County assessor Book-Page-Parcel / AIN | `assessorBook`, `assessorPage`, `assessorParcel` |

## Datasets

| `dataset` value | Rows at revamp | What it contains |
|---|---|---|
| `issuedBuilding` (default) | 1.60 M across three eras | Building permits LADBS has issued, 1988 → today |
| `submittedBuilding` | 1.08 M across three eras | Building permit applications, including ones not yet issued |
| `issuedElectrical` | 1.12 M across three eras | Electrical permits issued, 1988 → today |
| `submittedElectrical` | 197 K across three eras | Electrical permit applications |
| `issuedMechanical` | 1.39 M across three eras | Plumbing, HVAC, fire-sprinkler, elevator and pressure-vessel permits issued |
| `submittedMechanical` | 211 K across three eras | Mechanical permit applications |
| `certificateOfOccupancy` | 146 K | Certificates of Occupancy, 2005 → today, with contractor/applicant details |
| `legacyDetailed` | 375 K | The old detailed permit dataset, frozen 2015-11-03 → 2023-05-19 |

The actor also reads `hbkd-qubn` (LADBS-Permits, 1.6 M rows, 2013-01-01 → 2023-05-19, all trades) as an identity-enrichment source and for `byContractor` lookups. It is not a selectable dataset; it fills contractor/applicant fields on older records where the richer CoO/legacy rows are missing.

When `dataset` is left at its default and you choose an electrical or mechanical permit type, the matching trade dataset is selected automatically and reported in the run status. To search applications before issuance, choose one of the `submitted*` datasets explicitly.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search`, `byPermitNumbers`, `byAddress`, `byContractor` or `byAssessorParcel` |
| `dataset` | string | `issuedBuilding` | One of the eight datasets listed above |
| `permitNumbers` | array | – | Exact PCIS permit numbers; hyphens or spaces both work |
| `streetNumber` | string | – | Street number for `byAddress`; optional |
| `streetName` | string | – | Street name; exact street match in `byAddress`, substring filter in `search` |
| `streetDirection` | string | Any | `N`, `S`, `E` or `W` |
| `streetSuffix` | string | Any | `AVE`, `ST`, `BLVD`, `DR`, `PL`, `RD`, `WAY`, … |
| `assessorBook` | string | – | Assessor book component (4 digits) |
| `assessorPage` | string | – | Assessor page component (3 digits) |
| `assessorParcel` | string | – | Assessor parcel component (3 digits) |
| `contractorName` | string | – | Exact business name in `byContractor` (CoO + legacy detailed datasets, including the 2013–2023 all-trades file); substring filter in `search` (CoO + 2015–2023 legacy detailed) |
| `workDescriptionKeyword` | string | – | Substring match on the work description |
| `useDescriptionKeyword` | string | – | Substring match on the use description (`Accessory Dwelling Unit`, `Office`, `Retail`, …) |
| `permitType` | string | Any | `Bldg-New`, `Bldg-Addition`, `Bldg-Alter/Repair`, `Bldg-Demolition`, `Bldg-Relocation`, `Nonbldg-*`, `Grading`, `Swimming-Pool/Spa`, `Sign`, `Electrical`, `Plumbing`, `HVAC`, `Fire Sprinkler`, `Elevator`, `Pressure Vessel` |
| `permitSubType` | string | Any | `1 or 2 Family Dwelling`, `Apartment`, `Commercial`, `Onsite`, `Offsite`, `Public Safety Only`, `Special Equipment` |
| `permitCategory` | string | Any | `Plan Check` or `No Plan Check` |
| `status` | string | Any | Current status (`Issued`, `Permit Finaled`, `CofO Issued`, `PC Approved`, …) |
| `initiatingOffice` | string | Any | LADBS district office (CoO/legacy only; the actor switches to those) |
| `occupancy` | string | Any | Building-code occupancy group (CoO/legacy only) |
| `constructionType` | string | Any | `Type V-B Construction`, `Type III-A Construction`, … |
| `businessUnit` | string | Any | `Express Permit`, `Plan Check at Counter`, `Regular Plan Check`, … |
| `zipCodes` | array | – | One or more 5-digit ZIP codes |
| `issueDateFrom` | string | – | `YYYY-MM-DD`; earlier permits are dropped |
| `issueDateTo` | string | – | `YYYY-MM-DD`; later permits are dropped |
| `submittedDateFrom` | string | – | `YYYY-MM-DD`; earlier applications are dropped |
| `submittedDateTo` | string | – | `YYYY-MM-DD`; later applications are dropped |
| `statusDateFrom` | string | – | `YYYY-MM-DD`; earlier status updates are dropped |
| `statusDateTo` | string | – | `YYYY-MM-DD`; later status updates are dropped |
| `minValuation` | number | – | Minimum applicant-declared construction valuation (USD) |
| `maxValuation` | number | – | Maximum applicant-declared construction valuation (USD) |
| `minSquareFootage` | number | – | Minimum published square footage |
| `maxSquareFootage` | number | – | Maximum published square footage |
| `minStories` | integer | – | Minimum stories (CoO/legacy only) |
| `maxStories` | integer | – | Maximum stories (CoO/legacy only) |
| `minResidentialUnits` | integer | – | Minimum residential dwelling units (CoO/legacy only) |
| `councilDistrict` | integer | – | City council district, 1–15 (live permit feeds only) |
| `communityPlanArea` | string | – | Substring match on the community plan area (live permit feeds only) |
| `neighborhoodCouncil` | string | – | Substring match on the neighbourhood council (live permit feeds only) |
| `aduOnly` | boolean | `false` | Keep only permits adding an ADU or junior ADU |
| `evChargingOnly` | boolean | `false` | Keep only EV-charging permits |
| `solarOnly` | boolean | `false` | Keep only solar permits |
| `nearLatitude` | number | – | Centre latitude for a radius search |
| `nearLongitude` | number | – | Centre longitude for a radius search |
| `radiusMeters` | number | `500` | Radius in metres; used only with both coordinates |
| `sortBy` | string | `issueDateDesc` | Issue/status/submitted/CoO date, valuation or square footage (live), or stories/residential units (CoO/legacy only) |
| `includeDetails` | boolean | `true` | Enrich live-feed records from CoO + legacy detailed datasets: contractor, applicant, occupancy, stories, units. Detail-dataset records are always refreshed with current live status |
| `includeInspections` | boolean | `false` | Add inspection count and last inspection date/type/result |
| `maxItems` | integer | `50` | Hard cap on emitted records (1–10,000) |
| `appToken` | string | – | Optional free Socrata app token to raise rate limits |

### Example: newest issued building permits

```json
{
  "mode": "search",
  "dataset": "issuedBuilding",
  "maxItems": 25
}
```

### Example: new-construction apartment or commercial permits over $1M

```json
{
  "mode": "search",
  "dataset": "issuedBuilding",
  "permitType": "Bldg-New",
  "permitSubType": "Apartment",
  "minValuation": 1000000,
  "issueDateFrom": "2026-01-01",
  "maxItems": 100
}
```

### Example: ADU applications submitted in the last 90 days

```json
{
  "mode": "search",
  "dataset": "submittedBuilding",
  "aduOnly": true,
  "submittedDateFrom": "2026-08-01",
  "maxItems": 200
}
```

### Example: solar and EV electrical permits in one ZIP

```json
{
  "mode": "search",
  "dataset": "issuedElectrical",
  "zipCodes": ["90047"],
  "solarOnly": true,
  "maxItems": 100
}
```

### Example: look up permit numbers

```json
{
  "mode": "byPermitNumbers",
  "permitNumbers": ["24016-20000-19408", "23016-10000-03206"]
}
```

### Example: permits at a specific address

```json
{
  "mode": "byAddress",
  "streetNumber": "6500",
  "streetName": "SEABLUFF"
}
```

### Example: a contractor's permit history

```json
{
  "mode": "byContractor",
  "contractorName": "OWNER-BUILDER",
  "maxItems": 100
}
```

### Example: assessor parcel lookup (Book-Page-Parcel / AIN)

```json
{
  "mode": "byAssessorParcel",
  "assessorBook": "2405",
  "assessorPage": "003",
  "assessorParcel": "032"
}
```

### Example: certificates of occupancy in a ZIP code

```json
{
  "mode": "search",
  "dataset": "certificateOfOccupancy",
  "zipCodes": ["91606"],
  "issueDateFrom": "2026-01-01",
  "maxItems": 50
}
```

### Example: permits within 500 m of downtown LA

```json
{
  "mode": "search",
  "nearLatitude": 34.0522,
  "nearLongitude": -118.2437,
  "radiusMeters": 500,
  "maxItems": 50
}
```

## Output

One dataset item per permit. Field names are camelCase and stable; empty values are omitted rather than written as `null`.

**Identity and type:** `permitNumber`, `permitGroup`, `permitType`, `permitSubType`, `permitCategory`, `useCode`, `useDescription`, `recordType`, `recordSource`, `sourceDataset`, `sourceDatasetName`, `documentationUrl`, `sourceUrl`, `rowId`, `scrapedAt`, `refreshTime`.

**Status and dates:** `status`, `statusDate`, `submittedDate`, `issueDate`, `cofoDate`, `cofoNumber`, `cofoIssueDate`.

**Location:** `fullAddress`, `addressStart`, `addressEnd`, `streetDirection`, `streetName`, `streetSuffix`, `unitRangeStart`, `unitRangeEnd`, `city`, `state`, `zipCode`, `councilDistrict`, `communityPlanArea`, `areaPlanningCommission`, `neighborhoodCouncil`, `censusTract`, `zone`, `latitude`, `longitude`, `geocodeType`.

**Parcel:** `apn`, `assessorBook`, `assessorPage`, `assessorParcel`, `pinNumber`, `tract`, `block`, `lot`.

**Project:** `workDescription`, `valuation`, `squareFootage`, `constructionType`, `buildingHeight`, `businessUnit`, `aduChanged`, `juniorAduChanged`, `dwellingUnitsChanged`, `evCharging`, `solar`.

**Contractor / people (when LADBS publishes them):** `contractorBusinessName`, `contractorAddress`, `contractorCity`, `contractorState`, `licenseType`, `licenseNumber`, `licenseExpirationDate`, `principalFirstName`, `principalMiddleName`, `principalLastName`, `applicantFirstName`, `applicantLastName`, `applicantBusinessName`, `applicantAddress1`, `applicantAddress2`, `applicantAddress3`, `occupancy`, `numberOfStories`, `residentialDwellingUnits`, `floorAreaZoningCode`, `floorAreaBuildingCode`, `initiatingOffice`, `referenceOldPermit`, `projectNumber`, `eventCode`, `detailSource`, `detailSourceUrl`, `currentSource`.

**Optional inspections (`includeInspections=true`):** `inspectionCount`, `firstInspectionDate`, `lastInspectionDate`, `lastInspectionType`, `lastInspectionResult`.

## Freshness and coverage

- **Live feeds** are refreshed by LADBS roughly daily; the newest row seen during the revamp was 2026-11-14. The city usually publishes a day's permits a few days later, so a one-day window can be empty.
- **History** is split by era and queried automatically: 1988–2009, 2010–2019, 2020 → today.
- **Submitted applications** are the earliest signal — they exist before a permit is issued.
- **Contractor identity** is not in the live feed. The actor reads the Certificate of Occupancy dataset (146 K rows, 2005 → today), the legacy detailed dataset (2015–2023, building only) and the all-trades legacy file (2013–2023) to fill it. That covers most older permits but only a minority of 2024+ permits; see the FAQ.
- **Detail-dataset freshness** — CoO, legacy and all-trades records are always refreshed against the matching live feed (building, electrical or mechanical) so their status and dates are current; `includeDetails` controls identity enrichment on live-feed records, not this refresh.

## FAQ

**Is this affiliated with the City of Los Angeles?**
No. It is a third-party reader of the City's public open data.

**Why do some records lack a contractor?**
LADBS stopped publishing contractor/owner/applicant names in the current permit feed. The names remain in the Certificate of Occupancy file, a frozen 2015–2023 building-only detailed file, and a frozen 2013–2023 all-trades file. The actor fills them when a matching row exists and omits the fields otherwise. For 2024+ permits only the CoO file can help: roughly 15 % of sampled 2024 permits, 4.5 % of 2025 permits and 0 % of 2026 permits had a CoO row at revamp time.

**Can I get owner names?**
No. LADBS does not publish owner names in any of these public datasets.

**What does "submitted" mean?**
A permit application filed with LADBS. It may later be issued, corrected or withdrawn. The same permit number can appear in both a submitted and an issued dataset; use `issueDateFrom` if you only want issued work.

**Is the valuation the project cost?**
No. It is the figure the applicant declares on the permit. It is useful for ranking leads but is not an appraisal or a contract price.

**Why are some fields missing on some permits?**
LADBS only publishes a field when the permit type has it. Square footage, height, construction type, ADU/EV/solar flags and geolocation are populated on a minority of records. Empty fields are omitted, never filled with a guess.

**How fresh is the data?**
Each run queries the live API. LADBS refreshes the feeds about daily and usually publishes a day's permits a few days later.

**Can I search a neighbourhood or ZIP?**
Yes. `zipCodes`, street and keyword filters work on every dataset. `communityPlanArea`, `neighborhoodCouncil`, `councilDistrict` and the ADU/EV/solar flags are published only on the live permit feeds, so they are not available when `dataset` is `certificateOfOccupancy` or `legacyDetailed`.

**Are there rate limits?**
The public API allows a reasonable number of requests without a token. Large enriched runs make one request per 100 permits for CoO/legacy lookups; a free Socrata `appToken` raises the limit if you run big jobs often.

**Does this cover LA County, Santa Monica or Pasadena?**
No. It covers permits issued by the City of Los Angeles Department of Building & Safety only.

**Can I get every permit for a contractor?**
Yes, within the limits of the CoO/legacy datasets (including the 2013–2023 all-trades file). Contractor names are not in the live feed, so a contractor lookup cannot see a 2024+ permit unless LADBS also published it in the CoO file.

**Does sorting by stories or residential units work?**
Yes on the Certificate of Occupancy and legacy datasets. The current live feed no longer carries those columns, so those two sort values fall back to issue date on live feeds and report the fallback in the run status. They remain in the input schema so saved tasks keep validating.

**Does it include inspections?**
Only when `includeInspections` is enabled. The inspections dataset is large and most new permits have not been inspected yet, so it is off by default.

**Is a proxy or cookie required?**
No. The actor reads public JSON APIs with plain HTTP.

## Data source and attribution

Data: City of Los Angeles Open Data (data.lacity.org), published by the Los Angeles Department of Building & Safety. Datasets include the Building/Electrical/Mechanical permits issued and submitted families, the Certificate of Occupancy file, the legacy LA BUILD PERMITS file, and the Building and Safety Inspections file. Use is subject to the portal's terms of use. Each record carries `sourceDataset`, `documentationUrl` and a `sourceUrl` that resolves the exact row.

This actor is not affiliated with or endorsed by the City of Los Angeles.
