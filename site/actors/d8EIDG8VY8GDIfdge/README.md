# Google Workspace Marketplace App Search & Category Browser

Pull app listings from the [Google Workspace Marketplace](https://workspace.google.com/marketplace), with no Google account, API key, or proxy needed. Search by keyword, browse an entire category, or fetch full details for specific app IDs you already know.

## What this actor does

- **Keyword search** across the whole marketplace, enriched with full listing detail
- **Category browsing** across 26 categories and subcategories (popular apps, top rated, business tools, productivity, education, and more)
- **Direct app lookup** by numeric app ID, with no practical limit on how many you can fetch
- **Multi-language results** — choose the language the listing page is read in
- Fields with no value for a given app (e.g. no reviews yet, unlisted pricing) are omitted rather than returned as `null`

## Output per app

- `appId` — numeric app identifier
- `name` — app display name
- `developer` — publisher/developer name
- `shortDescription` — one-line app summary
- `description` — full app description
- `rating` — average star rating, 0–5
- `reviewCount` — total number of ratings
- `installCount` — install count, when the listing publishes one
- `pricingModel` — `Free`, `Freemium`, or `Paid`
- `categories` — official Marketplace categories the app belongs to
- `worksWith` — Google products the app integrates with (e.g. Google Docs, Google Drive)
- `lastUpdated` — date of the listing's most recent update
- `appUrl` — direct link to the app's Marketplace listing
- `iconUrl` — app icon image, hosted by Google
- `recordType` — always `"workspace_app"`
- `scrapedAt` — ISO timestamp of the scrape

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search`, `byCategory`, or `byAppId` |
| `searchQuery` | string | `mail merge` | Keyword to search for (mode=search) |
| `category` | string | `popular-apps` | Category path to browse (mode=byCategory) |
| `appIds` | array | `[]` | Numeric app IDs to fetch (mode=byAppId) |
| `maxItems` | integer | `50` | Maximum records to emit (1–200) |
| `language` | string | `en` | Language for search/category pages |

### Example: keyword search

```json
{
  "mode": "search",
  "searchQuery": "mail merge",
  "maxItems": 30
}
```

### Example: browse a category

```json
{
  "mode": "byCategory",
  "category": "business-tools/sales-and-crm",
  "maxItems": 50
}
```

### Example: fetch specific apps by ID

```json
{
  "mode": "byAppId",
  "appIds": ["7081045131", "218858140275"]
}
```

### Example: search results in Spanish

```json
{
  "mode": "search",
  "searchQuery": "crm",
  "language": "es",
  "maxItems": 20
}
```

## Use cases

- **IT and procurement evaluation** — compare pricing models, ratings and Google-product compatibility before approving an app
- **Competitive research** — track where your app or a competitor's ranks within a category
- **Market mapping** — enumerate every app in a category (e.g. all CRM or accounting tools) for a landscape report
- **Vendor and partner discovery** — find developers building for a specific Workspace product
- **App directory sites** — populate a curated listing page with live Marketplace data

## FAQ

**Does this need a Google account or API key?** No — the Marketplace is publicly browsable, and this actor reads it without any authentication, cookies, or proxy.

**How many apps can one run return?** Search and category pages return up to 100 apps per query (the marketplace's own natural limit); `maxItems` controls how many of those are emitted. `byAppId` mode has no such limit since it fetches exact listings.

**What does `pricingModel` mean?** `Free` means no cost at all; `Freemium` covers listings marked "free with paid features" or offering a free trial; `Paid` means payment is required to use the app.

**What is `worksWith`?** The Google products the app integrates with (e.g. Google Drive, Gmail, Sheets, Slides, Docs, Calendar, Forms, Chat), taken directly from the listing.

**Why might `rating`, `reviewCount`, or `installCount` be missing?** New or lightly used listings may not have published figures yet; the field is omitted rather than shown as zero.

**Are reviews included in this actor's output?** No — this actor covers app listing data only; review text is out of scope here.

**Are the icon URLs publicly accessible?** Yes — icons are hosted at `lh3.googleusercontent.com` and load without authentication.

**Is this affiliated with Google?** No — this is an independent actor reading the public Google Workspace Marketplace; it is not operated by or affiliated with Google.
