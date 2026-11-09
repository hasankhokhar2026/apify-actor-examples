# ImportYeti Trade, Supplier & Shipment Scraper

Search **ImportYeti** and pull three kinds of data from one actor across its public **US import**, **US export**, and **Mexico** datasets:

- **Company and supplier records** from keyword search, profile URLs, or an HS code.
- **Full profile enrichment** for importers, exporters, and overseas suppliers: website, phone/contact info, geography, 12-month activity, quarterly growth, monthly time series, partners, ports and lanes, carriers/SCAC, containers, HS and HTS breakdowns, notify parties, other addresses, other websites, trademarks, and UFLPA status.
- **Shipment rows** — one record per recent bill of lading, with BOL/master BOL, date, counterparty, route, transport type, weight, containers, quantity, product description, and CIF value when the source publishes it.

No ImportYeti account, cookie, or API key is required. Every record has a `recordType` (`company`, `supplier`, `hsCode`, or `shipment`) so you can split the dataset into streams. Every record also carries `dataset` (`us-import`, `us-export`, or `mx`), and profile/shipment records carry `sourceDomain`, so records from different datasets stay distinguishable.

## Modes

| Mode | Input | What you get |
|---|---|---|
| `searchImporters` | `query` | US importer summaries, paged until `maxItems` |
| `searchSuppliers` | `query` | Overseas supplier summaries, paged until `maxItems` |
| `companyProfile` | `startUrls` (URL or slug) | One enriched profile per US import company/supplier, US export company, or Mexico company/supplier |
| `searchByHsCode` | `hsCode` (2–10 digits) | HS summary, top importing companies, top suppliers, and optionally recent shipments under that code |

`includeShipments` adds shipment rows in `companyProfile` and `searchByHsCode`, and in the two search modes it fetches each matched company profile once to add its recent shipments.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `searchImporters` | One of the four modes above |
| `query` | string | `electronics` | Company name or product keyword for search modes; also accepted as a profile URL fallback or numeric HS-code fallback |
| `startUrls` | array | `[]` | `companyProfile` targets: full ImportYeti URLs or paths — `company/...`, `supplier/...`, `us-export/company/...`, `mx/company/...`, `mx/supplier/...` — or bare US company slugs |
| `hsCode` | string | — | `searchByHsCode` target with 2–10 digits. 2-digit chapters (`84`) and 4-digit headings (`8418`) load directly; 6+ digit subheadings use the HS search API (e.g. `841810` or `8418.10`); 8/10-digit HTS codes fall back to the 6-digit subheading |
| `maxItems` | integer | `20` | Total dataset records, 1–500 |
| `includeShipments` | boolean | `false` | Add one record per recent BOL (`recordType: "shipment"`) |
| `since` | string | — | Recency filter (`YYYY-MM-DD` or `DD/MM/YYYY`) for shipment dates and a company's most recent shipment date |
| `addressContains` | string | — | Case-insensitive filter on company/supplier address (state, city, street) |
| `proxyConfiguration` | object | `{"useApifyProxy": true}` | Optional. AUTO datacenter proxy is enough; no residential proxy needed |

## Examples

Search US importers:

```json
{
  "mode": "searchImporters",
  "query": "lithium battery",
  "maxItems": 100
}
```

Load a company profile and its recent shipments:

```json
{
  "mode": "companyProfile",
  "startUrls": [
    {"url": "https://www.importyeti.com/company/samsung-electronics-america"}
  ],
  "includeShipments": true,
  "maxItems": 60
}
```

Load a supplier by URL or slug:

```json
{
  "mode": "companyProfile",
  "startUrls": [{"url": "supplier/foxconn"}],
  "maxItems": 5
}
```

Load US export and Mexico profiles:

```json
{
  "mode": "companyProfile",
  "startUrls": [
    {"url": "https://www.importyeti.com/us-export/company/ikea-supply"},
    {"url": "https://www.importyeti.com/mx/company/latex-centroamericana"},
    {"url": "https://www.importyeti.com/mx/supplier/mic650113792"}
  ],
  "includeShipments": true,
  "maxItems": 60
}
```

Explore a 4-digit HS heading:

```json
{
  "mode": "searchByHsCode",
  "hsCode": "8418",
  "includeShipments": true,
  "maxItems": 25
}
```

Explore an HS subheading:

```json
{
  "mode": "searchByHsCode",
  "hsCode": "841810",
  "includeShipments": true,
  "maxItems": 25
}
```

Search with filters:

```json
{
  "mode": "searchImporters",
  "query": "furniture",
  "addressContains": "North Carolina",
  "since": "2026-01-01",
  "maxItems": 50
}
```

## Output

### Company / supplier records (`recordType: "company"` or `"supplier"`)

Core fields: `companyName`, `type`, `dataset`, `sourceDomain`, `country`, `countryName`, `address`, `website`, `phoneNumber`, `phones`, `companyUrl`, `totalShipments`, `shipments12m`, `mostRecentShipment`, `otherAddressesCount`, `otherNamesCount`, `trademarks`, `scrapedAt`.

Profile enrichment (when the profile page is loaded): `alsoKnownNames`, `otherAddresses`, `otherWebsites`, `trademarkDetails`, `uflpa`, `hasInternalShipments`, `internalSuppliersCount`, `notifyPartyShipments`, `notifyPartyShipmentsPercent`, `geo`, `dateRange`, `avgTeuPerMonth`, `avgTeuPerShipment`, `quarterlyGrowth`, `timeSeries` (up to 120 monthly points), `totalShippingCostUsd`, `shippingCostCoveragePercent`.

`phones` lists the contact numbers ImportYeti publishes for the company's addresses, with shipment/company/address counts and the last shipment date/BOL. The masked display numbers (`XXX-XXX-X000`) are omitted; `phoneNumber` is only present when the source publishes an unmasked main number.

Breakdowns: `partners` (suppliers for a US importer, customers for a supplier), `partnerRole`, `notifyParties`, `carriers`, `carriersByCountry`, `lanes`, `containers`, `containerLoad`, `hsCodes`, `htsCodes`, `topImportHsChapters`, `billTypeShipments`, `tags`.

### HS code record (`recordType: "hsCode"`)

`dataset` (`us-import`), `hsCode`, `description`, `exactDescription`, `totalShipments`, `tariff`, `dateRange`, `totals` (weight/TEU), `companyCount`, `supplierCount`, `companyUrl`, `scrapedAt`.

### Shipment record (`recordType: "shipment"`)

`companyName` / `companyUrl` / `companyType` / `dataset` / `sourceDomain` (the profile owner in profile/search modes; absent in HS-code shipment rows), `bol`, `bolId`, `masterBol`, `houseBol`, `billTypeCode`, `billType`, `transportType`, `date`, `counterpartyName`, `counterpartyAddress`, `counterpartyCountry`, `counterpartyCountryCode`, `counterpartyUrl`, `shipperName`, `weightKg`, `containersCount`, `quantity`, `quantityUnit`, `productDescription`, `shippingRoute`, `shippingCostUsd`, `cifValueUsd`, `cifBillType`, `hsCode` (in HS mode), `scrapedAt`.

All records are omit-empty: a field the source does not publish is left out, never returned as `null` or a placeholder.

## Use cases

- **Sourcing** — find suppliers that already ship a product category, then inspect their lanes and carriers.
- **B2B lead generation** — build importer lists by keyword, address, or HS code.
- **Competitive intelligence** — compare shipment volume, 12-month activity, quarterly growth, and recent BOLs.
- **Supply-chain risk** — map countries, ports, carriers, and notify parties for a counterparty.
- **Trade finance** — use shipment recency and CIF values as activity signals.
- **Tariff and product research** — start from an HS code and see who imports it and under which HTS lines.

## FAQ

**Where does this data come from?** Public records ImportYeti indexes: US Customs ocean bills of lading (US import dataset), US export bills of lading, and Mexico's SAT customs records (the `mx` dataset). Each profile record reports its `dataset`.

**Is this affiliated with ImportYeti?** No. This is a third-party actor that reads ImportYeti's public pages.

**Do I need an ImportYeti account?** No. The actor uses only public pages. It never logs in, and it does not bypass login walls or paid views.

**What are the hard limits?** ImportYeti allows roughly **25 pageviews per IP** before asking for a login. Public profiles expose at most **100 recent BOLs for US import companies** (two 50-row views merged by BOL) and up to **50 for US export and Mexico profiles**; that is the source ceiling, not an actor cap. Full BOL details, full contact records, and power-query exports require an ImportYeti login or paid plan and are out of scope. The US import dataset covers **ocean imports** only (no air freight); the US export and Mexico datasets are separate and the Mexico records include truck/air/sea transport types where the source publishes them.

**Why enable proxy?** On Apify cloud many runs share exit IPs. AUTO datacenter proxy rotation keeps the request budget fresh; no residential proxy is required. The daily-test prefill stays on the cheapest path that returns records.

**What happens when the limit is hit?** The run rotates proxy sessions when configured, keeps the records already collected, and ends with a status message instead of failing. A profile that cannot be loaded is skipped with a log line.

**Why do some 2- and 4-digit HS pages lack a tariff?** ImportYeti publishes tariff/AHTN detail on 6+ digit subheading pages. Chapter and heading pages still return the summary, top companies/suppliers, and recent BOL rows.

**Why do some shipment rows lack CIF values?** ImportYeti publishes two recent-BOL views for US import profiles. The actor merges them by BOL number; fields only one view carries are filled when present and omitted otherwise.

**How current are the dates?** Customs data is published with a lag of a few weeks, so the latest shipment date usually trails today even for very active importers.
