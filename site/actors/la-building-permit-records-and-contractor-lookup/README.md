# LA Building Permit Records & Contractor Lookup

Pull permit records straight from the City of Los Angeles Department of Building & Safety (LADBS) public dataset — every permit the department has issued, broken down to the permit-number level. Run it as an open-ended search across the whole city or as a pinpoint lookup for one address, contractor, or parcel. No account or API key is needed to query LADBS data.

## What this actor does

- **Five modes:** `search`, `byPermitNumbers`, `byAddress`, `byContractor`, `byAssessorParcel`
- **Rich filters:** permit type/sub-type/category, status, initiating office, street direction/suffix, occupancy group, zip codes, issue/status date range, valuation range, story count range, minimum residential units, work-description keyword, geo-radius search (lat/lng + radius)
- **Full permit detail:** contractor, principal, and applicant identity; construction valuation and floor area; assessor block/lot/tract; census tract; latitude/longitude
- **Sortable:** by issue date, status date, valuation, number of stories, or residential dwelling units
- **Empty fields are omitted**

## Output per permit

- `permitNumber` — LADBS PCIS permit number
- `referenceOldPermit` — legacy/cross-referenced permit number, if any
- `status`, `statusDate` — current permit status and the date it was last updated
- `permitType`, `permitSubType`, `permitCategory` — e.g. `Bldg-New` / `1 or 2 Family Dwelling` / `Plan Check`
- `projectNumber`, `eventCode`, `initiatingOffice`
- `issueDate` — date the permit was issued
- `addressStart`, `addressEnd`, `addressFractionStart`, `addressFractionEnd` — street-number range covered by the permit
- `streetDirection`, `streetName`, `streetSuffix`, `suffixDirection`
- `unitRangeStart`, `unitRangeEnd`
- `fullAddress`, `city`, `state`, `zipCode`
- `workDescription` — free-text description of the work
- `valuation` — declared construction valuation (USD)
- `floorAreaZoningCode`, `floorAreaBuildingCode` — floor area (sq ft) under LA zoning / building code definitions
- `residentialDwellingUnits`, `numberOfStories`
- `contractorBusinessName`, `contractorAddress`, `contractorCity`, `contractorState`
- `licenseType`, `licenseNumber`, `licenseExpirationDate`
- `principalFirstName`, `principalMiddleName`, `principalLastName`
- `applicantFirstName`, `applicantLastName`, `applicantBusinessName`, `applicantAddress1`, `applicantAddress2`, `applicantAddress3`
- `zone`, `occupancy`, `censusTract`
- `assessorBook`, `assessorPage`, `assessorParcel`, `tract`, `block`, `lot`
- `latitude`, `longitude`
- `sourceUrl` — public API query URL that resolves this exact permit record
- `rowId` — the source dataset's internal row identifier, used to de-duplicate rows across pages
- `recordType: "buildingPermit"`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `byPermitNumbers` / `byAddress` / `byContractor` / `byAssessorParcel` |
| `permitNumbers` | array | – | Exact PCIS permit numbers (mode=byPermitNumbers) |
| `streetNumber` | string | – | Building street number (mode=byAddress, optional) |
| `streetName` | string | – | Street name — exact in byAddress, substring filter in search |
| `streetDirection` | string | – | `N` / `S` / `E` / `W` |
| `streetSuffix` | string | – | e.g. `AVE`, `ST`, `BLVD` |
| `contractorName` | string | – | Contractor business name — exact in byContractor, substring filter in search |
| `assessorBook` / `assessorPage` / `assessorParcel` | string | – | LA County Assessor's Identification Number (AIN) components — exact match (mode=byAssessorParcel, all three required) |
| `workDescriptionKeyword` | string | – | Substring match on the work description |
| `permitType` | string | – | `Bldg-New` / `Bldg-Addition` / `Bldg-Alter/Repair` |
| `permitSubType` | string | – | `1 or 2 Family Dwelling` / `Apartment` / `Commercial` |
| `permitCategory` | string | – | `Plan Check` / `No Plan Check` |
| `status` | string | – | Current permit status (27 possible values) |
| `initiatingOffice` | string | – | LADBS district office |
| `occupancy` | string | – | Building-code occupancy group (25 possible values, e.g. `R3 Occ. Group`). Only populated on a minority of permits. |
| `zipCodes` | array | – | One or more 5-digit zip codes |
| `issueDateFrom` / `issueDateTo` | string | – | Issue-date range (`YYYY-MM-DD`) |
| `statusDateFrom` / `statusDateTo` | string | – | Status-date range (`YYYY-MM-DD`) |
| `minValuation` / `maxValuation` | number | – | Declared construction valuation range (USD) |
| `minStories` / `maxStories` | integer | – | Number-of-stories range |
| `minResidentialUnits` | integer | – | Minimum residential dwelling units |
| `nearLatitude` / `nearLongitude` | number | – | Center point for a geo-radius search. Both must be set together. |
| `radiusMeters` | number | `500` | Radius (in meters) around `nearLatitude`/`nearLongitude`. Only used when both coordinates are set. |
| `sortBy` | string | `issueDateDesc` | Sort order — issue date / status date / valuation / number of stories / residential units, each asc or desc |
| `appToken` | string | – | Optional free Socrata app token to raise rate limits |
| `maxItems` | integer | `50` | Hard cap on emitted records (1–10000) |

### Example: recent new-construction permits in a zip code

```json
{
  "mode": "search",
  "permitType": "Bldg-New",
  "zipCodes": ["90047"],
  "sortBy": "issueDateDesc",
  "maxItems": 50
}
```

### Example: lookup by permit number

```json
{
  "mode": "byPermitNumbers",
  "permitNumbers": ["20010-30000-00390", "19010-20000-04796"]
}
```

### Example: permits at a specific address

```json
{
  "mode": "byAddress",
  "streetNumber": "6500",
  "streetName": "SEABLUFF",
  "streetSuffix": "DR"
}
```

### Example: all permits for a contractor

```json
{
  "mode": "byContractor",
  "contractorName": "OWNER-BUILDER",
  "maxItems": 100
}
```

### Example: lookup by assessor parcel (Book-Page-Parcel / AIN)

```json
{
  "mode": "byAssessorParcel",
  "assessorBook": "2405",
  "assessorPage": "003",
  "assessorParcel": "032"
}
```

### Example: high-value apartment permits issued in a date range

```json
{
  "mode": "search",
  "permitSubType": "Apartment",
  "issueDateFrom": "2022-01-01",
  "issueDateTo": "2022-12-31",
  "minValuation": 500000,
  "sortBy": "valuationDesc"
}
```

### Example: permits within 500m of a point (downtown LA)

```json
{
  "mode": "search",
  "nearLatitude": 34.0522,
  "nearLongitude": -118.2437,
  "radiusMeters": 500,
  "sortBy": "issueDateDesc"
}
```

## Use cases

- **Real estate research** — track new construction, additions, and remodels in a neighborhood or zip code
- **Contractor intelligence** — pull a contractor's full LA permit history by business name
- **Market analysis** — trend construction valuation and permit volume over time
- **Lead generation** — find recently permitted projects for suppliers, insurers, or service providers
- **Compliance / due diligence** — verify a property's permit history and current permit status before a transaction

## FAQ

**What is the data source?**
The City of Los Angeles Open Data portal (data.lacity.org), specifically the "LA Building Permits" dataset (Socrata id `xnhu-aczu`) published by the LA Department of Building & Safety.

**Is this affiliated with the City of Los Angeles?**
No — this is a third-party actor that reads the City's public open-data API.

**How fresh is the data?**
The source dataset is refreshed periodically by LADBS; this actor always queries the live API, so results reflect whatever is currently published.

**Are there rate limits?**
The public API allows a reasonable number of requests without a token. If you scrape large volumes regularly, you can supply a free Socrata `appToken` to raise your rate limit.

**Why do some permits have the same permit number but different addresses?**
A small number of multi-parcel or multi-building projects in the source data share the same PCIS permit number across rows (e.g. Building A/B of the same project). Each row is still emitted as its own record.

**Why are some fields missing on certain permits?**
LADBS does not populate every field for every permit (e.g. `occupancy` and `residentialDwellingUnits` are rarely filled in for commercial-alteration permits). The source data also uses placeholders like `-` or `NA` for "not provided" on some fields (e.g. applicant/principal names, contractor address); the actor omits the field on that row rather than returning the placeholder text. Empty fields are omitted rather than returned as `null`.

**Why aren't `contractorState` and `licenseType` available as filter dropdowns?**
Both are free-text in the source data with inconsistent values (e.g. license class recorded as `B`, `b`, `01B`, or `C39` for what should be the same class; state recorded with non-standard codes). Rather than offer an inaccurate dropdown, they remain available as plain output fields.

**Why isn't `zone` available as a filter dropdown?**
LA zoning has 1,400+ distinct real codes (e.g. `R1-1`, `RD1.5-1XL`, `R1-1-HPOZ`) — too many and too granular for a stable dropdown. It's still returned as a plain output field on every permit.

**Some permits show unusually high or missing `numberOfStories`/`residentialDwellingUnits` — why?**
The City's source data contains occasional data-entry errors on these two fields (e.g. a small addition recorded with dozens of "stories"). The actor applies sub-type-aware plausibility limits — tight for single-family-home permits, wide for apartment/commercial towers — and omits the field on the rare row that falls outside a realistic range rather than surfacing an obviously mistaken number.

**Can I search near a location instead of an exact address?**
Yes — set `nearLatitude`/`nearLongitude` (and optionally `radiusMeters`, default 500m) to return only permits within that radius of a point. This combines with every other filter, including permit type, status, and date range.
