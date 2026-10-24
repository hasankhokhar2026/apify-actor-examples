# LinkedIn Ad Library Keyword & Advertiser Scraper

Search the **public LinkedIn Ad Library** (`linkedin.com/ad-library`) by keyword, advertiser, country, or date range. Get headline, body copy, advertiser info, media URLs, and CTA for the ads on each search's results page — with optional detail-page enrichment for the paying entity, canonical advertiser URL, and full body text.

**No login or LinkedIn account required.** The Ad Library is fully public and the actor runs without cookies.

## What this actor does

- Searches the Ad Library by keyword, advertiser name, country, or a date range, or accepts a pre-built Ad Library URL directly
- Returns each ad's headline, body copy, advertiser info, media URLs, and call-to-action, from the first results page of every search (no further pages are loaded)
- Optionally enriches each ad from its detail page with the paying entity, canonical advertiser URL, and full body text
- Date windows of the last 30 days, 90 days or year, or a custom range — inactive ads included where LinkedIn still lists them
- Combines every keyword × advertiser combination you provide, scoped by your country and date filters, and removes duplicate ads across searches
- Empty fields are dropped from each record

## Output per ad

For each ad on the search results page:

| Field | Description |
| --- | --- |
| `ad_id` | LinkedIn ad / creative identifier |
| `ad_url` | Direct LinkedIn Ad Library detail URL |
| `ad_format` | `image` / `video` / `carousel` / `document` / `text` / `inmail` (with enrichment, LinkedIn's own lower-cased format label from the detail page) |
| `advertiser_name` | Sponsoring entity (company or person) |
| `advertiser_logo` | Logo image URL |
| `advertiser_tagline` | Sponsoring entity tagline (e.g. "Chief AI Officer") |
| `advertiser_url` | LinkedIn company page URL |
| `body_text` | Ad commentary / body copy as shown in the preview |
| `headline` | Ad headline copy |
| `cta_text` | Call-to-action text (e.g. "Learn more", "Apply now") |
| `cta_url` | Click-through destination URL |
| `media_urls` | All image / video / document / carousel slide URLs |
| `scraped_at` | ISO 8601 UTC timestamp of extraction |

When `enrichWithDetailPage=true` is enabled, additional fields are pulled from each ad's detail page:

| Field | Description |
| --- | --- |
| `paid_for_by` | Entity that paid for the ad (often differs from the advertiser) |
| `body_text_full` | Full body / commentary text from the detail page (sometimes longer than the preview) |
| `advertiser_url` | Canonical advertiser URL — replaces the search-result URL when the detail page has one |
| `ad_format` | Format label from the detail page, when present (replaces the search-result value) |

## Input

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `searchTerms` | Array | `[]` | Keyword search queries (e.g. `"AI"`, `"remote work"`). Matched against ad copy and advertiser name. |
| `advertisers` | Array | `[]` | Advertiser / company names (e.g. `"Microsoft"`, `"Salesforce"`). |
| `countries` | Array | `[]` | ISO-3166-1 alpha-2 country codes (e.g. `"US"`, `"GB"`, `"IN"`). |
| `dateOption` | Enum | `last-30-days` | `last-30-days` / `last-90-days` / `last-year` / `custom`. The 30-day default applies to every keyword/advertiser/country search unless you change it (not to `directUrls`) |
| `dateFrom` | String | — | YYYY-MM-DD, only used when `dateOption=custom` (with `custom` and no dates, no date filter is sent). |
| `dateTo` | String | — | YYYY-MM-DD, only used when `dateOption=custom`. |
| `directUrls` | Array | `[]` | Pre-built Ad Library URLs — paste directly if you already configured filters in the LinkedIn UI. Fetched as-is, before the keyword/advertiser searches. |
| `maxResults` | Integer | `50` | Maximum ads to return across all queries (1–1000). |
| `enrichWithDetailPage` | Boolean | `false` | Open each ad's detail page to add `paid_for_by`, full body text, and canonical advertiser URL. Slower but more complete. |
| `proxy` | Object | `{"useApifyProxy": true}` | Defaults to free Apify Proxy (no residential group needed). |

You can combine inputs freely — every keyword × advertiser combination is tried, scoped by your country and date filters. With only `countries` (or nothing at all), a single search filtered by country and the date window is run.

### Example input — keyword search, fast

```json
{
  "searchTerms": ["AI", "machine learning"],
  "countries": ["US"],
  "dateOption": "last-30-days",
  "maxResults": 50
}
```

### Example input — advertiser focus, full enrichment

```json
{
  "advertisers": ["Microsoft", "Salesforce"],
  "dateOption": "last-90-days",
  "maxResults": 100,
  "enrichWithDetailPage": true
}
```

### Example input — direct Ad Library URL

```json
{
  "directUrls": [
    { "url": "https://www.linkedin.com/ad-library/search?keyword=cloud&country=US" }
  ]
}
```

### Example input — custom date range

```json
{
  "searchTerms": ["recruiting"],
  "dateOption": "custom",
  "dateFrom": "2026-01-01",
  "dateTo": "2026-03-31"
}
```

## Example output

```json
{
  "ad_id": "12345678",
  "ad_url": "https://www.linkedin.com/ad-library/detail/12345678",
  "ad_format": "video",
  "advertiser_name": "Anthropic",
  "advertiser_url": "https://www.linkedin.com/company/anthropicresearch",
  "advertiser_logo": "https://media.licdn.com/dms/image/.../company-logo.jpg",
  "headline": "Build with Claude",
  "body_text": "Ship faster with the Claude API. Trusted by 1000s of developers.",
  "cta_text": "Learn more",
  "cta_url": "https://www.anthropic.com/api",
  "media_urls": ["https://media.licdn.com/dms/image/.../ad-creative.jpg"],
  "paid_for_by": "Anthropic PBC",
  "body_text_full": "Ship faster with the Claude API. Trusted by 1000s of developers building agents, RAG pipelines, coding assistants, and more.",
  "scraped_at": "2026-05-05T13:42:18Z"
}
```

## Use cases

- **Competitive intelligence** — Monitor what competitors are running, in which countries, with what messaging.
- **Lead generation** — Build prospect lists of companies actively spending on LinkedIn ads in your category.
- **Brand monitoring** — Track every ad featuring your brand, products, or trademarks.
- **Creative research** — Mine patterns in headline length, CTA choice, and media format across an industry.
- **Geographic analysis** — Compare ad strategies across markets by combining country + advertiser filters.
- **Compliance / due diligence** — Verify what an advertiser is publicly claiming on LinkedIn (`paid_for_by` shows the actual paying entity).

## FAQ

**Do I need a LinkedIn account?**
No. The Ad Library is fully public — anyone can browse it without logging in. The actor makes the same anonymous requests the public web UI does.

**Do I need a proxy?**
No. The default Apify Proxy (no residential group required) works out of the box.

**What's the difference between `searchTerms` and `advertisers`?**
- `searchTerms` matches ad copy AND advertiser name (broad keyword search).
- `advertisers` matches only the advertiser display name (narrow company-targeted search).

Combine them when you want to find a specific company's ads about a specific topic.

**When should I enable `enrichWithDetailPage`?**
Whenever you need `paid_for_by` (regulatory / compliance use cases), the canonical advertiser URL, or the full body text. It opens one extra page per ad, so runs take noticeably longer — leave it off for fast list pulls and turn it on for high-value reporting.

**What does `dateOption=custom` enable?**
A user-defined `dateFrom` / `dateTo` window. LinkedIn returns ads served at any time during that window. Without `custom`, the actor uses LinkedIn's predefined buckets (last 30 / 90 / 365 days).

**How many ads can I scrape per run?**
Each search contributes only the ads on its first results page; the actor doesn't load further pages. To collect more, add more keywords, advertisers or direct URLs (each becomes its own search) and raise `maxResults` (up to 1000), or split the work into separate runs by keyword / country.

**What if a query returns no ads?**
The actor moves on to the rest. If no ads are collected at all, the dataset gets a single status record instead: `type: "linkedin_ads_blocked"`, `reason` (`upstream_error`, or `crash` after an unexpected error), `message`, `scrapedAt`, and for `upstream_error` up to 10 `requestedUrls`. Filter on `type` to separate it from ad records.

**Why are impression counts or targeting facets not in the output?**
LinkedIn loads those numbers via a separate request after the page renders, which this actor's static-page extraction doesn't execute, so they're never included in any record — not even for DSA-regulated ads that show them on linkedin.com itself.

**How current is the data?**
Live — every run hits LinkedIn at request time. Schedule the actor for daily / hourly refreshes.

**Can I scrape closed / paused ads?**
Yes, as long as LinkedIn still lists them in the Ad Library for your date window; pick `last-year` or a `custom` range to reach older ones.

**Is this affiliated with LinkedIn?**
No. This is an independent, third-party actor that reads LinkedIn's public Ad Library; it isn't affiliated with or endorsed by LinkedIn Corporation.

## Limitations

- Only ads visible in the public Ad Library are scraped — no access to LinkedIn's full Campaign Manager.
- Impression counts and targeting facets are never included: LinkedIn loads them via a separate request after the page renders, which this actor's extraction doesn't execute.
- Only the first results page of each search is read.
- LinkedIn may rate-limit unusually fast or large requests; spread very large pulls across multiple runs rather than one very large `maxResults`.
