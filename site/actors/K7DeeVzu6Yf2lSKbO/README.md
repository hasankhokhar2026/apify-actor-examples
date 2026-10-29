# Google Maps Photo Gallery Extractor by Category

Pull every photo and video thumbnail that Google Maps publicly shows for a place — full-resolution image URLs, contributor names, captions, dimensions, and the gallery category tab each one came from (Menu, Food & Drink, Outdoor, and more).

## What this actor does

- Reads a place's public photo gallery by place URL or canonical Place ID and returns up to the number of photos you request
- Filters to a single gallery tab, such as Menu, Food & Drink, Outdoor, Indoor, or Videos, instead of the full mixed gallery
- Captures each photo's contributor name and profile link, observed upload-date text, caption, and tags when the contributor published them
- Distinguishes short video clips from photos and reports their length as Google displays it
- Omits any field Google doesn't publicly expose for a given photo rather than returning a null or guessed value

## Output per photo

| Field | Description |
|---|---|
| `recordType` | Always `"photo"` |
| `photoId` | Google's photo identifier |
| `photoIndex` | Observed position in the active gallery/category tab; a useful ordering hint, but not guaranteed stable across runs |
| `photoUrl` | Full-resolution photo URL |
| `thumbnailUrl` | Thumbnail-size photo URL |
| `category` | The gallery tab this photo came from, included only when a specific (non-"all") tab was visibly selected |
| `contributorName` / `contributorUrl` | Name and profile link of whoever uploaded the photo, when shown |
| `uploadDateOriginal` | Upload date exactly as displayed, e.g. "2 months ago" |
| `uploadDate` | ISO 8601 upload date, only when Google publishes a complete calendar date |
| `caption` | Caption text, when the contributor added one |
| `tags` | Tags attached to the photo, when published |
| `width` / `height` / `aspectRatio` / `orientation` | Original dimensions and derived aspect ratio/orientation |
| `isVideo` | `true` when the item is a short video clip rather than a still photo |
| `videoDuration` | Clip length exactly as Google displays it, e.g. "0:29" — only present when `isVideo` is true |
| `businessName` | Name of the place the gallery belongs to |
| `placeId` | Canonical Google Place ID (`ChIJ…`), when that's the form Google exposes |
| `featureId` | Legacy Google feature ID (`0x…:0x…`), when that's the form Google exposes instead |
| `placeUrl` | The place's Google Maps URL, echoed on every row so the dataset stays joinable |
| `sourceUrl` | URL the record was read from |
| `scrapedAt` | UTC timestamp when the record was scraped |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `placeUrl` | string | – | Google Maps place URL to read photos from. Country domains, short links and tracking parameters are normalized. Required unless `placeId` is set. |
| `placeId` | string | – | Canonical Google Place ID beginning with `ChIJ`; use instead of `placeUrl` when available |
| `maxPhotos` | integer | 100 | Maximum number of photos to extract (1-100000); the place's gallery may expose fewer |
| `photoCategory` | string | all | Gallery tab to read: all, by_owner, by_visitors, food_and_drink, outdoor, indoor, menu, or videos |
| `enrichDetails` | boolean | true | Read each photo's contributor name/URL, upload date, dimensions, caption and tags. Turn off for faster, thumbnail-level rows (photo/thumbnail URL, business context, category, video flag and duration) only. |
| `proxyConfiguration` | object | Apify Proxy enabled | Optional proxy override |

### Example: full enriched gallery

```json
{
  "placeUrl": "https://www.google.com/maps/place/Empire+State+Building/@40.7484405,-73.9878584,17z/",
  "maxPhotos": 50,
  "photoCategory": "all",
  "enrichDetails": true
}
```

### Example: fast export of visitor photos only

```json
{
  "placeUrl": "https://www.google.com/maps/place/Sushi+no+Midori/@35.6704396,139.7596577,17z/",
  "maxPhotos": 1000,
  "photoCategory": "by_visitors",
  "enrichDetails": false
}
```

### Example: menu photos by Place ID

```json
{
  "placeId": "ChIJabtoT7hlwokRLECK0SW3_8I",
  "maxPhotos": 500,
  "photoCategory": "menu"
}
```

## Use cases

- **Visual asset libraries** — build a photo set for a restaurant, hotel, or venue
- **Menu and interior monitoring** — track how a place's menu or interior photos change over time
- **UGC sourcing** — pull contributor photography for travel or food content
- **Place previews** — power a "what does this place look like" preview in your own app
- **Lead enrichment** — add visual context to a business-lead dataset

## FAQ

**Do I need to log in or provide cookies?**
No. The actor reads Google Maps' public photo gallery; no login or cookies are accepted. A proxy is only used automatically as a fallback if direct access doesn't return a usable gallery.

**Why does `category` sometimes not appear on a row?**
It's only set when a specific tab (not "all") was visibly selected for that photo. If you request a specific category and Google doesn't expose that tab for the place, the run reports the problem rather than mislabeling "all" photos under the wrong category.

**What does `enrichDetails` change?**
With it on, each photo's contributor, upload date, dimensions, caption and tags are read in addition to the photo and thumbnail URLs. With it off, you get faster thumbnail-level rows without those extra fields.

**Are videos included?**
Yes, when `photoCategory` is "all" or "videos". Video rows have `isVideo: true` and a `videoDuration` showing the clip length as Google displays it.

**Why might I get fewer photos than `maxPhotos`?**
A place's public gallery may simply contain fewer photos than you requested, or fewer for the specific category chosen; the actor returns everything available rather than padding the output.

**Is this affiliated with Google?**
No. This actor reads Google Maps' public pages and is not affiliated with, endorsed by, or sponsored by Google.
