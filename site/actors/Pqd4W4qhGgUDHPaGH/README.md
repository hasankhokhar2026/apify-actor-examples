# Facebook Ad Library Byline & Advertiser Ad Finder

Look up who is advertising and what they are running. This actor reads Meta's public Facebook Ad Library without a login, a cookie, or a Meta API token. Start from an advertiser Page, a specific Ad Library ID, a free-text keyword, or the "Paid for by" name printed on a political disclaimer, and get one clean record per ad with its creative, media, run window, placements, creative-reuse count, advertiser context, and - when Meta publishes them for political or EU-regulated ads - spend, impressions and reach.

## What this actor does

- **Four lookup paths in one run:** keyword search, advertiser Page (numeric ID or URL), direct Ad Library ID, and "Paid for by" byline. Fill in one list or several; a single run processes them all.
- **Real request-side filters:** country (single or multi-country union), content language, active/inactive status, ad category, media type, publisher platform, keyword match mode, delivery-date window and sort order.
- **Creative in full:** ad body, title, caption, description, call-to-action, destination link, single image/video URLs, video previews, carousel cards and dynamic-creative placeholder tokens.
- **Advertiser context:** Page name and ID, Page likes, categories, profile picture and page URL, plus optional per-ad detail data such as page About text, Instagram handle and followers.
- **Political and EU transparency:** spend and impression ranges, byline, disclaimer label, payer/beneficiary, EU total reach, age/gender/location targeting and reach breakdowns.
- **Honest by design:** spend, impressions and reach appear only where Meta actually discloses them. Commercial ads never get a guessed number; the field is simply absent. Every empty field is dropped from the record.
- **Cookieless and setup-free:** no cookies, no login, no API key, and no proxy configuration. The actor manages its own connection automatically.

## Output per ad

Every record carries `ad_id` (Ad Library archive ID), `ad_snapshot_url` and `sourceUrl` (the ad's public permalink), `recordType: "ad"`, `scraped_at` and `scrapedAt`.

**Identity and advertiser**

- `page_id`, `page_name`, `page_url`, `page_profile_uri`, `page_profile_picture_url`
- `page_like_count`, `page_categories`, `page_is_deleted`, `page_is_restricted`, `page_verification`, `page_alias`, `page_cover_photo_url`
- `advertiser_about`, `advertiser_page_category`, `advertiser_ig_username`, `advertiser_ig_followers`, `advertiser_ig_verified`, `entity_type`, `page_spend`

**Creative**

- `ad_text`, `title`, `caption`, `link_description`, `cta_text`, `cta_type`, `display_format`
- `link_url` - the destination the ad sends clicks to
- `media_type` - `image`, `video` or `none` (derived from the creative). The `mediaType=meme` input is a server-side filter; Meta's payload has no meme marker, so the output never invents `meme`.
- `media_url` - primary creative. With `rehostMedia`, a successful copy is in `media_url`, the signed original in `media_url_original`/`media_url_original_expires_at`, and `media_rehost_status` says `rehosted`; `media_url_expires_at` is present only while `media_url` itself is a signed fbcdn URL (rehost off/failed). Failure values are `disabled`, `too_large`, `download_failed` and `kv_failed`, with `media_rehost_reason`.
- `image_urls[]`, `video_urls[]`, `video_preview_urls[]`
- `cards[]` - carousel cards with `title`, `body`, `caption`, `linkUrl`, `ctaText`, `ctaType`, `imageUrl`, `videoUrls`, `videoPreviewUrl`
- `template_tokens[]`, `template_body`, `template_title`, `resolved_ad_text`, `resolved_title` - dynamic-creative (DCO/DPA) placeholders and any token-free card variant

**Delivery**

- `start_date`, `end_date` - `YYYY-MM-DD`
- `days_running` - days between start and end (or today for active ads)
- `status` - `active` or `inactive`; omitted together with `is_active` when Meta does not send a boolean (no `unknown` sentinel)
- `publisher_platform[]` - e.g. `FACEBOOK`, `INSTAGRAM`, `MESSENGER`, `AUDIENCE_NETWORK`
- `collation_count`, `collation_id` - Meta's creative-reuse group and count
- `categories[]`, `gated_type`, `is_aaa_eligible`, `contains_digital_created_media`, `contains_sensitive_content`, `has_user_reported`, `hide_data_status`, `regional_regulation_data`

**Political and EU transparency (only when Meta publishes it)**

- `spend`, `spend_lower_bound`, `spend_upper_bound`, `currency`
- `impressions`, `impressions_index`, `impressions_lower_bound`, `impressions_upper_bound`
- `reach_estimate`, `reach_lower_bound`, `reach_upper_bound`
- `byline`, `disclaimer_label`
- `eu_total_reach`, `uk_total_reach`, `br_total_reach`
- `target_age_audience`, `target_gender_audience`, `target_location_audience`
- `age_country_gender_reach_breakdown`, `audience_age_gender`, `audience_location`, `audience_single_country`
- `payer_beneficiary[]`, `violation_types[]`, `is_violating_eu_siep`

When `onlyTotal` is on, the dataset contains one summary record per target **per country** instead: `type: "facebook_ads_library_total"`, `recordType: "total"`, `search_term`, `country`, `total_results`, `scraped_at`. Totals are not available for byline or direct ad-ID targets because the Ad Library page has no byline filter and an ad page has no search result list; those targets get an `unsupported_total` diagnostic.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `""` | `""` processes every provided target list; or choose `search`, `byPage`, `byAdId`, `byByline` |
| `searchTerms` | array | `[]` | Keywords to search, one query per term. Prefill: `["coffee"]` |
| `pageIds` | array | `[]` | Facebook Page IDs, or URLs containing `view_all_page_id=` / `profile.php?id=` |
| `adIds` | array | `[]` | Ad Library IDs, or ads-library URLs containing `?id=` |
| `bylines` | array | `[]` | Funding-entity names from a political ad's "Paid for by" disclaimer. Non-EU targets use the political archive; EU/EEA targets use the all-types EU DSA stream and a client-side byline check |
| `country` | string | `ALL` | Single ISO 3166-1 alpha-2 country, or `ALL` |
| `countries` | array | `[]` | Multiple country codes, searched as a union. Takes precedence over `country` |
| `adActiveStatus` | string | `active` | `all`, `active` or `inactive` |
| `adType` | string | `all` | `all`, `political_and_issue_ads`, `housing`, `employment` or `credit` |
| `mediaType` | string | `all` | `all`, `image`, `video`, `meme` or `none`. `meme` is a server-side filter only; output `media_type` stays `image`/`video`/`none` |
| `publisherPlatforms` | array | `[]` | Only ads shown on Facebook, Instagram, Messenger, Audience Network, WhatsApp or Threads |
| `contentLanguages` | array | `[]` | 2-letter ISO 639-1 creative languages (full list in the dropdown) |
| `searchType` | string | `keyword_unordered` | `keyword_unordered` or `keyword_exact_phrase` |
| `startDate` | string | - | Include ads with delivery on or after this date (`YYYY-MM-DD`) |
| `endDate` | string | - | Include ads with delivery on or before this date (`YYYY-MM-DD`) |
| `sortBy` | string | `relevance` | `relevance` or `total_impressions` |
| `resultsPerSearch` | integer | `50` | Cap per target (1-100000). Prefill: `3` |
| `maxItems` | integer | `1000` | Cap for the whole run across all targets (1-100000). Prefill: `3` |
| `includeEuDetails` | boolean | `true` | Fetch per-ad EU transparency and advertiser-profile detail. Adds one request per ad. Prefill: `false` |
| `rehostMedia` | boolean | `true` | Copy the primary media (max 15 MB) into the run's key-value store and emit a permanent URL. `media_rehost_status` records success/failure; arrays, carousel cards and Page profile/cover URLs stay signed. Prefill: `false` |
| `onlyTotal` | boolean | `false` | Skip ad records and return one result count per target per country. Not available for byline or direct ad-ID targets |

Provide at least one of `searchTerms`, `pageIds`, `adIds` or `bylines`. Per-mode requirements are checked in code, so an empty list simply produces a clear status message instead of a crash.

### Example: every active ad from an advertiser Page

```json
{
  "mode": "byPage",
  "pageIds": ["15087023444"],
  "countries": ["US", "CA"],
  "adActiveStatus": "active",
  "maxItems": 200
}
```

### Example: trace a political funding entity

```json
{
  "mode": "byByline",
  "bylines": ["JON OSSOFF FOR SENATE"],
  "countries": ["US"],
  "adType": "political_and_issue_ads",
  "maxItems": 50
}
```

### Example: exact-phrase creative search with a delivery window

```json
{
  "mode": "search",
  "searchTerms": ["free shipping"],
  "searchType": "keyword_exact_phrase",
  "country": "GB",
  "startDate": "2026-01-01",
  "endDate": "2026-06-30",
  "mediaType": "video",
  "sortBy": "total_impressions"
}
```

### Example: fetch known ads by ID, with EU detail

```json
{
  "mode": "byAdId",
  "adIds": ["1098840072544828", "2619351891814847"],
  "includeEuDetails": true,
  "rehostMedia": true,
  "maxItems": 2
}
```

### Example: count results without downloading them

```json
{
  "mode": "search",
  "searchTerms": ["nike", "adidas"],
  "country": "US",
  "onlyTotal": true
}
```

## Use cases

- **Competitive ad monitoring:** pull the current rotation for a competitor Page and compare hooks, offers and landing pages.
- **Creative research:** collect live ad copy, images, video and carousel cards for a swipe file or mood board.
- **Political and issue-ad accountability:** follow a "Paid for by" committee, then read its spend, impressions and payer/beneficiary data.
- **EU DSA transparency:** audit an advertiser's EU reach, targeting and demographic breakdown.
- **Creative-reuse analysis:** sort by `collation_count` to see which creative a brand is scaling hardest.
- **Known-ad due diligence:** resolve a specific Ad Library ID to its full record before it disappears from the live library.

## FAQ

**Do I need a Facebook account, cookies or a developer app?** No. The actor reads the public Ad Library anonymously. There are no cookie, login or API-key inputs, and none are needed for the daily test.

**Why are spend and impressions missing on some ads?** Meta only publishes those figures for political/issue ads and some EU/UK transparency ads. The actor never estimates or fills them for ordinary commercial ads; the fields are omitted instead.

**Why is a media URL missing or different?** Facebook's own media URLs are signed and expire after a few days. With `rehostMedia` on, the actor copies the primary media (up to 15 MB) to the run's key-value store and returns a permanent URL in `media_url`, keeping the original in `media_url_original` and its expiry in `media_url_original_expires_at`. `media_rehost_status` tells you whether the copy succeeded; if it is `too_large`, `download_failed` or `kv_failed`, `media_url` remains the signed original. Per-card, array and Page profile/cover URLs stay as Meta served them.

**How many ads can one run return?** The Ad Library serves 10 ads per page and the actor follows the cursor until it reaches `maxItems` or the server runs out. Meta's displayed totals cap at 50,001, so a search may honestly report "50,000+" rather than an exact larger number.

**Why did a byline search return nothing?** Meta's byline filter matches the funding-entity string exactly and only works inside the political archive. The actor tries the uppercase form first, then the original casing, and also re-checks each returned ad's `byline` field client-side. If nothing matches, you get a diagnostic rather than an unrelated ad.

**Why did an EU political or byline search get remapped?** The political-and-issue archive excludes EU/EEA countries. When those filters are combined, the actor searches the EU transparency stream (`adType=all`) and warns in the run status. For byline targets in EU/EEA countries, the match is checked client-side because Meta may not expose the funding byline there; a zero result is explained as an EU archive limitation, not proof that the funder has no ads. Filter on `categories` to pick out political ads.

**What is `collation_count`?** Meta's own count of ad variants that share one creative and text. It is the fastest built-in signal for creative reuse.

**Can one run mix keyword, Page, Ad ID and byline lookups?** Yes. Leave `mode` empty and fill in any combination of the four lists. Each target is processed in order and every ad is deduplicated by `ad_id` across the whole run.

**Does the actor need a proxy?** No. It chooses a working connection automatically; there is nothing to configure.

**Is this affiliated with Meta?** No. It is an independent tool reading the same public Ad Library pages anyone can browse at facebook.com/ads/library.

## Limitations

- Meta's public payload does not expose spend, impressions or reach for ordinary commercial ads. Those fields are omitted, never estimated.
- Media URLs from Facebook's CDN are signed and expire. With `rehostMedia`, only the primary `media_url` is copied (15 MB cap); `image_urls`, `video_urls`, `video_preview_urls`, carousel-card URLs and Page profile/cover URLs remain signed. A failed/oversized rehost is marked in `media_rehost_status` and keeps the signed URL rather than pretending to be permanent.
- The Ad Library page size is 10. Large runs are cursor-bound and can be slow.
- Displayed totals cap at 50,001 ("50,000+"). The actor reports what Meta reports. `onlyTotal` queries one country per record; it does not add the countries together.
- Byline filtering is exact-cased and works only inside the political/issue archive. Lowercase retries and a client-side byline check are applied. In EU/EEA countries the actor searches `adType=all` because the political archive returns zero there; Meta may not expose the funding byline, so an EU byline zero is a documented limitation, not proof of no ads.
- Dynamic-creative (DCO/DPA) templates sometimes contain placeholders whose values are not in the public payload. The actor keeps the placeholder and attaches a token-free card variant when one exists; it never invents a brand.
- `mediaType=meme` is a server-side filter only. The payload has no meme marker, so output `media_type` is always `image`, `video` or `none`.
- `status`/`is_active` are omitted when Meta does not send a boolean; no `unknown` sentinel is emitted.
- Page-name typeahead is not supported: use a numeric Page ID or a Page URL containing the ID.
- Page-owner contact details and admin history are not part of the ad payload and are not shipped.
- Byline and direct ad-ID totals are unavailable; `onlyTotal` emits an `unsupported_total` diagnostic for those targets because the Ad Library page has no byline filter and an ad page has no search result list.
- Facebook Page URLs (`ad_snapshot_url`, `page_url`, `page_profile_uri`) return 403 to non-browser HTTP clients. They open normally in a browser; this is an anti-bot posture, not a broken URL.
- Scheduled watchlists, diffs and e-commerce enrichment are separate use cases and are not part of this actor.
