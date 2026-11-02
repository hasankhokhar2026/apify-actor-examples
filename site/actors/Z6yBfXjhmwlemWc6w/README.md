# ImportYeti US Importer & Global Supplier Search

Search **ImportYeti** — a public index built on US customs bill-of-lading records — for US importers by company name or product keyword, or for overseas suppliers by company name. Each match comes back with country, address, lifetime shipment count, most recent shipment date, alternate name and address counts, registered trademarks, and a link to its ImportYeti profile. No account required.

## What this actor does

- Searches in two modes: `searchImporters` for US buyers, `searchSuppliers` for overseas sellers
- Matches the same query field against both company names and product keywords
- Walks through result pages automatically until `maxItems` is reached or matches run out
- Keeps collecting across ImportYeti's per-IP usage cap when a proxy is configured, picking back up instead of stopping short
- Omits any field ImportYeti has no data for — no nulls or placeholders in the output

## Output per company

- `companyName` — company as listed on ImportYeti
- `type` — record type reported upstream (importer / supplier)
- `country` — ISO country code
- `address` — primary registered address
- `totalShipments` — lifetime shipment records attributed to the company
- `mostRecentShipment` — date of the latest shipment on file
- `otherAddressesCount` — additional known addresses for the same company
- `otherNamesCount` — additional known trading names
- `trademarks` — registered trademarks linked to the company (capped at 20)
- `companyUrl` — ImportYeti profile page
- `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `searchImporters` | `searchImporters` / `searchSuppliers` |
| `query` | string | `electronics` | Company name or product keyword |
| `maxItems` | int | `20` | Hard cap (1–500) |
| `proxyConfiguration` | object | `{"useApifyProxy": true}` | Proxy settings — strongly recommended, see FAQ |

### Example: US importers of a product

```json
{
  "mode": "searchImporters",
  "query": "electronics",
  "maxItems": 50,
  "proxyConfiguration": { "useApifyProxy": true }
}
```

### Example: a specific buyer's import footprint

```json
{
  "mode": "searchImporters",
  "query": "Home Depot",
  "maxItems": 25,
  "proxyConfiguration": { "useApifyProxy": true }
}
```

### Example: global suppliers by name

```json
{
  "mode": "searchSuppliers",
  "query": "Foshan furniture",
  "maxItems": 100,
  "proxyConfiguration": { "useApifyProxy": true }
}
```

### Example: wide sweep for lead generation

```json
{
  "mode": "searchImporters",
  "query": "lithium battery",
  "maxItems": 500,
  "proxyConfiguration": { "useApifyProxy": true }
}
```

## Use cases

- **Sourcing teams** — find overseas suppliers that already ship the product category you buy
- **B2B lead generation** — build lists of US importers active in a given product niche
- **Competitive intelligence** — see how many shipments a competitor receives and how recently
- **Supply-chain risk** — map which countries a company's inbound freight originates from
- **Trade finance & credit** — use shipment volume and recency as an activity signal on a counterparty
- **Brand protection** — spot importers bringing in goods under trademarks linked to your brand

## FAQ

**Where does this data come from?**  US Customs bill-of-lading filings, which are public records for ocean freight entering the United States. ImportYeti indexes and publishes them.

**Is this affiliated with ImportYeti?**  No. This is a third-party actor that reads ImportYeti's public search results; it is not endorsed by or affiliated with ImportYeti.

**Do I need an ImportYeti account?**  No. The search results this actor returns are the ones ImportYeti serves publicly.

**Why should I enable proxy?**  ImportYeti limits anonymous searching to roughly 25 requests per IP address before asking for a login. On Apify cloud many actors share exit IPs, so without a proxy a run can be cut short. With `{"useApifyProxy": true}` the actor rotates through IPs and picks up where it left off. The free Apify Proxy `AUTO` group is sufficient — no residential proxy needed.

**What happens if the limit is hit anyway?**  The run ends with a status message explaining the cap rather than failing, and any records already collected stay in the dataset.

**Does this cover air freight or exports?**  No. Bill-of-lading data is ocean freight into the US, so air cargo and US exports are out of scope.

**Why do some companies show a huge `otherNamesCount`?**  Large importers file under many trading names and subsidiaries. The count tells you how many aliases ImportYeti has consolidated under that profile.

**How current are the shipment dates?**  Customs data is published with a lag of a few weeks, so `mostRecentShipment` typically trails today's date even for very active importers.

**Why are trademarks capped at 20?**  Big brand owners hold hundreds. The first 20 keep records readable; the full list is on the linked `companyUrl` profile.
