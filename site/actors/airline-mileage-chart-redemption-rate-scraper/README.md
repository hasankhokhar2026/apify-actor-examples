# Airline Mileage Chart Redemption Rate Scraper

Read published award-chart rates directly from seven loyalty programs' current public PDF or HTML charts. Every emitted miles value comes from the issuer's parsed chart; conversions between one-way and round-trip are marked in `derivedFields`. The actor does not invent taxes, partner multipliers, or premium-cabin rows.

## What this actor does

- Fetches each selected issuer's public chart at run time and parses the issuer-native rows.
- Maps native zones onto seven macro regions while keeping the issuer's own zone labels in `originZone` / `destinationZone`.
- Filters by cabin, one-way vs. round-trip, partner-only, distance band, native zone, and award product.
- Returns source provenance for every row: URL, title, format, effective date, retrieval time, parser version, and a content hash.
- Writes one `chart_status` record per selected issuer (optional in the dataset, always in the `STATUS` key-value record), so a skipped issuer is never silent.
- Emits no tax fields: these charts do not publish taxes, fees, or carrier surcharges.

## Supported live charts

| Issuer key | Program | Source format | Native pricing | Notes |
|---|---|---|---|---|
| `aeroplan` | Air Canada Aeroplan | PDF | One-way, distance bands | Air Canada/Select Partners and "All other partners" rows; Aeroplan's Atlantic zone is mapped to Europe, Africa, and the Middle East, and its Pacific zone to Asia and Oceania. |
| `lufthansa` | Lufthansa Miles & More | PDF | Round-trip, region matrix | Star Alliance Award Flight chart only; all rows are partner awards. |
| `singaporeKrisflyer` | Singapore Airlines KrisFlyer | PDF | One-way, zone matrix | Saver and Advantage charts; Zone 10 is labelled "Africa, Middle East and Turkey" by the issuer and is mapped to Africa and the Middle East. |
| `anaMileage` | ANA Mileage Club | HTML | One-way, zone matrix | ANA Partner Airline Flight Awards; the chart publishes economy, business, and first, not premium economy. |
| `jal` | JAL Mileage Bank | HTML | One-way, route/zone | JAL-operated international awards from Japan; base cabins plus first-class seasonal rows. |
| `qantas` | Qantas Frequent Flyer | HTML | Distance bands | Qantas, Jetstar, Emirates, Partner, and oneworld Classic Flight Reward tables. Qantas prices by distance, so every distance band matches any macro region pair. |
| `turkishMilesAndSmiles` | Turkish Airlines Miles&Smiles | HTML | One-way, region matrix | Turkish-operated Promotion and standard Award Tickets from/to Türkiye, plus the Star Alliance partner matrix. |

The visible `issuers` input lists only these seven adapters. Saved tasks that still send an older key (`united`, `american`, `alaska`, `britishAirways`, and so on) keep running: the actor emits an explicit `chart_status` record with `no_chart`, `blocked`, or `requires_browser` and does not silently skip the issuer.

## Output per rate

| Field | Description |
|---|---|
| `recordType` | `mileage_chart` for a rate row, `chart_status` for a status row. |
| `issuer` / `issuerName` | Program key and display name. |
| `originRegion` / `destinationRegion` | Macro regions requested by the user. |
| `originZone` / `destinationZone` | The issuer's own zone labels for this row. |
| `direction` | `forward` when the native row matches the request order, `reverse` when it is applied symmetrically. |
| `cabin` | `economy`, `premium`, `business`, or `first`. |
| `awardType` / `tier` | Published product and native tier, such as `saver`, `classic`, `promotion`, `star_alliance`, or `fixed_chart`. |
| `miles` | Miles for the requested basis: one-way when `oneWay` is true, otherwise round-trip. |
| `milesOneWay` / `milesRoundTrip` | Both bases when published or derivable. |
| `nativeDirection` | `one_way` or `round_trip`: the basis the issuer publishes natively. |
| `derivedFields` | Names of fields computed from the published value, e.g. `["miles","milesRoundTrip"]`. |
| `isPartner` / `partnerName` | Whether the row is a partner-operated award and the published partner label. |
| `distanceBandMin` / `distanceBandMax` | Distance band for distance-priced charts; `distanceBandMax` is omitted for an open-ended band. |
| `season` / `isPeak` | Published season when the chart is seasonal. |
| `isCombinedCabin` | `true` when the source combines cabins (for example, Singapore Suites/First). |
| `milesNote` | The issuer's chart context, markers, and distance band. |
| `sourceUrl` / `sourceTitle` / `sourceFormat` | Provenance for the chart that produced the row. |
| `sourceEffectiveDate` | Date or month the issuer says the chart is effective. |
| `retrievedAt` / `scrapedAt` | ISO 8601 retrieval time. |
| `verificationStatus` | `live` or `static_snapshot`. |
| `parserVersion` / `contentHash` | Parser identifier and the first 16 hex characters of the fetched content's SHA-256. |
| `status` / `statusMessage` / `recordsReturned` | Present on `chart_status` rows, together with the same provenance fields. |

`taxes_min_usd`, `taxes_max_usd`, `taxesCurrency`, and `taxesNote` are retained as legacy field names but are not emitted, because the live charts do not publish tax amounts. No value is estimated.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `originRegion` | String (select) | `"north_america"` | Macro region the trip departs from. |
| `destinationRegion` | String (select) | `"europe"` | Macro region the trip ends in. |
| `cabin` | String (select) | `"business"` | Cabin to return. |
| `issuers` | Array (select) | `["lufthansa"]` | Live chart adapters to query. |
| `oneWay` | Boolean | `false` | Return one-way values; round-trip charts are halved and marked as derived. |
| `partnerOnly` | Boolean | `false` | Keep only partner-operated award rows. |
| `maxResults` | Integer | `5` | Cap on pushed `mileage_chart` rows; status rows do not count. |
| `distanceMiles` | Integer | none | Optional filter for distance-priced charts (Aeroplan, Qantas Classic). Zone-priced charts ignore it. |
| `originZone` / `destinationZone` | String | none | Optional case-insensitive text match on the issuer's native zone. |
| `awardType` | String (select) | `"any"` | Filter on a published award product. |
| `fallbackMode` | String (select) | `"live_only"` | `snapshot` replays the most recent successful parse cached in this actor's key-value store when a live fetch fails. |
| `includeStatusRecords` | Boolean | `true` | Push `chart_status` rows to the dataset. The `STATUS` key-value record is always written. |

### Example: default prefill

```json
{
    "originRegion": "north_america",
    "destinationRegion": "europe",
    "cabin": "business",
    "issuers": ["lufthansa"],
    "maxResults": 5
}
```

### Example: Aeroplan distance bands

```json
{
    "originRegion": "north_america",
    "destinationRegion": "asia",
    "cabin": "business",
    "issuers": ["aeroplan"],
    "distanceMiles": 9000,
    "oneWay": true
}
```

### Example: compare several programs

```json
{
    "originRegion": "north_america",
    "destinationRegion": "europe",
    "cabin": "business",
    "issuers": ["aeroplan", "lufthansa", "singaporeKrisflyer", "turkishMilesAndSmiles"],
    "maxResults": 100
}
```

## Status and provenance

Every run writes a `STATUS` key-value record containing:

- the effective input,
- one entry per selected issuer with `status`, `statusMessage`, `recordsReturned`, and provenance,
- whether `maxResults` truncated the output.

Status values are `live`, `static_snapshot`, `blocked`, `no_chart`, `parse_error`, and `requires_browser`. A live fetch that succeeds but matches no rows reports `live` with `recordsReturned: 0` and a clear message; it is not treated as a silent skip.

`fallbackMode: "snapshot"` only uses a cache written by this actor after an earlier successful parse. It never fabricates a chart and never runs by default.

## Region mapping and native zones

Charts use their own zones. The actor maps them onto the seven macro regions but keeps the native labels, so two rows can share a macro region pair and still differ:

- Aeroplan's Atlantic zone covers Europe, Africa, the Middle East, and also India; India is not mapped to Asia here. Aeroplan's Pacific zone covers Asia and Oceania.
- ANA zone 5 is Hawaii and zone 6 is North America; both map to the `north_america` macro.
- Singapore zone 10 is Africa, the Middle East and Turkey; it is mapped to Africa and the Middle East, not Europe.
- Turkish "Türkiye" rows are mapped to the Europe macro, while the Turkish chart keeps its own `Türkiye`, `Europe 1`, and `Europe 2` labels.
- JAL rows originate in Japan and are therefore returned for `originRegion: "asia"` only.
- Qantas Classic charts are distance-based, not region-based; all distance bands match any macro pair, and `distanceMiles` narrows them.

Use `originZone` / `destinationZone` to select an exact native zone when a macro mapping is broader than you want.

## Limitations

- **No live seat availability.** These are published charts, not a search for bookable award seats on a date.
- **No taxes or surcharges.** The charts do not publish them, so the actor does not estimate them.
- **No browser-only programs.** American, Copa, and SAS need a JavaScript browser session; legacy keys return `requires_browser`. Alaska blocks non-browser requests (HTTP 406) and no dated snapshot is bundled, so its legacy key returns `blocked`.
- **No public charts.** British Airways, Emirates, Flying Blue, LifeMiles, Qatar, United, Virgin Atlantic, Aeromexico, Azul, Delta, Etihad, and Finnair publish no fixed public chart that this actor can verify; their legacy keys return `no_chart`.
- **Chart coverage is not every route.** A chart may price only some region pairs or cabins. Missing pairs return no rows rather than an invented value.
- **ANA partner chart only.** ANA-operated seasonal charts are not mixed into the partner rows.
- **Lufthansa partner chart only.** Miles & More dynamically prices its own-metal flights in the booking flow; this actor reads the fixed Star Alliance Award Flight chart.
- **Derived conversions.** One-way/round-trip conversion is arithmetic on a published value and is always named in `derivedFields`. Odd round-trip values are not halved; the one-way row is omitted.

## Use cases

- Compare published award-chart prices across programs before transferring points.
- Build a redemption calculator from real chart values with source dates and hashes.
- Audit a chart change by comparing `contentHash`, `sourceEffectiveDate`, and parsed rows between runs.
- Keep a provenance trail for travel-hacking research without scraping dynamic availability.

## FAQ

**Is this live seat availability?**
No. It reads the published mileage charts that programs use to price awards.

**Why are taxes missing?**
Because the charts do not publish tax amounts. The legacy tax field names remain in the schema for compatibility, but no value is estimated or invented.

**Why did an issuer return a `chart_status` row instead of rates?**
The program either has no fixed public chart, blocks non-browser requests, needs a browser session, or the chart could not be parsed. The status row states which case applies.

**What does `derivedFields` mean?**
It lists the output fields that were calculated from the issuer's published value, usually the one-way or round-trip counterpart. The published value itself is never altered.

**Why can a macro region pair return several rows?**
Native zones are finer than the seven macro regions. For example, ANA prices Hawaii separately from North America, and Aeroplan prices several distance bands. `originZone`, `destinationZone`, and `distanceBandMin` / `distanceBandMax` keep the rows distinct.

**Are taxes/fees ever added from another source?**
No. The actor only emits values parsed from the selected issuer's chart.

**Is this affiliated with any airline or loyalty program?**
No. It reads publicly published charts and is not affiliated with or endorsed by any airline, alliance, or loyalty program.
