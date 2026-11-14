# Carousell Marketplace Listing Search Across 8 Markets

Carousell runs a separate marketplace for each country it operates in, each with its own listings, currency and sellers. This actor searches one of those eight markets by keyword or category, or fetches specific listing URLs directly, and returns each item's price, condition, seller and image.

## What this actor does

- Searches listings by keyword in a chosen country market
- Browses listings within a specific category
- Fetches full details for one or more direct listing URLs
- Browses a market's listings with no keyword (`nearbyListings` — see FAQ for how this differs from `search`)
- Filters by item condition and price range, and sorts by relevance, recency or price
- Omits a field from a record when Carousell's own listing didn't provide it

## Output per listing

| Field | Description |
|---|---|
| `listingId` | Carousell listing ID |
| `title` | Item title |
| `price` | Price as a number, when Carousell provides a parsed amount |
| `priceText` | Price as displayed, when no numeric value could be parsed |
| `currency` | Currency code for the market (e.g. `SGD`, `MYR`) |
| `condition` | Item condition, e.g. `New` or `Used` |
| `category` | Item category |
| `seller` | Seller username |
| `sellerRating` | Seller's rating score, when available |
| `location` | Meetup or listing location |
| `country` | Country market searched |
| `imageUrl` | First listing image URL |
| `listingUrl` | Direct link to the listing |
| `listedAt` | When the listing was posted |
| `scrapedAt` | UTC timestamp of when the record was captured |
| `mode` | Which mode produced this record |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string (select) | `search` | `search`, `searchByCategory`, `listingDetails`, or `nearbyListings` |
| `query` | string | `iPhone` | Keyword to search for (mode `search`) |
| `country` | string (select) | `singapore` | `singapore`, `malaysia`, `philippines`, `indonesia`, `taiwan`, `hong_kong`, `australia`, or `new_zealand` |
| `category` | string | – | Category slug to browse (mode `searchByCategory`) |
| `listingUrls` | array | `[]` | Carousell listing URLs to fetch directly (mode `listingDetails`) |
| `sortBy` | string (select) | `relevance` | `relevance`, `recent`, `price_asc`, or `price_desc` |
| `condition` | string (select) | `all` | `all`, `new`, or `used` |
| `priceMin` | integer | – | Minimum price in the market's local currency |
| `priceMax` | integer | – | Maximum price in the market's local currency |
| `maxItems` | integer | 20 | Maximum number of listings to return (1–1000) |

### Example: search used phones in Singapore

```json
{
  "mode": "search",
  "query": "iPhone",
  "country": "singapore",
  "condition": "used",
  "maxItems": 20
}
```

### Example: browse a category sorted by price

```json
{
  "mode": "searchByCategory",
  "category": "electronics",
  "country": "malaysia",
  "sortBy": "price_asc",
  "maxItems": 50
}
```

### Example: fetch specific listings

```json
{
  "mode": "listingDetails",
  "listingUrls": ["https://www.carousell.sg/p/iphone-14-pro-max-256gb-98765432"]
}
```

## Use cases

- **Price comparison** — compare asking prices for the same item across different Carousell markets
- **Resale market research** — track condition and pricing trends in a category over time
- **Sourcing and arbitrage** — find underpriced listings in a category or price band
- **Seller monitoring** — pull a seller's listings via direct URLs to track their current inventory
- **Classifieds aggregation** — feed structured Carousell listings into a broader marketplace search tool

## FAQ

**Is this affiliated with Carousell?**
No. This is an independent data extraction tool and has no connection to Carousell Pte. Ltd.

**Do I need a Carousell account to run this?**
No — listings are publicly accessible without login.

**Which markets are supported?**
Eight: Singapore, Malaysia, the Philippines, Indonesia, Taiwan, Hong Kong, Australia, and New Zealand, each with its own domain and currency.

**Why is `price` sometimes missing but `priceText` present instead?**
Some listings show a price in a form the actor can't parse into a clean number (e.g. "Swap" or "Contact for price"); in that case the raw displayed text is kept in `priceText` instead of a fabricated number.

**What's the difference between `search` and `searchByCategory`?**
`search` matches a free-text keyword against listings; `searchByCategory` browses a specific category slug without requiring a keyword.

**Can I scrape a specific seller's listings?**
Not directly by username — but if you have the listing URLs, `listingDetails` mode will fetch each one's full details.

**Why might `sellerRating` be absent from a listing?**
Not every seller has accumulated a rating yet; the field is left out rather than shown as zero.

**What does `nearbyListings` do differently from `search`?**
It runs the same country-wide browse with no keyword. There's no location/coordinates input, so it doesn't filter by physical distance — use `country` (and `category`, if relevant) to scope the results.
