# TripAdvisor Hotel, Restaurant & Attraction Finder

Read Tripadvisor places and reviews in one actor. Search a destination for ranked hotels, restaurants and attractions, open a specific place by its Tripadvisor URL or numeric ID, or export a review stream with server-side filters. Everything works without a Tripadvisor account, API key or cookie.

## Modes

| Mode | What it does | Main inputs |
|---|---|---|
| `search` | Finds ranked places through Tripadvisor listing pages. If those pages are unavailable, it falls back to the GraphQL type-ahead index. | `query`, optional `location` |
| `details` | Reads one place per URL or ID from the place page JSON-LD and embedded data, including amenities and a larger photo when published. | `startUrls` |
| `reviews` | Reads reviews for each target place, 20 per request, with offset pagination and filters. Targets can come from URLs, IDs, or a search query. | `startUrls` or `query`, review filters |

Every record is a flat JSON object. Place rows carry `recordType: "place"`, review rows carry `recordType: "review"`, and both include `sourceUrl` and `scrapedAt`. Empty fields are omitted at every depth, so there are no nulls, empty strings, empty arrays or empty objects in the dataset.

## Place fields

Current fields: `id`, `name`, `type`, `url`, `ratingValue`, `reviewCount`, `ranking`, `priceRange`, `cuisine`, `phone`, `email`, `address`, `lat`, `lng`, `amenities`, `photos`, `sourceUrl`, `scrapedAt`, `recordType`, `detailSource`, `detailStatus`.

Backward-compatible legacy fields are always restored on place rows: `locationId`, `subcategory`, `street`, `city`, `state`, `country`, `postalCode`, `latitude`, `longitude`, `rating`, `numberOfReviews`, `rankingPosition`, `rankingString`, `priceLevel`, `website`, `hotelClass`, `hours`, `description`, `neighborhoods`, `webUrl`, `isClosed`, `photoUrl`, `searchQuery`, `scrapeTimestamp`.

`type` is `hotel`, `restaurant` or `attraction`. `ratingValue`, `reviewCount`, `lat` and `lng` are numeric. The legacy `rating`, `numberOfReviews`, `latitude` and `longitude` fields are strings, matching the pre-revamp contract. `amenities` and `photos` are arrays of strings. `ranking` is the full Tripadvisor ranking text when the place page publishes it.

A TypeAhead fallback row carries `detailSource: "typeaheadFallback"` and `detailStatus: "partial"`; a normal detail-page row carries `detailStatus: "complete"`. Media URLs are checked for scheme, host and extension before they are published.

## Review fields

`id`, `placeId`, `title`, `text`, `rating`, `date`, `tripType`, `language`, `author`, `authorLocation`, `helpfulVotes`, `sourceUrl`, `scrapedAt`, `recordType`.

`date` is the review submission timestamp, `tripType` is the traveler type reported by the reviewer, and `authorLocation` is the reviewer's published hometown.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `search` | `search`, `details` or `reviews`. |
| `query` | string | - | Search phrase, for example `hotels in New York` or `Eiffel Tower`. Also used by `reviews` when no URLs are given. |
| `location` | string | - | Optional destination for search, for example `New York`. With this set, `query` can be just `hotels`. |
| `startUrls` | string list | - | Tripadvisor place URLs or numeric location IDs. Used by `details` and `reviews`. |
| `maxItems` | integer 1-500 | `20` | Maximum places to return in `search`, process in `details`, or use as review targets in `reviews`. |
| `includeDetails` | boolean | `true` | Fetch extra place data: key amenities, a larger photo, and HTML enrichment when the JSON fields are missing. |
| `maxReviews` | integer 1-500 | `20` | Reviews per place in `reviews` mode. |
| `reviewSort` | select | `MOST_RECENT` | `MOST_RECENT`, `MOST_HELPFUL` or `DETAILED`. Attractions automatically use `DETAILED` for `MOST_RECENT` so bookable product reviews do not mix into the attraction's reviews. |
| `reviewRating` | select | `ANY` | `ANY` or 1-5. |
| `reviewLanguage` | select | `ANY` | Common Tripadvisor language tags such as `en`, `de`, `fr` or `es`. |
| `reviewTripType` | select | `ANY` | `FAMILY`, `COUPLES`, `SOLO`, `BUSINESS` or `FRIENDS`. |
| `reviewMonth` | select | `ANY` | `JANUARY` through `DECEMBER`. |
| `reviewKeyword` | string | - | Text that must appear in the review. |
| `proxyConfiguration` | object | - | Optional. Direct access is tried first. |

At least one search phrase or start URL is required, depending on the mode. Search and details modes need their own target. Reviews mode accepts either start URLs or a query.

## Examples

Open one hotel and include amenities:

```json
{
  "mode": "details",
  "startUrls": [
    "https://www.tripadvisor.com/Hotel_Review-g60763-d675616-Reviews-The_Plaza_New_York_A_Fairmont_Managed_Hotel-New_York_City_New_York.html"
  ],
  "maxItems": 1,
  "includeDetails": true
}
```

Search hotels in New York:

```json
{
  "mode": "search",
  "query": "hotels",
  "location": "New York",
  "maxItems": 10,
  "includeDetails": false
}
```

Export recent five-star English reviews for a place:

```json
{
  "mode": "reviews",
  "startUrls": ["675616"],
  "maxItems": 1,
  "maxReviews": 100,
  "reviewSort": "MOST_RECENT",
  "reviewRating": "5",
  "reviewLanguage": "en"
}
```

Search a city and then export its reviews:

```json
{
  "mode": "reviews",
  "query": "restaurants in Paris",
  "maxItems": 5,
  "maxReviews": 20
}
```

## How search works

The actor resolves the destination with the type-ahead GraphQL index and always sends the full free-text query first, even when the query contains a family word such as `restaurants`. Queries like `sushi restaurants in New York` therefore keep `sushi` in the request instead of browsing every restaurant in the city.

Ranked listing pages (`Hotels`, `Restaurants` and `Attractions`) 30 places at a time are used as a supplement. When listing rows are added for a free-text query, they are filtered client-side by the remaining terms against name, cuisine and description; unrelated rows are dropped and reported as `relevance_filtered` in the run status. TypeAhead results are limited to 20 per request, so a free-text-only query can stop at 20 rows; listing supplement and pagination extend family searches up to `maxItems`.

Duplicates are removed by place ID, and TypeAhead results keep their order ahead of listing supplements. `search` never uses a browser, a cookie or a login. Listing pages use a Safari TLS profile; the JSON APIs are called with plain HTTP. With `includeDetails: true`, each place is opened once to fill the full ranking, amenities and photo.

## How details works

Place IDs are read from URLs such as `/Hotel_Review-g60763-d675616-...` or from numeric IDs. Each place page is read as HTML and its schema.org JSON-LD plus server-rendered data supply the place fields, including rating, review count, ranking, price range, contacts, coordinates, amenities, cuisine and photos.

When only a numeric ID is given, the actor opens a category-agnostic Tripadvisor URL and follows the canonical redirect to the hotel, restaurant or attraction page. Redirected URLs are accepted when they keep the same location ID; a redirect to a different ID or to a category page is treated as not found, so data is never attributed to the wrong place.

If a detail page is blocked, details mode falls back to the public TypeAhead record for the same location ID, including ID-only targets with no URL. The fallback is attempted even when the only target is a numeric ID. If TypeAhead cannot identify the place, the review clients resolve the type as a last resort (`detailSource: "reviewTypeFallback"`). Those rows are marked `detailStatus: "partial"` and counted as `details_fallback` in the run status. For reviews, an ID-only target whose detail page cannot resolve the place type also tries the three review clients before the run is marked blocked.

Unsupported Tripadvisor entities such as activities, cruises and airlines are skipped with a counter instead of failing the whole run.

## How reviews works

Reviews come from the public reviews GraphQL endpoint. Each request returns at most 20 reviews; the actor pages by offset until `maxReviews`, the place total, or the run cap is reached. Filters are sent to the server, not applied after downloading everything.

Unlike many review tools, the actor filters every row by the target location ID. Attractions are read with the `DETAILED` sort when `MOST_RECENT` is requested, which keeps bookable product reviews out of the attraction's own review stream.

## Limits

- 20 results per TypeAhead request. Free-text-only queries can therefore stop at 20 unless listing pages add relevant rows.
- Search listing pages hold 30 places; up to 17 pages (500 places) are read per family, matching the `maxItems` ceiling.
- 500 reviews per place per run (a product cap; the upstream offset pagination was verified past 5,000).
- 10,000 reviews per run across all targets.
- 500 places per run.
- Reviews are deduplicated by review ID and places by location ID.
- Media URLs are validated for scheme, host and extension, but are not rehosted; a hotlink-blocked CDN URL can still fail in a consumer application.

The actor fails the run when it produces zero records or when every request is blocked. If only some targets or pages fail, it pushes the records it has and reports the partial counts in the run status, including `details_fallback` and `relevance_filtered`.

## Proxy and anti-bot behaviour

Access is direct first. If Tripadvisor returns a real block, the actor tries the free Apify datacenter proxy (`AUTO`). It only moves to the `RESIDENTIAL` group after `AUTO` is also blocked. A user-supplied `proxyConfiguration` is used after a direct block. You do not need to configure anything for a normal run.

Escalation is per request: every JSON or HTML request starts at `direct` and only that request moves up the ladder after a block. A blocked detail page therefore does not force later TypeAhead or review requests onto a paid rung.

The TypeAhead and reviews GraphQL endpoints are the primary path for discovery and reviews. Place details are read from the place page HTML, which is fetched with the Safari TLS profile and only when a place record is needed.

## FAQ

**Do I need a Tripadvisor account or API key?**
No. The actor reads public place and review data. It does not log in, and it does not need user cookies.

**Do I need a proxy?**
No. Direct access is tried first and works for the JSON APIs. The actor escalates automatically only after a block.

**Why is `amenities` missing for some places?**
Tripadvisor publishes amenities mainly for hotels. Restaurants and attractions often have none, and the field is omitted rather than filled with a placeholder.

**Why are there fewer reviews than the total on the page?**
The review count on a place page can include reviews in many languages and, for attractions, reviews from bookable products. The actor returns the reviews that match the target place and your filters, up to `maxReviews`.

**Why does a search return fewer places than `maxItems`?**
Tripadvisor may not render enough ranked cards for a destination, a page may be unavailable, or a free-text TypeAhead query may return at most 20 rows. The actor supplements TypeAhead with filtered listing pages and reports `relevance_filtered`, `listing_failures` and other partial counts in the status message.

**Are the records always the same shape?**
No. Empty fields are removed, so a restaurant row has `cuisine` while a hotel row may have `amenities`. Every record keeps the identity, source and timestamp fields.

**Is this affiliated with Tripadvisor?**
No. This is an independent, third-party actor that reads publicly available Tripadvisor data. It is not affiliated with or endorsed by Tripadvisor.
