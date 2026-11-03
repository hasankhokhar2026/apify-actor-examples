# Google Maps Photo Gallery Extractor by Category

Collect the public photo and video gallery of Google Maps places without a login, cookie or API key. Paste place links, Place IDs, feature IDs, CIDs or business names, or search for places by keyword, then receive one dataset row per photo, video or nearby Street View panorama with its image link, dimensions, contributor, upload date, owner/visitor flag and place context.

Google's public gallery exposes a large but finite sample of each place. This actor walks that sample to its natural end — a 30-place survey ranged from 4 to 1,983 media items, median 326 — instead of stopping at the first handful. Every URL in the dataset is a direct Google-hosted image or video link that can be fetched without a Referer or cookie.

## What this actor does

- Reads photos and videos for one or many places using URLs, share links, `ChIJ...` Place IDs, `0x...:0x...` feature IDs, numeric CIDs or business names
- Searches Google Maps by keyword and reads the gallery of each matching place
- Filters by photos, videos, business-owner photos, visitor photos or nearby Street View panoramas
- Adds contributor name, profile link and ID, exact upload date, image dimensions, video download link and video length when Google publishes them
- Marks owner-uploaded media so official business photos can be separated from customer contributions
- Exposes the place identity, categories, address and coordinates on every row so the data joins cleanly to other Google Maps datasets
- Omits a field when Google does not publish it for that item instead of returning null or a guess

## Output per media item

| Field | Description |
|---|---|
| `recordType` | Always `"photo"` for backward compatibility |
| `photoId` | Google's media identifier; use it to deduplicate |
| `photoIndex` | 0-based position in the returned media list for that place |
| `photoUrl` | Highest-resolution image URL (the poster frame for videos) |
| `thumbnailUrl` | Small preview image URL |
| `businessName` | Name of the place |
| `placeId` | Canonical `ChIJ...` Place ID when Google exposes it |
| `featureId` | Legacy `0x...:0x...` feature ID |
| `placeUrl` | Google Maps URL of the place |
| `category` | The selected filter when it is not `all` |
| `mediaType` | `photo`, `video` or `streetView` |
| `isVideo` | `true` for a video |
| `isStreetView` | `true` for a nearby Street View panorama |
| `contributorName` | Public contributor name |
| `contributorUrl` | Contributor profile link |
| `contributorId` | Contributor profile identifier |
| `contributorAvatarUrl` | Contributor avatar link |
| `isOwnerPhoto` | `true` when the contributor matches the business owner, `false` for visitor media; omitted when owner attribution is unavailable |
| `uploadDate` | ISO 8601 upload timestamp |
| `uploadDateOriginal` | Upload date as Google displays it, such as `Oct 2026` |
| `width`, `height` | Original pixel dimensions |
| `aspectRatio`, `orientation` | Derived aspect ratio and `landscape` / `portrait` / `square` |
| `latitude`, `longitude` | Media coordinates when Google publishes them |
| `videoUrl` | Direct MP4 link for videos |
| `videoDuration` | Video length as `m:ss` or `h:mm:ss` |
| `videoDurationSeconds` | Video length in seconds |
| `caption` | Caption when the contributor published one |
| `tags` | Retained for backward compatibility; Google's public photo data does not expose tags |
| `placeCategory`, `placeCategories` | Primary and full place category list |
| `placeAddress` | Place address |
| `searchQuery` | The query that found the place, in search mode |
| `sourceUrl` | Place URL used as the record's source (legacy meaning) |
| `scrapedAt` | UTC timestamp when the record was scraped |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `place` | `place` for specific places, `search` to discover places by keyword |
| `placeUrls` | array | `[]` | Place URLs, share links, `ChIJ...` IDs, `0x...:0x...` feature IDs, numeric CIDs or business names (mode=place) |
| `searchQueries` | array | `[]` | Keyword queries such as `coffee shops in New York` (mode=search) |
| `maxPlacesPerQuery` | integer | `20` | Places to take from each query (1-100) |
| `maxPhotos` | integer | `100` | Maximum media items per place (1-10000). The actor stops earlier when Google's public sample ends |
| `photoCategory` | string | `all` | `all`, `photos`, `videos`, `by_owner`, `by_visitors` or `street_view` |
| `enrichDetails` | boolean | `true` | Read contributor, exact date, caption, video link and video length |
| `language` | string | `en` | Language for place names, categories and dates |
| `imageSize` | string | `original` | Main photo URL size: `original`, `large` (~1600 px), `medium` (~800 px) or `thumbnail` (~200 px) |
| `minWidth` | integer | `0` | Drop media narrower than this; 0 keeps every width. Media with unknown dimensions are kept |
| `minHeight` | integer | `0` | Drop media shorter than this; 0 keeps every height. Media with unknown dimensions are kept |

### Example: a batch of place links

```json
{
  "mode": "place",
  "placeUrls": [
    "https://www.google.com/maps/place/Empire+State+Building/@40.7484405,-73.9878584,17z/data=!3m1!4b1!4m6!3m5!1s0x89c259a9b3117469:0xd134e199a405a163!8m2!3d40.7484405!4d-73.9878584",
    "https://maps.app.goo.gl/KZLn9FA3aokoiVaP8"
  ],
  "maxPhotos": 100,
  "photoCategory": "all"
}
```

### Example: search for places, then read their galleries

```json
{
  "mode": "search",
  "searchQueries": ["coffee shops in New York", "bakeries in Toronto"],
  "maxPlacesPerQuery": 10,
  "maxPhotos": 50,
  "photoCategory": "photos"
}
```

### Example: owner photos only, high resolution

```json
{
  "mode": "place",
  "placeUrls": ["ChIJhxCTWhJZwokRIAYkdUUdRz0"],
  "photoCategory": "by_owner",
  "maxPhotos": 100,
  "minWidth": 1200
}
```

### Example: videos and nearby Street View

```json
{
  "mode": "place",
  "placeUrls": ["0x89c259125a931087:0x3d471d4575240620"],
  "photoCategory": "videos",
  "maxPhotos": 50
}
```

## Use cases

- **Menu and storefront monitoring** — collect photos for a restaurant, café or retail chain and compare owner media with customer uploads
- **Hospitality and real-estate galleries** — build visual datasets for hotels, venues and apartment listings from public place photos
- **Brand consistency audits** — track the owner/visitor photo mix and freshness across every branch of a business
- **Computer-vision datasets** — full-resolution image URLs with dimensions and place/category context for training and evaluation
- **Local SEO research** — compare how competing places present themselves visually, and how recently their galleries changed
- **Travel and directory enrichment** — add authentic location imagery to city guides, maps and booking products

## FAQ

**Do I need a Google account, cookies or an API key?**
No. The actor reads Google Maps' public place and gallery pages. No login, cookie, API key or proxy configuration is needed.

**Why do I get fewer items than `maxPhotos`?**
Google's signed-out gallery exposes a finite public sample of each place. The actor walks the whole sample it is given (the 30-place survey ranged 4-1,983 items, median 326), but the public sample can be smaller than the requested cap, and some places simply have very few public photos.

**Why are the category tabs from the Google Maps website not all available?**
The full signed-in gallery and its Menu, Food & drink, Vibe, Rooms and Amenities tabs require a Google login. The public surface exposes media type and public contributor information, so this actor offers `photos`, `videos`, `by_owner`, `by_visitors` and `street_view` filters instead of claiming tabs it cannot read anonymously.

**How are owner photos identified?**
Google publishes the business owner's profile separately from the photo contributor. When both are present, `isOwnerPhoto` is `true` or `false`; when Google omits the owner profile, the flag is omitted and media with unknown owner status are not returned by the owner or visitor filter.

**Are videos included?**
Yes. Video rows have `isVideo: true`, a direct `videoUrl` MP4 link when Google provides one, and a video length when it can be read from the file.

**What is the `street_view` filter?**
It returns Street View panoramas near the place's coordinates. These are nearby 360° imagery rather than photos from the place's own gallery; `isStreetView` marks them, and they do not carry the place's `placeId` or `featureId`.

**Why is `caption` or `tags` missing on many rows?**
Most Google Maps photos have no caption or tags. The field appears only when the contributor or Google published it.

**Are the image and video links permanent?**
They are public Google-hosted URLs that work without a Referer or cookie. Google can change or remove a photo at any time, so re-run the actor when you need a fresh copy.

**Is this affiliated with Google?**
No. This actor reads publicly visible Google Maps data and is not affiliated with, endorsed by or sponsored by Google.
