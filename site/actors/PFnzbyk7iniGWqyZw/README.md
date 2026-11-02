# ImportYeti Company & Supplier Shipment Lookup

Search [ImportYeti](https://www.importyeti.com) by company name, supplier name, trademark, or product keyword, and get back the matching US importers and overseas suppliers — each with lifetime shipment counts, how recently they last shipped, their top trading partners, and any associated trademarks.

## What this actor does

- Matches a single query against ImportYeti's company, supplier, trademark, and product records
- Returns lifetime shipment counts and the most recent shipment date for every match
- Lists each company's top trading partners and any trademarks tied to it, when ImportYeti has them on file
- Lets you narrow results to importers only, suppliers only, a recent-activity window, or a minimum shipment count
- Omits any field ImportYeti didn't have data for — no nulls or placeholder text in the output

## Output per record

- `type` — always `importyeti_record` for a matched company or supplier
- `name` — company or supplier name
- `recordType` — `company` (US importer) or `supplier` (overseas exporter)
- `countryCode` — ISO 2-letter country code
- `address` — full address string as published
- `addressParsed` — the same address broken into `street`, `city`, `state`, `postalCode`, and `country` when it could be parsed
- `totalShipments` — lifetime shipment count
- `mostRecentShipment` — date of the latest shipment on record
- `topSuppliers` — the company's top trading partners
- `trademarks` — trademarks associated with the company, when any are on file
- `detailUrl` — link to the full profile on ImportYeti
- `scrapedAt` — ISO 8601 timestamp of when the record was collected

If nothing matches your query and filters, the run outputs a single record instead: `type: "importyeti_blocked"`, plus `query`, `typeFilter`, `recentFilter`, `minShipments`, `message`, and `scrapedAt`, explaining that no companies matched.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `query` | string | – | **Required.** Company name, supplier name, trademark, or product keyword |
| `type` | string | `any` | Restrict results to `company` (importers), `supplier` (exporters), or leave as `any` |
| `mostRecentShipment` | string | `any` | Keep only companies with a shipment in the last `6mo`, `12mo`, or `any` time |
| `minShipments` | integer | `0` | Exclude companies with fewer than this many lifetime shipments |
| `maxResults` | integer | `25` | Maximum records to return (1–1000) |

### Example: basic company search

```json
{
    "query": "electronics",
    "maxResults": 25
}
```

### Example: active suppliers only

```json
{
    "query": "furniture",
    "type": "supplier",
    "mostRecentShipment": "6mo",
    "maxResults": 50
}
```

### Example: high-volume importers

```json
{
    "query": "auto parts",
    "type": "company",
    "minShipments": 100,
    "maxResults": 100
}
```

## Use cases

- **Supplier discovery** — find overseas suppliers tied to a product category or trademark before reaching out
- **Competitor research** — see how many shipments a competitor's importer or supplier has moved and how recently
- **Supply-chain due diligence** — check a potential partner's shipment history and trading partners before committing
- **Lead generation** — build a list of active importers in a product niche, filtered to recent shipping activity
- **Trademark and brand tracking** — look up which companies are shipping goods tied to a specific trademark

## FAQ

**Do I need an ImportYeti account or API key?** No — this reads the same public search results ImportYeti shows to any visitor.

**Why would `topSuppliers` or `trademarks` be missing from a record?** Those fields only appear when ImportYeti has actual data for that company; many smaller importers and suppliers simply don't have trademarks or a published partner list.

**What does `mostRecentShipment` filter on?** It keeps only companies whose last recorded shipment falls inside the window you choose — useful for excluding importers or suppliers that have gone quiet.

**Can I search by product instead of company name?** Yes — `query` matches against company names, supplier names, trademarks, and product keywords all at once.

**Why might I get fewer records than `maxResults`?** ImportYeti simply may not have that many matches for your query and filter combination; the actor returns everything that qualifies, up to your limit.

**Is this affiliated with ImportYeti?** No. This is an independent actor that reads ImportYeti's public search results; it is not endorsed by or affiliated with ImportYeti.
