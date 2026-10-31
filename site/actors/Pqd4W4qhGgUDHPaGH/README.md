# Facebook Ad Library Byline & Advertiser Ad Finder

Start from whoever is actually running the ad — a Page ID, a direct Ad Library ID, or the "Paid for by" name printed on a political disclaimer — and this actor hands back every matching record from Meta's public Ad Library, free-text keyword search included. Each record keeps the creative copy, media, destination link, run dates, platform split, and, when Meta discloses it for political/issue/EU ads, spend and impression figures.

## What this actor does

- Looks up ads four different ways in one run: by advertiser Page ID, by a direct Ad ID you already have, by the "Paid for by" byline on a political disclaimer, or by free-text keyword
- Narrows results with country, content-language, active/inactive status, ad category (political & issue, housing, employment, credit), media type, a date range, and a sort order
- Flags reused creative via `collation_count`, Meta's own count of how many ad variants share one underlying creative/text pairing
- Carries spend, impressions and reach only where Meta actually publishes them — political, issue and EU-eligible ads — leaving the field out entirely for ordinary commercial ads rather than guessing
- Drops any field the Ad Library didn't return for a given ad, so records never carry empty placeholders

## Output per ad

- `ad_id` — the ad's unique Ad Library archive ID
- `page_name` — the advertiser Page running the ad
- `ad_text` — the creative's written copy
- `ad_snapshot_url` — permalink back to this ad on the Ad Library
- `start_date` / `end_date` — the run window Meta reports
- `status` — `active`, `inactive`, or `unknown`
- `publisher_platform` — placements such as Facebook, Instagram, Messenger, Audience Network, Threads
- `media_type` / `media_url` — the creative format (image, video, meme, none) and a link to it
- `cta_text` — the button label shown on the ad
- `link_url` — where the ad's call-to-action sends visitors
- `collation_count` — how many variants Meta groups under this one creative
- `page_like_count` / `page_categories` — the advertiser Page's follower count and listed categories
- `gated_type` — whether the ad qualifies for Meta's political/EU transparency disclosures
- `disclaimer_label` / `byline` — the disclaimer type and funding-entity name shown on political/issue ads
- `spend` / `impressions` / `reach_estimate` / `currency` — published only for political, issue and EU-eligible ads
- `regional_regulation_data` — jurisdiction-specific flags, e.g. financial-services or anti-scam delivery limits
- `contains_digital_created_media` — whether Meta's AI-generated-content label applies to this ad
- `search_term` — which of your inputs (keyword, Page ID, Ad ID, byline) surfaced this record
- `scraped_at` — timestamp of the run that collected the record

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchTerms` | array | – | Free-text keywords or advertiser names to look up |
| `pageIds` | array | – | One or more Facebook Page IDs; returns every ad that Page is running |
| `adIds` | array | – | Specific Ad Library IDs to fetch directly |
| `bylines` | array | – | Funding-entity or committee names printed on "Paid for by" disclaimers |
| `country` | string | `ALL` | A single country code (e.g. `US`, `GB`) or `ALL` |
| `countries` | array | – | Country codes to try; only the first entry is honored |
| `contentLanguages` | array | – | ISO language codes restricting the ad's content language |
| `adActiveStatus` | string | `active` | `all`, `active`, or `inactive` |
| `adType` | string | `all` | `all`, `political_and_issue_ads`, `housing`, `employment`, or `credit` |
| `mediaType` | string | `all` | `all`, `image`, `video`, `meme`, or `none` |
| `startDate` / `endDate` | string | – | Restrict results to a run-date window (YYYY-MM-DD) |
| `sortBy` | string | `relevance` | `relevance` or `total_impressions` |
| `resultsPerSearch` | integer | `50` | Cap per lookup — term, Page, ad, or byline (1–500) |
| `cookies` | string | – | Optional logged-in Facebook cookies, for when a region gates search behind a login wall |

Supply at least one of `searchTerms`, `pageIds`, `adIds`, or `bylines`.

### Example: ads from one advertiser Page

```json
{
    "pageIds": ["15087023444"],
    "country": "US",
    "resultsPerSearch": 100
}
```

### Example: who's funding a political message

```json
{
    "bylines": ["RNC"],
    "adType": "political_and_issue_ads",
    "country": "US",
    "resultsPerSearch": 50
}
```

### Example: brand keyword, image ads only

```json
{
    "searchTerms": ["patagonia", "north face"],
    "mediaType": "image",
    "country": "US",
    "resultsPerSearch": 25
}
```

### Example: look up a known ad by ID

```json
{
    "adIds": ["987654321012345"],
    "resultsPerSearch": 1
}
```

## Use cases

- **Advertiser auditing** — pull every live ad from a single Page ID to see its full current rotation
- **Creative-reuse tracking** — sort by `collation_count` to spot which ad variants a brand is scaling hardest
- **Campaign-finance monitoring** — resolve a "Paid for by" byline back to every ad it's running behind
- **Swipe-file building** — collect real running creative, copy and landing pages for a pitch deck or inspiration board
- **Spend transparency checks** — compare published spend/impression ranges across political advertisers in one country
- **Known-ad lookups** — fetch a specific ad's full record once you already have its Ad Library ID

## FAQ

**Who runs this actor — is it part of Meta?** No. It's an independent tool reading the same public Ad Library data anyone can browse at facebook.com/ads/library.

**Will search work without a login?** Yes, by default. A handful of regions occasionally require a logged-in session to return results; the optional `cookies` input covers that case.

**How do I pick between the four lookup modes?** Use `pageIds` when you know the advertiser, `adIds` when you already have a specific ad's archive ID, `bylines` when you're chasing a funding-entity disclaimer, and `searchTerms` for everything else.

**Some ads skip spend and impressions — why?** Meta only publishes those figures for political, issue, and EU-regulated ads. Commercial ads never get a fabricated number here; the fields are simply absent.

**Can one run cover several countries?** Not server-side — Meta's Ad Library only accepts one country per request, so if `countries` holds more than one entry, only the first is used.

**What's the point of byline search specifically?** It matches the funding-entity name printed in a political/issue ad's disclaimer, which is often different from the advertiser Page name — handy for tracing who's actually paying.

**How should I read `collation_count`?** It's Meta's own tally of ad variants sharing one creative and text — a fast way to see how aggressively an ad is being scaled across variations.

**How far back can I search?** Active ads are always available; political and social-issue ads carry roughly seven years of history. Results reflect whatever Meta is currently serving for your query.

**Can I combine lookup modes in a single run?** Yes — set `searchTerms`, `pageIds`, `adIds` and `bylines` together and each is queried independently, with everything merged into one output dataset.
