# Wholesale Central Supplier Directory Scraper

Scrape wholesale supplier and dropshipper listings from [WholesaleCentral.com](https://www.wholesalecentral.com), the B2B directory where retailers look up wholesalers, dropshippers and closeout sellers. Browse by product category or run a keyword search across the catalog. Get company name, category, location, minimum order, and contact info (phone, address, website, social media), with no registration or login.

## What this actor does

- **Browse by category**: 56 departments in the dropdown (Apparel, Electronics, Health & Beauty, Toys & Games, Jewelry, and more), plus a free-text override for any narrower sub-category slug
- **Keyword search**: search the catalog by product or company keyword
- **Pagination**: walks the numbered result pages of a category or search until `maxItems` is reached, a page brings no new suppliers, or 40 pages have been read
- **Supplier type** (category mode only): switch to the site's Dropshippers or Closeout Suppliers department
- **Filters** (both modes): location text match, maximum minimum-order amount, keyword, featured listings only
- **Contact details**: optionally visits each supplier's page for phone number, mailing address, website URL, company description, and social media links
- **Empty fields are omitted** — no null/blank noise in the output

## Output per supplier

From the listing card (every run):

- `recordType`: always `"supplier"`
- `name`: company name
- `slug`: the supplier's identifier in its WholesaleCentral URL
- `detailUrl`, `sourceUrl`: the supplier's WholesaleCentral page (both hold the same link)
- `category`: readable name of the category page the supplier was found on (category mode only; absent in search mode)
- `supplierType`: echoes the `supplierType` you picked (`Wholesaler`, `Manufacturer`, `Importer`, `Dropshipper` or `Liquidator`); it is your selection, not a label the site gives the supplier, and it is absent for `all` and in search mode
- `location`, `city`, `state`: "City, State" as shown on the card, and its two parts
- `memberSince`: year the supplier joined the directory
- `minimumOrderUSD`: minimum order in USD (`0` means the listing says "No minimum order")
- `isFeaturedListing`: `true` when the card carries a "Featured" badge
- `websiteUrl`: the supplier's own website, when the card links to it
- `scrapedAt`: ISO 8601 UTC time the record was built

Added from the supplier's page when `fetchSupplierDetails` is on:

- `phone`: contact phone number
- `address`: mailing address as one line
- `websiteUrl`: website link from the contact panel
- `companyDescription`: the supplier's own description
- `socialMediaLinks`: links to Instagram, TikTok, Facebook, X/Twitter, Pinterest, YouTube or LinkedIn

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `byCategory` | `byCategory` (browse) or `search` (keyword) |
| `category` | string | `Apparel` | Category to browse (mode=byCategory) |
| `customCategorySlug` | string | – | Advanced: override `category` with any wholesalecentral.com category slug |
| `searchQuery` | string | `bluetooth speakers` | Keyword search (mode=search); required in that mode |
| `supplierType` | string | `all` | `all` / `wholesaler` / `manufacturer` / `importer` / `dropshipper` / `liquidator`; category mode only. `dropshipper` switches to the category's Dropshippers page (or the general Dropshippers department if none exists), `liquidator` switches to Closeout Suppliers regardless of `category`, and the other three browse the category unchanged |
| `state` | string | – | Only suppliers whose location contains this text; suppliers that show no location are kept |
| `maxMinimumOrderUSD` | int | – | Only suppliers with minimum order ≤ this amount; suppliers that don't state a minimum are kept |
| `keyword` | string | – | Only suppliers whose name (or description, when details are fetched) contains this text; works in both modes |
| `featuredOnly` | bool | `false` | Only suppliers WholesaleCentral.com badges as a "Featured" (premium/paid) listing |
| `fetchSupplierDetails` | bool | `true` | Visit each supplier's detail page for phone/address/website |
| `proxyConfiguration` | object | off | Optional Apify proxy; off by default since a direct connection is faster and more reliable against this site |
| `maxItems` | int | `20` | Hard cap on emitted records (1–500) |

### Example: apparel wholesalers in California

```json
{
  "mode": "byCategory",
  "category": "Apparel",
  "state": "California",
  "maxItems": 30
}
```

### Example: dropshippers for pet supplies

```json
{
  "mode": "byCategory",
  "category": "Pet-Supplies",
  "supplierType": "dropshipper",
  "maxItems": 20
}
```

### Example: keyword search

```json
{
  "mode": "search",
  "searchQuery": "bluetooth speakers",
  "maxMinimumOrderUSD": 200,
  "maxItems": 25
}
```

## Use cases

- **Retail/e-commerce sourcing** — find wholesale suppliers for a specific product category
- **Dropshipping** — build a shortlist of dropshipping-ready suppliers by niche
- **Liquidation buying** — find closeout/liquidation suppliers for discount resale
- **Market research** — analyze supplier density, minimum order thresholds, and geographic distribution by category
- **Lead generation** — build a contact list of wholesale suppliers for B2B outreach

## FAQ

**Does WholesaleCentral separately label suppliers as "wholesaler", "manufacturer", or "importer"?** No — the site doesn't expose that distinction as a filter. Only "Dropshippers" and "Closeout Suppliers" are structurally separate departments on the site, so those two `supplierType` values switch to a genuinely different listing set; `wholesaler`/`manufacturer`/`importer` browse the selected category unrestricted and only change the `supplierType` value written on each record. In search mode `supplierType` is ignored.

**Why do some suppliers have no `phone` or `websiteUrl`?** Not every supplier discloses a phone number or website publicly, and some detail pages only show a website link (no phone) or vice versa. The field is simply omitted rather than shown as empty.

**Why is `minimumOrderUSD` sometimes `0`?** `0` means the supplier explicitly advertises "No minimum order" — a real, meaningful value, not a placeholder. If minimum order isn't disclosed at all, the field is omitted instead.

**Does this need a login or proxy?** No login: supplier listings on WholesaleCentral.com are public. No proxy is needed either, and `proxyConfiguration` defaults to off because a direct connection has proven faster and more dependable on this site. Only enable it if you're running very high volumes and want to spread requests across IPs.

**What if a category has very few suppliers?** Some niche categories or location combinations genuinely have few listings on WholesaleCentral. The actor returns what it finds within `maxItems` and the 40-page limit. An empty dataset means nothing matched your filters, or the category or search page couldn't be loaded; the run's status message says which.

**Why does a run occasionally return suppliers without `phone`/`address`/`companyDescription`/`socialMediaLinks` even with `fetchSupplierDetails` on?** Some suppliers simply don't publish them. Ads on WholesaleCentral.com also sometimes interfere with loading a supplier's contact panel. When that keeps failing across many suppliers, the actor stops visiting supplier pages for the rest of the run, so the remaining suppliers arrive with listing-card fields only (name, category, location, minimum order). That also means a `keyword` can then only match supplier names. Re-running later usually restores full details.

**Is this affiliated with WholesaleCentral.com?** No. This is an independent tool that reads the directory's public supplier pages; it is not run or endorsed by WholesaleCentral.com.
