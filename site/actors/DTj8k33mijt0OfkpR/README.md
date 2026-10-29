# Facebook Marketplace Listing & Price Extractor

Extract public Facebook Marketplace listings without cookies, login, or a proxy of your own. Point the actor at Marketplace search, category, city-feed, or direct item URLs, or give it a keyword plus a city, and get one structured row per listing with price, location, delivery, status, seller, photos, and optional detail fields.

## What this actor does

- Scrapes keyword searches, city categories, global categories, city/location feeds, and direct item pages in one run.
- Builds a Marketplace search from `searchQueries` + `location`, resolving city names, postal codes, and addresses server-side.
- Paginates search and category feeds with Facebook's cursor, stopping on source exhaustion, a repeated cursor, two empty pages, `maxPagesPerUrl`, or `maxItems`. There is no fixed row cap: the Phase 6 probe reached 1,694 unique search rows across 71 pages before Facebook returned an empty page 72.
- Reads feed rows in `fast` mode and fetches each listing page in `deep` mode for description, condition, attributes, seller, coordinates, gallery, and vehicle fields.
- Applies price, condition, delivery, age, availability, category, and exact-keyword filters against the data each row actually carries.
- Rehosts the primary photo into the actor key-value store by default so the emitted URL does not expire; the original signed URL is retained. If a download fails, the original signed URL is kept and flagged `mediaUrlTemporary: true`.
- Empty fields are omitted: null, empty-string, empty-list, and empty-object values are never emitted. `0` and `false` are preserved.
- Works without user cookies. The proxy ladder starts direct and only escalates when Facebook blocks a request; residential is a hardcoded last resort after free rungs fail, never a schema default.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `auto` | `auto` uses `startUrls` when present, otherwise keyword search. `search` builds searches from `searchQueries` + `location`. `urls` scrapes Marketplace URLs. `items` fetches direct item URLs or numeric IDs. |
| `startUrls` | array | none | Marketplace search, city-category, global-category, city-feed, or `/marketplace/item/` URLs. In `items` mode a bare numeric listing ID is also accepted. |
| `searchQueries` | array | `[]` | One to 20 keywords or phrases. Each query becomes one source. Legacy `searchQuery` is mapped in code. |
| `location` | string | none | Marketplace slug, city, postal code, or address, e.g. `nyc`, `Austin, Texas`, `90210`, `London`. Required for keyword search unless coordinates are provided. |
| `country` | string | `US` | ISO 3166-1 alpha-2 country used when resolving a human location. Use `GB` for London, `CA` for Toronto, and so on. |
| `latitude` | number | none | Optional search center latitude. Provide `longitude` too. Overrides `location` when both are set. |
| `longitude` | number | none | Optional search center longitude. Provide `latitude` too. |
| `radiusKm` | integer | `65` | Search radius in kilometres (1-500). Sent server-side (search uses kilometres; category and city queries convert to metres) and enforced client-side over listing coordinates. Rows whose coordinates are absent cannot be distance-checked and are kept; the status message reports how many were kept that way. URL-mode sources use the radius embedded in the page unless `radiusKm` is set explicitly. |
| `category` | string | `all` | Curated Marketplace category: `vehicles`, `electronics`, `furniture`, `home`, `tools`, `sports`, `toys`, `appliances`, `jewelry`, `autoparts`, `garden`, `pets`, `books`, `shoes`, `games`, `motorcycles`, `boats`, `antiques`, `arts`, `health`, `cell-phones`, `computers`, `video-games`, `cameras`, or `all`. With no `searchQueries`, opens the city or global category feed instead. Books, shoes, games, motorcycles, cell-phones, computers, video-games, and cameras were verified as category feeds but expose no server category ID, so they cannot be used as keyword filters; use `categoryId` or a category URL instead. Cameras returned rows in the city feed but 0 rows globally in the probe. |
| `categoryId` | string | none | Advanced numeric Facebook category ID. Takes precedence over `category`. |
| `sortBy` | string | `relevance` | `relevance`, `newest`, `oldest`, `price_asc`, `price_desc`, or `distance`. Sent server-side where Marketplace supports it; price and time are re-sorted client-side, with rows missing a price or date last. |
| `minPrice` | number | none | Minimum price. Listings without a readable price are dropped when set. |
| `maxPrice` | number | none | Maximum price. Listings without a readable price are dropped when set. |
| `condition` | string | `any` | `any`, `new`, `used_like_new`, `used_good`, or `used_fair`. Sent server-side in search/category modes; checked again in deep mode. Fast rows without condition data are kept. |
| `deliveryMethod` | string | `all` | `all`, `shipping`, or `local`. Client-side over `delivery_types`; legacy `local_pickup` is accepted and normalized to `local`. Rows without delivery data are dropped while this filter is active. |
| `daysSinceListed` | integer | none | Only listings created within this many days (1–365). Rows without a posting time are dropped. |
| `availability` | string | `all` | `all`, `available`, `sold`, or `pending`. Client-side over `is_live`/`is_sold`/`is_pending`. |
| `exactMatch` | boolean | `false` | Keep only rows whose title (and description in deep mode) contains every query word. |
| `maxItems` | integer | `50` | Global output limit across all sources (1–10000). |
| `maxItemsPerUrl` | integer | `50` | Per-source output limit (1–10000). |
| `maxPagesPerUrl` | integer | `100` | Cost guard for cursor pagination (1–500). The actor stops earlier on source exhaustion, a repeated cursor, two empty pages, or `maxItems`. The observed search ceiling was 1,694 unique rows over 71 pages; this is not an enforced cap. |
| `scrapeMode` | string | `fast` | `fast` streams feed rows. `deep` fetches each listing page for description, condition, attributes, seller, coordinates, and photos. `auto` follows `includeListingDetails`/`includeAllPhotos`. |
| `includeListingDetails` | boolean | `false` | Compatibility alias that enables deep mode unless `scrapeMode` is explicitly `fast`. |
| `includeAllPhotos` | boolean | `false` | Enables deep mode and emits the full photo gallery. |
| `rehostImages` | boolean | `true` | Copy primary photos and seller avatars into the actor key-value store. When off, signed Facebook URLs are emitted as-is (including the seller avatar) with `mediaUrlTemporary: true`. |
| `deduplicateAcrossInputs` | boolean | `true` | Emit each listing ID once across sources. Disable to preserve repeats from repeated input URLs. |
| `proxyConfiguration` | object | none | Optional advanced override. The actor works without a proxy and escalates only after a real block. Explicit user configuration is respected exactly. |

### Legacy inputs

`searchQuery` is mapped to `searchQueries` when the new field is absent. `resultsLimit` is still accepted from API clients and maps to `maxItemsPerUrl` when that field is absent; it is intentionally not shown in the schema. `deliveryMethod: "local_pickup"` is normalized to `local`. The old production input with a US residential `proxyConfiguration` still runs unchanged, although it is no longer the default.

## Output per listing

Every dataset row is one listing object. Empty values are omitted at every depth; consumers should treat a missing field as unknown rather than `null`.

**Identity and provenance**

- `id`, `title`, `listingUrl`, `sourceUrl`, `facebookUrl`
- `sourceType` (`search`, `category`, `location`, or `direct-item`), `inputIndex`
- `searchQuery`, `locationQueried`, `categoryQueried`
- `recordType` (`listing`), `scrapedAt`

**Core fields**

- `price` — `{ amount, currency, formatted, amountWithOffset }`; `currency` is usually absent in fast feed rows and present in deep mode
- `strikethroughPrice`, `description`, `condition`, `conditionLabel`
- `attributes` — `{ name, value, label }` entries
- `categoryId`, `categoryName`, `categorySlug`, `categoryPath`

**Location**

- `locationText`, `city`, `state`, `latitude`, `longitude`, `distanceKm` (when the radius filter ran and the listing has coordinates)

**Delivery, status, and age**

- `deliveryTypes`, `shippingAvailable`, `localPickupAvailable`
- `creationTime`, `createdAt`, `listingAgeDays`
- `isLive`, `isSold`, `isPending`, `isHidden`, `isViewerSeller`, `listingStatus`

**Seller**

- `seller` — `{ id, name, profileUrl, profilePictureUrl, rating, ratingCount, ratingsPrivate, dealer }`
- `profileUrl` is emitted only for stable numeric Facebook user IDs as `https://www.facebook.com/profile.php?id=<numeric id>`. `pfbid...` Marketplace seller IDs are session-scoped opaque tokens that often resolve to dead or restricted pages, so they are never turned into profile links.
- `dealer` is emitted only for dealer/business rows (`DIRECT_DEALERSHIP` or dealer fields present, never `PRIVATE_SELLER`): `{ name, street, city, region, postalCode, country, phone, phoneUniversal }`. Private-seller phone/email is never fabricated or collected.
- `sellerDataAvailability` (`exposed` or `not_exposed`)

**Media and vehicle**

- `primaryPhotoUrl` (rehosted KV URL when rehosting succeeds), `primaryPhotoUrlOriginal`, `mediaUrlTemporary`; failed primary, avatar, and gallery rehosts fall back to the original signed URL with the temporary flag set instead of dropping the media.
- `photos` — `{ id, url, width, height, caption }`; only when `includeAllPhotos` is enabled
- `videoUrl`, `videos`
- `vehicleDetails` — `{ make, model, trim, odometer, transmission, fuelType, exteriorColor, interiorColor, titleStatus, sellerType, condition, specs, numberOfOwners, isPaidOff }` for vehicle listings; conditional fields are omitted when Facebook does not expose them
- `specs` — `{ gasMileageCity, gasMileageCombined, gasMileageHighway, safetyRatingFront, safetyRatingOverall, safetyRatingRollover, safetyRatingSide, safetyRatingSideBarrier, co2Emissions, engineSize, horsePower }`, each as `{ value, unit }` when present
- `vehicleVin` and `vehicleVinSource` — `structured` when Facebook supplies the field, otherwise `description` only for a checksum-valid 17-character VIN found in the listing text. Invalid VIN-shaped prose is never emitted.

**Quality and access**

- `dataMode` (`fast` or `deep`), `extractionSource`, `qualityStatus` (`complete` or `partial`)
- `missingFields` — expected canonical fields that were absent
- `accessState`, `detailFetchStatus` (deep/direct rows)

**Facebook compatibility aliases**

The actor also emits, when present: `marketplace_listing_title`, `listing_price` (`amount`, `formatted_amount`, `amount_with_offset_in_currency`, `currency`), `strikethrough_price`, `location`, `is_hidden`, `is_live`, `is_pending`, `is_sold`, `is_viewer_seller`, `delivery_types`, `marketplace_listing_category_id`, `marketplace_listing_seller`, `primary_listing_photo`, `listingPhotos`, `listingVideo`, `vehicle`, `custom_title`, `custom_sub_titles_with_rendering_flags`, `origin_group`, `parent_listing`, `comparable_price`, `comparable_price_type`, `min_listing_price`, `max_listing_price`, `redacted_description`, `attribute_data`, `creation_time`, `share_uri`, `shipping_offered`, `commerce_badges_info`, `cross_post_info`, `search_pivots`, and `created_with_seller_app`. `shipping_offered` is a raw Facebook compatibility value and can be `false` even when `deliveryTypes` contains a shipping value; use the derived `shippingAvailable` flag instead.

## Example: daily prefill

```json
{
  "mode": "urls",
  "startUrls": [
    { "url": "https://www.facebook.com/marketplace/nyc/search/?query=laptop" }
  ],
  "maxItems": 3,
  "maxItemsPerUrl": 3,
  "maxPagesPerUrl": 1,
  "scrapeMode": "fast",
  "includeListingDetails": false,
  "includeAllPhotos": false,
  "rehostImages": false,
  "deduplicateAcrossInputs": true
}
```

## Example: keyword search by city

```json
{
  "mode": "search",
  "searchQueries": ["laptop", "office chair"],
  "location": "Austin, Texas",
  "country": "US",
  "radiusKm": 40,
  "condition": "used_good",
  "minPrice": 50,
  "maxPrice": 500,
  "maxItems": 100
}
```

## Example: deep detail scrape

```json
{
  "mode": "urls",
  "startUrls": [
    { "url": "https://www.facebook.com/marketplace/nyc/electronics" }
  ],
  "scrapeMode": "deep",
  "includeAllPhotos": true,
  "maxItemsPerUrl": 20
}
```

## Example: direct item

```json
{
  "mode": "items",
  "startUrls": [
    { "url": "https://www.facebook.com/marketplace/item/772594759027016/" }
  ],
  "includeAllPhotos": true
}
```

## Use cases

- **Price monitoring** — track asking prices for a product or category across cities over time.
- **Resale and arbitrage** — scan multiple city feeds for underpriced items.
- **Vehicle shopping** — pull vehicle listings by location, price range, and condition.
- **Apartment hunting** — collect rental and furniture listings from several neighborhoods.
- **Market research** — compare listing volume and pricing across regions.

## Verified hard limits

These limits were measured in the Phase 6 research and are not configurable away:

- **24 listings per search page.** `count` 24/50/100/250 all return 24; the cursor still advances.
- **City feed: 20 listings, no cursor.** The actor keeps the mode for compatibility, warns in the status message, and returns at most 20 rows. Use a keyword or category URL for volume.
- **Delivery filter is client-side.** Facebook's delivery server parameters are no-ops (`shipping-only` returned 0 rows, `local-only` did not filter). The actor filters on `delivery_types` after fetching.
- **Private-seller contact is not exposed.** No phone, email, or messaging path appears logged out. The actor never fabricates contact data. Dealer rows with `DIRECT_DEALERSHIP` can expose `dealership_name`, `listing_address`, and `seller_phone_number`; those are emitted in `seller.dealer` only for dealer rows.
- **Vehicle features, Carfax, registration plate, and website link are null logged out.** They are not emitted. VIN is different: structured VIN is always null, but a checksum-valid VIN pasted in the description is emitted with `vehicleVinSource: "description"`.
- **Signed media URLs expire in roughly 4.3–4.5 days.** Primary photos and avatars are rehosted when `rehostImages` is true; gallery photos are rehosted when `includeAllPhotos` is enabled. If a download fails (including CDN blocking one network path), the actor retries over an alternate proxy and then keeps the original signed URL with `mediaUrlTemporary: true`. Videos remain signed and temporary (`mediaUrlTemporary: true`); safe video rehosting is not implemented.
- **Property rentals category is unsupported.** `/marketplace/<city>/propertyrentals` redirects without usable variables. Use a keyword search such as `query=apartment` as the workaround.
- **Cloud free proxy rungs are blocked.** Direct, fresh-session, and Apify Proxy AUTO returned the login wall on the cloud; residential is the hardcoded last resort after those free rungs and is never a schema default.

## FAQ

**Why did I get fewer rows than `maxItems`?**
`maxItems` and `maxItemsPerUrl` are ceilings, not guarantees. The source may have fewer matches, Facebook may stop paginating, or client filters may remove rows that lack the evidence they check. If nothing can be returned and no source produced a valid empty result, the run fails with the access states in its status message.

**What is the difference between fast and deep mode?**
`fast` reads only the search/category feed and streams rows. `deep` also fetches each listing page for description, condition, attributes, seller, coordinates, photos, and vehicle detail. Deep rows keep the fast row if a detail fetch fails, with `detailFetchStatus` set.

**Why is the seller or currency missing on some rows?**
Facebook does not expose every field in every view. Feed rows usually omit currency, condition, and some seller details; deep mode fills them when available. `price.currency` is intentionally absent when it cannot be determined rather than guessed.

**Does this need Facebook login or cookies?**
No. It reads publicly accessible Marketplace pages without signing in. Private-seller contact details and private profile scraping are not available logged out and are not collected. A `seller.profileUrl` is derived only from stable numeric seller IDs; session-scoped `pfbid...` tokens are not linked. Dealer name/address/phone are emitted only for dealer rows that expose them.

**Do I need to configure a proxy?**
No. The actor starts with a direct TLS-impersonated request and escalates to a fresh session and then Apify Proxy AUTO only when a request is actually blocked. Cloud verification showed all free rungs still return Facebook's login wall, so residential is the hardcoded last resort after them; it is never a schema default. An explicit `proxyConfiguration` is honored as provided.

**Why is the city feed capped at 20 listings?**
Facebook's city/location feed returns one page of about 20 listings with no cursor. The actor keeps the mode for compatibility and warns in the status message. Use a keyword or category URL for volume.

**How many listings can a search return?**
Search and category feeds paginate with a 24-item page. There is no hardcoded 600-row stop. Phase 6 reached 71 pages / 1,694 unique rows, then page 72 returned an empty payload while still reporting `has_next_page`. The actor stops on source exhaustion, a repeated cursor, two consecutive empty pages, `maxPagesPerUrl`, or `maxItems`, so larger jobs need a higher `maxPagesPerUrl` and `maxItems` rather than price/category splitting.

**Do photo URLs expire?**
Facebook CDN URLs are signed and expire in roughly 4.3–4.5 days. With `rehostImages: true` the primary photo and seller avatar are copied into the actor key-value store so `primaryPhotoUrl` and the avatar URL are stable; the signed primary URL remains in `primaryPhotoUrlOriginal`. With `rehostImages: false`, signed primary and avatar URLs are emitted as-is with `mediaUrlTemporary: true`. Gallery photos are also rehosted with `includeAllPhotos`; any photo whose download fails keeps its original signed URL and the row is marked `mediaUrlTemporary: true`, so the gallery is never silently dropped. Video URLs always remain temporary and are marked with `mediaUrlTemporary`.

**Is this affiliated with Facebook or Meta?**
No. This is an independent third-party actor that reads publicly accessible Facebook Marketplace pages. It is not affiliated with or endorsed by Meta.
