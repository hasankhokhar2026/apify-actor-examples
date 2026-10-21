# Facebook Business Page Recommendation & Review Scraper

Get **Facebook business page reviews** by direct URL, business name search, or Facebook Page ID — no login or cookies required. Returns review text, Recommended/Not Recommended status, author details, reaction breakdowns, structured recommendation tags, business owner replies, and page-level aggregate stats like follower count and overall recommendation percentage.

## What this actor does

- Scrapes reviews from any **public Facebook business page** — restaurants, hotels, retailers, airlines, and services
- **Three input modes**: paste a page or `/reviews` URL, search by business name + city, or supply a Facebook Page ID (numeric) or page username
- **Filters results** by date range, recommendation status (Recommended / Not Recommended), or keyword in the review text
- Extracts **review photos**, **structured recommendation tags** (e.g. "Outdoor dining", "Fast delivery"), **reaction breakdowns** (Like/Love/Wow/Haha/Sad/Angry/Care counts), and **top comments including business/owner replies**
- Attaches **page details** to each review — page name and ID, plus follower count, total review count and recommendation percentage when Facebook exposes them
- Empty/unavailable fields are omitted from each record rather than returned as `null`

## Output

One record per review. Fields are only present when Facebook actually has that data — see the FAQ for why some fields (like `reviewPhotos`) are frequently absent.

| Field | Example |
|-------|---------|
| `reviewId` | `"UzpfSTEwMDAy..."` |
| `text` | `"Amazing food and great service!"` |
| `isRecommended` | `true` |
| `reviewTags` | `["Outdoor dining", "Fast delivery"]` |
| `createdAt` | `"2024-03-15T10:22:00+00:00"` |
| `timestamp` | `1710498120` |
| `authorName` | `"Julia Odan"` |
| `authorProfileUrl` | `"https://www.facebook.com/julia.odan"` |
| `authorProfileImageUrl` | `"https://scontent.fbcdn.net/..."` |
| `authorIdType` | `"pfbid"` or `"numeric"` — see FAQ |
| `authorReviewCount` | `12` — only on reviews delivered in Facebook's older review format |
| `reactionCount` | `3` |
| `reactionBreakdown` | `[{"type": "Like", "count": 4}, {"type": "Haha", "count": 1}]` |
| `shareCount` | `0` |
| `commentCount` | `2` |
| `reviewPhotos` | `["https://scontent.fbcdn.net/..."]` |
| `topComments` | `[{"authorName": "McDonald's", "text": "Thanks for the feedback!", "createdAt": "2024-03-16T09:00:00+00:00", "isOwnerReply": true, "authorIdType": "numeric", "commentPermalinkUrl": "https://facebook.com/...", "replyCount": 2}]` |
| `reviewUrl` | `"https://www.facebook.com/.../posts/..."` |
| `page.name` | `"McDonald's"` |
| `page.id` | `"100064458773195"` |
| `page.url` | `"https://www.facebook.com/McDonalds"` — when available |
| `page.category` | `"Fast Food Restaurant"` — present only when Facebook's page data exposes it |
| `page.address` | `"110 N Carpenter St, Chicago, IL"` — present only when Facebook's page data exposes it |
| `page.phone` | `"+1 630-623-6196"` — present only when Facebook's page data exposes it |
| `page.website` | `"https://www.mcdonalds.com"` — present only when Facebook's page data exposes it |
| `page.totalReviewCount` | `4821` — when available |
| `page.recommendationPercentage` | `87` — when available |
| `page.followerCount` | `82000000` — read from the follower label Facebook displays (e.g. "82M"), so it is rounded the same way |
| `recordType` | `"review"` |
| `scrapedAt` | `"2026-09-02T12:00:00+00:00"` |

The dataset can also contain error records with `"recordType": "error"`, holding only `error` (a description) and `scrapedAt`. One is written when an input item returns no reviews at all or still fails after three attempts, and the run writes a single error record and stops when no input items are given for the chosen mode, the dates are invalid, or the proxy can't be set up. If reviews were fetched but your filters matched none of them, no error record is written.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `url` | `url` / `search` / `pageId` — how to specify the Facebook page |
| `startUrls` | array | `[]` | Facebook page URLs (mode=`url`); `/reviews` is added automatically when missing |
| `searchQueries` | array | `[]` | Business name + location, e.g. `"Starbucks Dallas TX"` (mode=`search`) |
| `pageIds` | array | `[]` | Numeric Facebook Page IDs, e.g. `"100064458773195"`, or page usernames such as `"mcdonalds"` (mode=`pageId`) |
| `maxReviews` | integer | `100` | Maximum total reviews across all input pages (1–500) |
| `maxReviewsPerPage` | integer | – | Cap per individual page, for an even spread across multiple pages (1–500). When empty, only `maxReviews` applies |
| `sortBy` | string | `most_recent` | `most_recent` keeps the page's default order; `most_helpful` is attempted but usually has no effect (see FAQ) |
| `filterByRecommendation` | string | `all` | `all` / `recommended` / `not_recommended` |
| `filterByDateFrom` | string | – | Only reviews on or after this date (`YYYY-MM-DD`). Reviews without a date are kept |
| `filterByDateTo` | string | – | Only reviews on or before this date (`YYYY-MM-DD`) |
| `filterByKeyword` | string | – | Only reviews containing this word or phrase (case-insensitive) |
| `cookies` | array | `[]` | Optional logged-in session cookies to unlock more than ~10-15 reviews per page |
| `proxyCountry` | string | `US` | Exit country of the built-in residential proxy: `US` / `GB` / `CA` / `AU` / `IE` |

### Example: scrape reviews from a direct URL

```json
{
  "mode": "url",
  "startUrls": [{ "url": "https://www.facebook.com/mcdonalds/reviews" }],
  "maxReviews": 100
}
```

### Example: find a business by name and city

```json
{
  "mode": "search",
  "searchQueries": ["Starbucks Seattle WA"],
  "maxReviews": 50
}
```

### Example: only negative reviews from the last 90 days

```json
{
  "mode": "url",
  "startUrls": [{ "url": "https://www.facebook.com/IHOP/reviews" }],
  "filterByRecommendation": "not_recommended",
  "filterByDateFrom": "2026-06-01",
  "maxReviews": 100
}
```

### Example: multiple pages by numeric Page ID, capped per page

```json
{
  "mode": "pageId",
  "pageIds": ["100064458773195", "100044057870366"],
  "maxReviewsPerPage": 25,
  "maxReviews": 50
}
```

## Use Cases

- **Reputation monitoring** — track new Recommended/Not Recommended reviews and business owner replies for a brand or franchise location
- **Competitor analysis** — compare recommendation percentages, review volume, and recurring complaint keywords across competing businesses
- **Local business research** — pull reviews for restaurants, hotels, or service providers before choosing where to eat, stay, or book
- **Customer feedback analysis** — export review text and recommendation tags (e.g. "Fast delivery", "Disappointing food") for sentiment or NLP pipelines
- **Franchise/multi-location tracking** — scrape reviews across many location-specific Page IDs in a single run to compare performance
- **Market research** — measure follower counts and recommendation trends across an industry vertical

## FAQ

**Does this require a Facebook account or cookies?**
No. The actor scrapes publicly visible reviews on public business pages without logging in. Cookies are an optional input for unlocking more than the ~10-15 reviews per page that Facebook shows to logged-out visitors.

**Is this an official Facebook or Meta product?**
No. This is an independent, third-party actor that reads publicly available Facebook business page data. It is not affiliated with, endorsed by, or connected to Meta Platforms, Inc.

**Why does Facebook use Recommended/Not Recommended instead of star ratings?**
Facebook business pages now use a binary Recommended/Not Recommended system, so there is no per-review star rating. The page-level `page.recommendationPercentage` is Facebook's own figure and is not recalculated from the reviews returned here, so it may not match a simple count of them. Use `isRecommended` for per-review analysis.

**Can I get the business's replies to reviews?**
Yes. When a business reply is among the comments Facebook shows on a review, it appears inside `topComments` with `isOwnerReply: true`. The flag is set when the commenter's account ID matches the page's own ID, not by comparing display names.

**How many reviews can I get per page?**
`maxReviews` and `maxReviewsPerPage` each go up to 500. Without cookies, Facebook usually stops serving new reviews to a logged-out visitor well before that (commonly around 5-15 per page) — this is a Facebook-side limit, not a scraper failure; the run's status message notes it when it happens. Supply `cookies` for a logged-in session to raise this ceiling.

**Do I need to configure a proxy?**
No separate setup is needed — a residential proxy is always used for access to Facebook. `proxyCountry` just lets you pick which country that proxy exits from.

**Will search mode always find the right business?**
Facebook's own on-site search requires a login, so `search` mode looks your query up through a public web search; if that finds nothing, it tries a page address built from the first two words of the query. For distinctive business names this generally finds the correct page, but ambiguous queries (a common name with no location) can return the wrong page or no match. For a guaranteed exact match, use `url` or `pageId` mode instead.

**Does "Most Helpful" sort actually work?**
Rarely. The actor looks for a sort control on the reviews page, but Facebook's current review pages generally don't show one, so in practice reviews come back in the page's default order for both `sortBy` values. The run continues normally either way.

**What is `authorIdType`?**
Facebook identifies most regular reviewers with a rotating `pfbid` token rather than a permanent numeric ID, meaning the same person isn't always reliably trackable as "the same reviewer" across separate runs. Business/Page accounts (e.g. a company replying to its own reviews) do get a stable numeric ID. `authorIdType` tells you which kind of identifier you got (`"pfbid"` or `"numeric"`).

**What happens if a page has no reviews or can't be reached?**
A record with `"recordType": "error"` and a description is pushed instead of the run failing or crashing.

**Are review photo URLs permanent?**
Facebook CDN URLs can expire after some time — use the `scrapedAt` timestamp to track freshness. In practice most reviews are text-only or carry a recommendation tag rather than a photo, so `reviewPhotos` is frequently absent — that reflects real review behavior, not a gap in the scraper.

**Can this scrape a business's About info (address, phone, hours, category)?**
Only partly. The actor doesn't open the About tab, so it never returns opening hours. `page.category`, `page.address`, `page.phone` and `page.website` are filled in only when Facebook happens to include them with the reviews data, which is often not the case.

## Limitations

- **500 review cap** — `maxReviews` and `maxReviewsPerPage` can't exceed 500, and without cookies far fewer reviews per page are usually available
- **Public pages only** — private groups, personal profiles, and Marketplace listings are not supported
- **Sort control is usually missing** — `most_helpful` falls back to the page's default order when Facebook doesn't show the control
- **Search mode resolves via external web search, not Facebook's own search** — most reliable for distinctive business names
- **Reviewer identity isn't always a stable ID** — see `authorIdType` in the FAQ
- **Business "About" details are partial at best** — see the FAQ
- **Some pages are blocked more often than others** — a page that still returns nothing after three attempts produces an error record
