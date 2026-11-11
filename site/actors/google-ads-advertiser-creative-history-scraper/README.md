# Google Ads Transparency Advertiser & Creative Scraper

Scrape **Google Ads Transparency Center** ad creatives for a single advertiser, every advertiser linked to a domain, a brand or keyword search, or one specific creative. Each record carries the advertiser identity, ad format, first and last shown dates, ad copy or product details, media previews, region stats, and impression ranges when Google exposes them. The data is public: no Google account, cookies, or login are required.

## What this actor does

- **Four lookup modes:** `advertiser` (URL or `AR...` ID), `domain` (all advertisers linked to a domain), `search` (brand name or keyword), and `creative` (one ad URL or `CR...` ID).
- **Server-side filters:** country `region`, ad `format` (text, image, video), `platform` (Play, Maps, Search, Shopping, YouTube), and a `political` toggle for political and issue ads.
- **Complete creative history:** cursor pagination at 100 ads per page, up to 1,000 unique ads per run.
- **Rich per-ad detail:** headline, description, display domain, Shopping product title and brand, preview image, video poster, YouTube link, region stats, and impression bounds when available.
- **Client-side date filtering:** `startDate` and `endDate` narrow the fetched slice; Google exposes no date-range parameter for anonymous searches.
- **Clean records:** fields that Google does not expose are omitted rather than returned as `null`, empty strings, or empty arrays.

## Output per ad

- `advertiserId`, `advertiserName` - Google's advertiser ID and display name.
- `advertiserCountry`, `advertiserLegalName`, `advertiserVerified` - advertiser metadata when Google returns it.
- `advertiserAdCountMin`, `advertiserAdCountMax` - the advertiser's total ad-count range when available.
- `creativeId`, `adId` - Google's unique ID for the creative.
- `format` - `TEXT`, `IMAGE`, or `VIDEO`.
- `firstShown`, `lastShown` - first and last dates Google recorded the ad as active (YYYY-MM-DD).
- `headline`, `description`, `body` - text-ad copy when the creative exposes it.
- `callToAction` - call-to-action text when present.
- `displayDomain`, `landingUrl` - display domain, and a full landing URL only when Google exposes one.
- `productTitle`, `productBrand` - Shopping/image ad product details.
- `imageUrl`, `imageUrls` - image creative or Shopping product image URLs.
- `previewUrl` - a preview or media link for the creative.
- `posterUrl` - video poster image.
- `youtubeUrl` - stable YouTube link when the video exposes a YouTube ID.
- `videoUrl`, `videoUrlExpiresAt` - direct video file when Google exposes one; signed, IP-bound, and short-lived.
- `regions`, `regionStats` - country codes and per-region dates/impressions/platform stats for the creative.
- `impressionsMin`, `impressionsMax` - impression bounds when Google returns them.
- `platforms`, `platform` - Google surfaces reported for the creative.
- `adLibraryUrl`, `sourceUrl` - direct Ads Transparency Center links.
- `source` - data source identifier (`google_ads_transparency`).
- `startUrl`, `searchTerm` - the input URL or search term that produced the record, when applicable.
- `recordType`, `scrapedAt` - record type and fetch timestamp.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `advertiser` | `advertiser` / `domain` / `search` / `creative`. |
| `advertiserUrl` | string | - | Advertiser or creative Transparency Center URL (mode=`advertiser` or `creative`). |
| `advertiserId` | string | - | Google advertiser ID beginning with `AR` (mode=`advertiser` or `creative`). |
| `domain` | string | - | Domain to search across all linked advertisers, e.g. `nike.com` (mode=`domain`). |
| `searchQuery` | string | - | Brand name or keyword resolved through Google's advertiser suggestions (mode=`search`). |
| `startUrls` | array | `[]` | Additional advertiser or creative URLs as Apify `{ "url": "..." }` request-list objects. |
| `creativeId` | string | - | Google creative ID beginning with `CR` (mode=`creative`); also set `advertiserId` or `advertiserUrl`. |
| `region` | string | `anywhere` | Country where the ad was shown; `anywhere` applies no filter. Required when `political` is on. |
| `format` | string | - | `TEXT`, `IMAGE`, or `VIDEO`; leave empty for all formats. |
| `platform` | string | - | `PLAY`, `MAPS`, `SEARCH`, `SHOPPING`, or `YOUTUBE`; leave empty for all platforms. |
| `political` | boolean | `false` | Return only political and issue ads. Requires a country `region`. |
| `startDate` | string | - | Only ads with activity on or after this date (YYYY-MM-DD); applied to the fetched slice. |
| `endDate` | string | - | Only ads with activity on or before this date (YYYY-MM-DD); applied to the fetched slice. |
| `maxAdsPerAdvertiser` | integer | `20` | Per-advertiser cap, 1-1000. In domain mode it applies to each advertiser found. |
| `maxItems` | integer | `50` | Total ads to emit, 1-1000. |
| `includeDetails` | boolean | `true` | Fetch per-creative detail and preview content. Turn off for a faster list-only run. |
| `proxyConfiguration` | object | Apify automatic proxy | Optional proxy override; the actor uses an Apify proxy by default. |

## Example: scrape one advertiser

```json
{
  "mode": "advertiser",
  "advertiserUrl": "https://adstransparency.google.com/advertiser/AR16735076323512287233",
  "maxAdsPerAdvertiser": 50,
  "maxItems": 50,
  "includeDetails": true
}
```

## Example: find every advertiser using a domain, US image ads only

```json
{
  "mode": "domain",
  "domain": "nike.com",
  "region": "US",
  "format": "IMAGE",
  "maxAdsPerAdvertiser": 25,
  "maxItems": 100
}
```

## Example: search a brand, video ads shown in 2024

```json
{
  "mode": "search",
  "searchQuery": "Nike",
  "region": "GB",
  "platform": "YOUTUBE",
  "startDate": "2024-01-01",
  "endDate": "2024-12-31",
  "maxItems": 50
}
```

## Example: inspect one creative

```json
{
  "mode": "creative",
  "advertiserId": "AR16735076323512287233",
  "creativeId": "CR17471063371053793281"
}
```

## Example output

```json
{
  "advertiserId": "AR16735076323512287233",
  "advertiserName": "Nike, Inc.",
  "advertiserCountry": "US",
  "creativeId": "CR17471063371053793281",
  "format": "TEXT",
  "firstShown": "2024-03-09",
  "lastShown": "2026-10-24",
  "headline": "Nike Official Site",
  "description": "Shop the latest Nike styles.",
  "body": "Shop the latest Nike styles.",
  "displayDomain": "nike.com",
  "regions": ["CA"],
  "previewUrl": "https://tpc.googlesyndication.com/archive/simgad/6265887525695880208",
  "adLibraryUrl": "https://adstransparency.google.com/advertiser/AR16735076323512287233/creative/CR17471063371053793281",
  "source": "google_ads_transparency",
  "recordType": "ad",
  "scrapedAt": "2026-10-25T12:00:00+00:00"
}
```

```json
{
  "advertiserId": "AR16735076323512287233",
  "advertiserName": "Nike, Inc.",
  "creativeId": "CR13237700337168547841",
  "format": "IMAGE",
  "productTitle": "Nike Club Fleece Hoodie",
  "productBrand": "Nike",
  "imageUrl": "https://encrypted-tbn2.gstatic.com/shopping?q=tbn:ANd9GcExample",
  "displayDomain": "nike.com",
  "regions": ["US"],
  "impressionsMin": 1000,
  "impressionsMax": 2000,
  "source": "google_ads_transparency",
  "recordType": "ad",
  "scrapedAt": "2026-10-25T12:00:00+00:00"
}
```

## Use cases

- **Competitive ad monitoring** - track which creatives a competitor is running and how long they have been live.
- **Creative research** - collect text, image, and video ad examples by brand, country, or platform.
- **Media buying intelligence** - see which surfaces and regions a brand invests in.
- **Compliance review** - check where an advertiser's ads were recorded as shown.
- **Agency reporting** - build a prospect's ad history into an audit or pitch deck.
- **Dataset building** - export normalised ad creatives for analysis or model training.

## Limits and caveats

- **1,000-ad cap:** the actor reads 100 ads per page and stops at 1,000 unique ads per run, even if Google reports more for the advertiser or domain.
- **Date filtering is client-side:** Google does not expose an anonymous date-range parameter, so `startDate` and `endDate` only filter the slice the actor fetched. It may miss older ads outside that slice.
- **Impressions are partial:** impression ranges appear for political/issue ads and some display creatives, not for every ad.
- **Regions are partial:** `regions` reflects the per-creative stats Google returns, which is often one country and sometimes a longer subset. It is not a complete targeting list.
- **Video URLs expire:** direct `videoUrl` links are signed, tied to the resolving IP, and expire in about a day. Use `youtubeUrl` or `posterUrl` when you need a stable reference.
- **Copy is conditional:** most text ads expose a headline, description, and display domain; some do not. Image and video creatives usually have no text copy.
- **Anonymous results:** Google may show fewer ads to logged-out visitors than to signed-in users. This is a source limitation, not a missing filter.
- **Domain results span advertisers:** a domain search can return ads from several advertisers (brand owners, regional entities, and agencies). `maxAdsPerAdvertiser` applies to each one separately.
- **Political ads need a country:** Google's political/issue filter requires a concrete `region`; `anywhere` is rejected for that mode.

## FAQ

### What is the difference between the four modes?

`advertiser` takes an advertiser URL or `AR...` ID and returns that advertiser's creatives. `domain` searches all advertisers Google links to a domain. `search` resolves a brand or keyword to the best-matching advertiser and scrapes it. `creative` fetches one specific ad by URL or `CR...` ID.

### What is the difference between domain mode and search mode?

Domain mode queries Google by domain and returns ads from every associated advertiser. Search mode uses Google's advertiser suggestions and picks the best match for a name or keyword, which is useful when you do not know the domain.

### Why are impressions missing on many ads?

Google only publishes impression ranges for some creatives, mainly political/issue ads and certain display ads. When the field is absent, the source did not return a range; the actor does not estimate it.

### How many ads can I get per advertiser?

Up to 1,000 unique ads per run, read 100 at a time. Use `maxAdsPerAdvertiser` to cap each advertiser and `maxItems` to cap the whole run.

### Do the date filters search Google's full history?

No. Google does not expose a date-range parameter for anonymous searches. The actor filters the ads it fetched using their first and last shown dates. A narrow date window combined with a low `maxItems` can therefore miss older ads.

### Why do some records have no headline or description?

Google's preview content only exposes text copy for some text creatives. Image and video ads generally have no text copy. Missing fields are omitted from the record.

### Why does a video URL stop working?

Direct video files are signed to the IP that resolved them and expire quickly. Prefer `youtubeUrl` for a stable link, or `posterUrl` for a still image.

### Do I need a Google account, cookies, or a proxy?

No account or cookies are needed. The actor uses an Apify proxy automatically; `proxyConfiguration` is only an optional override.

### Is this affiliated with Google?

No. This is an independent third-party actor that reads the publicly accessible Google Ads Transparency Center. It is not affiliated with or endorsed by Google.
