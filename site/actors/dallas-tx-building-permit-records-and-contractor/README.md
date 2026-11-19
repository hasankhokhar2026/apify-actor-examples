# Dallas TX Building Permit Records & Contractor Lookup

The City of Dallas publishes its historical building permit filings on its open data portal, but filtering across tens of thousands of rows by hand isn't practical. This actor turns the Dallas building-permit dataset into filtered, structured records — by permit type, land use, ZIP code, contractor, date range, declared value, or an exact permit number.

## What this actor does

- Browses and filters Dallas permits by type, land use, ZIP code, keyword matches on work description/address/contractor/Mapsco grid, issued-date range, and declared value or area range.
- Looks up specific permits directly when you already know their permit numbers.
- Sorts results by declared value, area, or issued date, in either direction.
- Offers curated dropdowns for the most common permit types, land uses, and ZIP codes, with free-text "contains" fields to reach values outside those lists.
- Leaves a field out of a record whenever the source filing never recorded it, rather than filling it with a placeholder.

## Output per permit

| Field | Description |
|---|---|
| `permitNumber` | Dallas permit number |
| `permitType` | Permit type as filed, e.g. `Building (BU) Single Family New Construction` |
| `issuedDate` | Issue date in `YYYY-MM-DD` format |
| `workDescription` | Free-text description of the work |
| `landUse` | Zoning / land-use classification |
| `streetAddress` | Address the permit was filed for |
| `zipCode` | ZIP code of the address |
| `value` | Declared project value in USD, when recorded |
| `area` | Declared project area in square feet, when recorded |
| `contractor` | Contractor name, address, and phone as filed |
| `contractorPhone` | Phone number pulled out of the `contractor` field, when present |
| `mapsco` | Dallas Mapsco grid reference |
| `sourceUrl` | Link to this permit's record in the Dallas Open Data API |
| `recordType` | Always `"buildingPermit"` |
| `scrapedAt` | UTC timestamp of the scrape |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` to browse and filter, or `byPermitNumbers` to look up exact permits. |
| `permitType` | string | – (Any) | One exact permit type from a curated list of the 45 most common of 137 total types. |
| `permitTypeCustom` | string | – | Free-text contains-match for a permit type outside the dropdown; takes precedence over `permitType`. |
| `landUse` | string | – (Any) | One exact land-use classification from a curated list of the 45 most common of 189 total uses. |
| `landUseCustom` | string | – | Free-text contains-match for a land use outside the dropdown; takes precedence over `landUse`. |
| `zipCode` | string | – (Any) | One Dallas-area ZIP code to restrict results to. |
| `workDescriptionKeyword` | string | – | Keep only permits whose work description contains this text. |
| `streetAddressKeyword` | string | – | Keep only permits whose street address contains this text. |
| `contractorKeyword` | string | – | Keep only permits whose contractor field contains this text. |
| `mapscoKeyword` | string | – | Keep only permits whose Mapsco grid reference contains this text. |
| `issuedDateFrom` | string | – | Earliest issue date to include, `YYYY-MM-DD`. |
| `issuedDateTo` | string | – | Latest issue date to include, `YYYY-MM-DD`. |
| `minValue` | integer | – | Lowest declared permit value (USD) to include. |
| `maxValue` | integer | – | Highest declared permit value (USD) to include. |
| `minArea` | integer | – | Smallest declared area (sq ft) to include. |
| `maxArea` | integer | – | Largest declared area (sq ft) to include. |
| `sortBy` | string | `default` | `default`, `valueHighToLow`, `valueLowToHigh`, `areaHighToLow`, `areaLowToHigh`, `issuedDateNewestFirst`, or `issuedDateOldestFirst`. |
| `permitNumbers` | array | `[]` | Exact permit numbers to look up in `byPermitNumbers` mode. |
| `maxItems` | integer | `50` | Maximum number of records to return. |

### Example: new single-family construction

```json
{
  "mode": "search",
  "permitType": "Building (BU) Single Family  New Construction",
  "maxItems": 50
}
```

### Example: high-value permits in one ZIP code

```json
{
  "mode": "search",
  "zipCode": "75201",
  "minValue": 500000,
  "sortBy": "valueHighToLow",
  "maxItems": 100
}
```

### Example: lookup by permit number

```json
{
  "mode": "byPermitNumbers",
  "permitNumbers": ["2003133024", "1904171125"]
}
```

## Use cases

- **Contractor lead generation** — find which contractors filed recent permits for a project type you serve.
- **Neighborhood development research** — track new construction, additions, and renovations by ZIP code or land use.
- **Property due diligence** — check whether permitted work was ever filed for a specific address.
- **Market sizing** — total declared permit value or area across a permit type or ZIP code to gauge building activity.
- **Civic and academic research** — study Dallas development patterns across permit types and time.

## FAQ

**Where does this data come from?**
The City of Dallas's own open data portal, specifically its Building Permits dataset.

**How recent is the data?**
The dataset covers permits issued between January 2018 and August 2020. Dallas migrated active permit tracking to a different system after that and hasn't updated this historical dataset since — the permit records themselves are complete and accurate for that window, but there's no newer data to pull.

**Why do some records have no `value` or `area`?**
Plenty of permit types — many electrical or plumbing alteration permits, for example — never had a declared dollar value or square footage filed in the first place. Rather than show a misleading `0`, the field is left off the record.

**Why isn't ascending value/area sort just the mirror of descending sort?**
A large share of permits have no recorded value or area at all. Sorting ascending without excluding those would put every "not recorded" permit first, so `valueLowToHigh` and `areaLowToHigh` only return permits with a real positive number, keeping the sort meaningful. Descending sort doesn't need this adjustment since those rows already fall to the bottom.

**Why do some permits have no `contractor`?**
Owner-filed or self-built projects often went through without naming a contractor in the original filing, so there's nothing to report for that field.

**What's the difference between a dropdown field and its `Custom` counterpart?**
The dropdowns cover the most common ~45 permit types and ~45 land uses out of 137 and 189 total values. If what you need isn't listed, the matching `Custom` field matches any value containing the text you type, covering the rest.

**Is there a location/map field?**
No — the source data has no coordinates, only a street address, ZIP code, and Mapsco grid reference, so there's nothing accurate to populate a map field with.

**Is this affiliated with the City of Dallas?**
No. This actor reads the City of Dallas's public open data and is not affiliated with, endorsed by, or connected to the City of Dallas in any way.
