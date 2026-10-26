# iOS App Store Deep Reviews & App Intelligence

Collect structured data from the iOS App Store: app metadata, customer reviews with developer replies, publisher catalogs, and top-chart rankings. Everything runs without an Apple account, cookie, API key, or proxy setup.

## What this actor does

- **Five modes:** `search`, `lookup`, `reviews`, `developer`, `charts`
- **Deep reviews:** pages through Apple's own App Store review API at 20 reviews per request, well past the 500-review RSS limit, and falls back to RSS when needed
- **Developer replies:** kept when Apple exposes them for a review
- **Rich app data:** privacy labels, rating histogram, version history, subtitle, support URL, requirements, and chart position
- **62 storefronts:** pricing, availability, charts, and review language follow the selected country
- **Backward compatible:** old saved inputs with `searchTerms`, `appIds`, `startUrls`, `maxResults`, `includeReviews`, or `reviewPages` still run; the legacy fields are accepted in code and are no longer shown in the input form
- **No empty values:** every record is cleaned recursively; fields Apple does not provide are omitted rather than returned as `null`, `""`, or `[]`

## Modes

| Mode | What it returns | Notes |
|---|---|---|
| `search` | One row per app for each keyword | Up to 200 apps per term (Apple's cap), de-duplicated across terms, with `searchTerm` and `searchRank` |
| `lookup` | One row per app | Accepts numeric IDs, bundle IDs, app URLs, and developer URLs; developer URLs expand to the publisher catalog |
| `reviews` | One row per review | Deep pagination plus RSS enrichment for version, reviewer URL, and helpful votes |
| `developer` | One row per app | Resolves a developer ID, developer URL, or publisher name; up to 200 apps per publisher |
| `charts` | One row per chart entry | Top free, paid, grossing, iPad, and Mac charts, with `chartPosition` |

## Output per app

Identity and storefront:

- `id`, `appId` — numeric App Store ID
- `bundleId`, `name`, `subtitle`
- `url`, `sourceUrl` — App Store page
- `country`, `language`

Developer:

- `developer`, `developerId`, `developerUrl`, `developerWebsite`
- `sellerInfo` — EU/EEA trader details when Apple publishes them

Pricing and ratings:

- `price`, `formattedPrice`, `currency`, `isFree`
- `rating`, `ratingCount`
- `currentVersionRating`, `currentVersionRatingCount`
- `ratingHistogram` — 1★ through 5★ counts

Content and release data:

- `description`, `releaseNotes`, `version`
- `releaseDate`, `lastUpdated`
- `category`, `genres`, `contentRating`, `ageRating`, `advisories`
- `minimumOs`, `requirements`
- `fileSize`, `size` — bytes
- `icon`, `screenshots`, `ipadScreenshots`
- `languages` — iTunes language codes
- `languageNames` — full language names from the App Store detail page

Trust and depth:

- `privacy` — App Store privacy labels as `{type, category, dataTypes}` rows, plus purposes where Apple supplies them
- `privacyPolicyUrl`, `supportUrl`
- `versionHistory` — up to 25 releases, newest first
- `chartPosition`, `chartType` — when Apple reports a current chart position, and for chart runs
- `searchTerm`, `searchRank` — search runs only
- `recordType: "app"`, `scrapedAt`

Rich fields appear only when `includeDetails` is on and Apple exposes the data. A field Apple genuinely lacks for a given app is omitted.

## Output per review

- `id` — Apple review ID
- `appId`
- `country`
- `rating` — 1 to 5
- `title`, `text`
- `author`, `authorUrl`
- `date` — Apple's review timestamp
- `version` — reviewed release, when RSS exposes it
- `voteCount`, `voteSum` — helpfulness votes, when RSS exposes them
- `isEdited`
- `developerResponse` — `{body, date}` when the developer replied and `includeDeveloperResponses` is on
- `sort`, `position`
- `sourceUrl`, `recordType: "review"`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search`, `lookup`, `reviews`, `developer`, or `charts` |
| `searchTerms` | array | `["calculator"]` in the daily prefill | Keywords for `search` |
| `appIds` | array | – | Numeric IDs, bundle IDs, app URLs, or developer URLs for `lookup`/`reviews` |
| `startUrls` | array | – | App Store app or developer URLs for `lookup`/`reviews` |
| `developerId` | string | – | Apple artist ID or developer URL for `developer` |
| `developerName` | string | – | Publisher name to resolve for `developer` |
| `country` | string | `us` | One of 62 App Store storefronts |
| `language` | string | `en-US` | Storefront language |
| `maxItems` | integer | `100` | Hard row cap for the whole run (1–5000) |
| `maxReviewsPerApp` | integer | `200` | Review cap per app (1–50000) |
| `reviewSort` | string | `recent` | `recent` or `helpful` |
| `includeDeveloperResponses` | boolean | `true` | Keep developer replies when present |
| `includeDetails` | boolean | `true` | Add privacy, version history, histogram, support URL, and other rich detail |
| `chartType` | string | `top-free` | `top-free`, `top-paid`, `top-grossing`, `top-free-ipad`, `top-paid-ipad`, or `top-free-mac` |
| `proxyConfiguration` | object | disabled | Optional proxy; the actor works without one |

The daily test prefill runs `search` for `calculator` in the US storefront, `maxItems: 3`, and `includeDetails: false`. That is three App Store search results from a single iTunes request.

### Example: search with rich details

```json
{
  "mode": "search",
  "searchTerms": ["photo editor", "note taking"],
  "country": "us",
  "maxItems": 50,
  "includeDetails": true
}
```

### Example: look up apps by ID, bundle ID, and URL

```json
{
  "mode": "lookup",
  "appIds": ["544007664", "com.google.ios.youtube"],
  "startUrls": [
    {"url": "https://apps.apple.com/gb/app/things-3/id904280696"}
  ],
  "country": "gb"
}
```

### Example: deep reviews with developer replies

```json
{
  "mode": "reviews",
  "appIds": ["618783545"],
  "country": "us",
  "maxReviewsPerApp": 2000,
  "reviewSort": "recent",
  "includeDeveloperResponses": true
}
```

### Example: a developer's catalog

```json
{
  "mode": "developer",
  "developerId": "281956209",
  "country": "us",
  "maxItems": 200
}
```

### Example: top free chart

```json
{
  "mode": "charts",
  "chartType": "top-free",
  "country": "jp",
  "maxItems": 100
}
```

## What is available and what is not

- **Search** returns up to 200 apps per term. Apple does not paginate search results.
- **RSS reviews** are capped at 10 pages, 50 reviews per page, so 500 reviews per app and country.
- **Deep reviews** use Apple's same-origin App Store API at 20 reviews per request. Pagination stops when Apple's corpus ends (HTTP 404), when the per-app cap is reached, or when `maxItems` is reached.
- **Developer responses** exist only on apps where the developer replied. They are not available for every review or every app.
- **Written reviews are not the same as ratings.** `ratingCount` counts star ratings; the actor reports only the review rows it actually collected.
- **Version, reviewer URL, and helpful votes** come from the RSS feed and therefore cover at most the first 500 reviews per app and country.
- **In-app purchase catalogs, autocomplete, and Apple TV screenshots** are not exposed by the cookieless routes used here, so they are not emitted.
- **Apple TV** apps are outside this actor's scope; it reads iPhone, iPad, and Mac listings.

## Reliability

- Requests to `apps.apple.com` are serialized and throttled. HTTP 429 and 5xx responses retry with exponential backoff and `Retry-After` support.
- If a rich detail request fails, the app still ships with its iTunes metadata and the run reports a warning.
- If every request is blocked or Apple is unavailable, the run fails with an explicit message instead of returning an empty dataset.
- Duplicate apps are removed by App Store ID. Duplicate reviews are removed by review ID.
- Partial runs keep the rows that succeeded and report how many warnings occurred.

## FAQ

**Do I need an Apple Developer account or API key?**
No. The actor reads Apple's public App Store listings, review feeds, and the same-origin web API used by the App Store website.

**How do I find an app ID?**
Open the app in a browser. The number after `/id` is the App Store ID, for example `https://apps.apple.com/us/app/youtube/id544007664` gives `544007664`.

**Can I pass bundle IDs?**
Yes. Put a bundle ID such as `com.google.ios.youtube` in `appIds`. Bundle IDs also work in `lookup` and `reviews` modes.

**Why do some apps have fewer reviews than requested?**
Apple returns only the reviews that exist for that app in that storefront. The deep route can page far past the 500-review RSS limit for large apps, but a small app may have only a handful. RSS is capped at 500.

**Why are developer replies missing?**
Apple exposes a reply only when the developer actually wrote one. Apps with no reply history return no `developerResponse` field.

**Why is `version` missing from a deep review?**
The deep review API does not include the reviewed version. The actor fills it from RSS for the first 500 reviews; older reviews have no version.

**Does the country change results?**
Yes. Country controls pricing and currency, app availability, chart contents, and the language of reviews.

**Can I run several countries in one run?**
One country per run. Run the actor once per storefront and combine the datasets.

**Is this affiliated with Apple?**
No. This is an independent third-party actor that reads publicly available App Store data. It is not affiliated with or endorsed by Apple Inc.
