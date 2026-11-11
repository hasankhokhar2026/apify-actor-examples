# Yelp Business Profile, Hours & Menu Extractor

Yelp business pages carry far more than a star rating — hours, services, photo galleries, owner replies, and sometimes a full menu. This actor pulls all of it from a Yelp search or a direct business URL, alongside customer reviews with per-review dates and reaction counts.

## What this actor does

- Searches Yelp by keyword and location, or scrapes specific businesses via direct URL
- Returns business profile data: name, phone, address, categories, price range, cuisine, website, description
- Extracts customer reviews with text, star rating, per-review date, attached photos, and Useful/Funny/Cool reaction counts
- Pulls hours of operation, services and amenities, geographic coordinates, photo galleries by category, owner replies, and (for some restaurants) a full menu
- Empty fields are omitted from records — no empty strings, empty arrays, or null values

## Output per business

- `directUrl` — full Yelp URL of the business page
- `bizId` — Yelp business slug identifier
- `name`, `description` — business name and description
- `categories` — business categories (e.g. "Pizza", "Italian")
- `type` — business type (e.g. "Restaurant", "LocalBusiness")
- `phone`, `website` — contact details
- `reviewCount`, `aggregatedRating` — total reviews and average star rating
- `priceRange` — price level (`$`, `$$`, `$$$`)
- `cuisine` — cuisine type, for restaurants
- `images` — business hero image URLs
- `address` — `streetAddress`, `addressLocality`, `addressRegion`, `postalCode`, `addressCountry`
- `coordinates` — `latitude`, `longitude`
- `hours` — one entry per weekday (e.g. `"Mon": "11:00 AM - 10:00 PM"`)
- `services` — amenities and services (takeout, delivery, parking, and more)
- `photoCategories` — photo URLs grouped by category (food, inside, outside, menu)
- `menu` — menu items as `{name, price, description}`, for restaurants with a published menu
- `claimStatus` — `claimed` or `unclaimed`
- `ownerReplies` — business responses to reviews as `{reviewDate, reply, replyDate}`
- `reviews` — customer reviews (see below)
- `scrapedAt` — when the record was scraped

### Review fields

- `reviewerName` — the reviewer's display name, when shown
- `date` — review date, anchored to that specific review
- `rating` — star rating (`1`–`5`)
- `text` — review text
- `photos` — URLs of photos attached to the review
- `isUsefulCount`, `isFunnyCount`, `isCoolCount` — reaction counts on the review

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchTerms` | Array | – | Search queries, e.g. `pizza`, `plumber`, `hair salon`. Combined with each entry in `locations`. |
| `locations` | Array | – | Locations to search, e.g. `New York, NY`, `Los Angeles, CA`. |
| `directUrls` | Array | – | Direct Yelp business page URLs to scrape instead of searching. |
| `searchLimit` | Integer | `10` | Maximum business results to collect per search query (1–100). |
| `reviewLimit` | Integer | `5` | Maximum reviews to collect per business (0–50). Set to `0` to skip reviews. |
| `fetchPhotos` | Boolean | `true` | Extract gallery photos grouped by category. |
| `fetchHours` | Boolean | `true` | Extract hours of operation. |
| `fetchMenu` | Boolean | `false` | Attempt to extract menu items for restaurants. |
| `proxy` | Object | `{"useApifyProxy": true, "apifyProxyGroups": ["RESIDENTIAL"]}` | Required. Proxy configuration used to fetch Yelp pages. |

You must provide at least one of `searchTerms` or `directUrls`.

## Example input

### Search for businesses

```json
{
    "searchTerms": ["pizza", "sushi"],
    "locations": ["New York, NY", "San Francisco, CA"],
    "searchLimit": 5,
    "reviewLimit": 3,
    "fetchPhotos": true,
    "fetchHours": true,
    "fetchMenu": false,
    "proxy": {
        "useApifyProxy": true,
        "apifyProxyGroups": ["RESIDENTIAL"]
    }
}
```

### Scrape specific businesses with menus

```json
{
    "directUrls": [
        { "url": "https://www.yelp.com/biz/prince-street-pizza-new-york-2" },
        { "url": "https://www.yelp.com/biz/joes-pizza-new-york" }
    ],
    "reviewLimit": 10,
    "fetchMenu": true,
    "proxy": {
        "useApifyProxy": true,
        "apifyProxyGroups": ["RESIDENTIAL"]
    }
}
```

## Use cases

- Collecting business contact information — phone, website, and address — for outreach
- Comparing ratings, price points, and services across similar businesses in a market
- Evaluating business density, pricing, and customer sentiment by neighborhood
- Tracking menus, cuisine types, and hours across restaurant competitors
- Monitoring customer sentiment and owner responses to reviews over time
- Auditing how businesses rank in Yelp search results for target keywords

## FAQ

**Do I need a proxy?**
Yes. A residential proxy is required because Yelp blocks requests from non-residential IP ranges.

**How many reviews can I get per business?**
Up to 50 via `reviewLimit`, though Yelp itself only publicly displays around 30 reviews per business.

**Why are some businesses missing a menu?**
Yelp's menu feature is opt-in and mostly limited to US restaurants, so many businesses simply don't have one published — the `menu` field is omitted when that's the case.

**Why are some fields missing from my output?**
Fields are omitted whenever Yelp doesn't have that data for a business, rather than being filled with an empty placeholder.

**Can I scrape businesses outside the US?**
Yes. Yelp operates in many countries and international business pages work the same way, though some fields like menu and certain services are more US-centric.

**What's the difference between `searchTerms`/`locations` and `directUrls`?**
`searchTerms` combined with `locations` runs a Yelp search and collects up to `searchLimit` results per combination; `directUrls` fetches exact businesses you already have a link for.

**Is there a limit on how many businesses one run can scrape?**
Yes — a single run scrapes at most 100 businesses total, combining results from all search term/location pairs and direct URLs.

**Is the data fresh?**
Yes — every run fetches live data directly from Yelp at the time it runs.

**Does this require login or cookies?**
No. Only publicly available Yelp data is collected, with no account or authentication needed.
