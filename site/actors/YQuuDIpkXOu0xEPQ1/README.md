# DoorDash Store Menu & FAQ Data Finder

Find restaurant details and complete menus from **DoorDash** store pages — name, address, cuisine breadcrumbs, menu sections with item names, descriptions and prices, and the store's published FAQ. Provide one or more store URLs and get a flat, fully-populated record back for each.

## What this actor does

- **Full menu extraction** — every section and item, with name, description, and price
- **FAQ extraction** — questions and answers published on the restaurant's store page
- **Breadcrumb extraction** — cuisine type and neighborhood, as shown on the page
- **Deduplication** — the same store ID is only emitted once per run, even if its URL is listed twice
- **Always-populated fields** — every field is present with a typed default (empty string, `0`, or `[]`) rather than `null`, so downstream code never needs to check for missing keys

## Output per restaurant

- `storeId` — DoorDash store ID (from the URL)
- `storeName`, `storeUrl`
- `title`, `description` — the page's title and meta description
- `address`, `city`, `state`
- `breadcrumbs[]` — page breadcrumb trail, e.g. `["Home", "Boston", "Burgers", "UBURGER"]` (last is the restaurant name, second-to-last is typically the cuisine)
- `menuSections[]` — section names, e.g. `["Salads", "Burgers", "Drinks"]`
- `menuSectionCount`
- `menuItems[]` — flat list of `{section, name, description, price}`
- `menuItemCount`
- `faq[]` — list of `{question, answer}` pairs
- `faqCount`
- `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `storeUrls` | array | – | DoorDash store URLs to scrape |
| `maxItems` | integer | `10` | Maximum restaurants to scrape across all URLs (1–100) |

### Example: scrape a list of specific stores

```json
{
  "storeUrls": [
    "https://www.doordash.com/store/15034",
    "https://www.doordash.com/store/6422"
  ],
  "maxItems": 10
}
```

### Example: a single store

```json
{
  "storeUrls": ["https://www.doordash.com/store/15034"],
  "maxItems": 1
}
```

## Use cases

- **Competitor menu intelligence** — track pricing and item offerings for named restaurants over time
- **Cuisine analysis** — group restaurants by their breadcrumb cuisine tag
- **Menu engineering research** — compare which sections and items are common across similar restaurants
- **Franchise auditing** — pull menus for every location of a chain by store URL
- **Customer support/FAQ research** — collect how restaurants answer common ordering questions

## FAQ

**Why doesn't this return individual customer reviews?** DoorDash store pages no longer expose individual customer reviews — only aggregate signals surfaced elsewhere on the page. This actor extracts everything the store page actually publishes: menu, address, FAQ, and breadcrumbs.

**How do I find a store's URL?** Visit the restaurant on doordash.com and copy its page URL, in the form `https://www.doordash.com/store/<id>`.

**Can I get prices as numbers instead of strings?** Prices are returned as strings (e.g. `"$8.50"`) because DoorDash sometimes shows ranges or non-numeric formatting. Convert them downstream if you need numeric values.

**Will this work for every DoorDash store?** It works for any restaurant with a published menu. Some stores — closed restaurants, catering/aggregator brands, or convenience-store and grocery listings — don't expose a structured menu; for those, this actor still returns the restaurant's info, FAQ, breadcrumbs, and address, but `menuSections` and `menuItems` come back empty.

**Does this include duplicate stores if I list the same URL twice?** No — each store ID is only emitted once per run even if its URL appears more than once in `storeUrls`.

**Is this affiliated with DoorDash?** No. This is an independent third-party actor that reads DoorDash's public store pages.
