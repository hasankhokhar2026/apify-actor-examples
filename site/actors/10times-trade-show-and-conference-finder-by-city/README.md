# 10times Trade Show & Conference Finder by City

10times.com lists trade shows, conferences, workshops, and festivals worldwide, searchable by city, country, category, and date. This actor pulls event listings from 10times given direct event URLs, a city, or a free-text search, and returns one structured record per event.

## What this actor does

- Scrapes individual event pages when given direct 10times event URLs.
- Enumerates events from a city or listing page, or from a free-text search query.
- Filters discovered events by country, event type, category, online-only status, and date range.
- Extracts name, dates, venue/location, organizer, pricing, categories, and attendance signals (followers, rating, estimated visitor/exhibitor counts) from each event page.
- Fields that aren't present on a given event's page are left out of that event's record.

## Output per event

| Field | Description |
|---|---|
| `type` | Always `event_10times`. |
| `url` | Event page URL. |
| `slug` / `id` | 10times URL slug for the event. |
| `name` | Event name. |
| `description` | Event description. |
| `startDate` / `endDate` | Event start and end dates. |
| `eventStatus` | Event status (e.g. scheduled, cancelled, postponed), when published. |
| `eventAttendanceMode` | Attendance mode (e.g. in-person, online, mixed), when published. |
| `image` | Event cover image URL. |
| `tags` | Keyword tags from the event page's metadata. |
| `categories` | Industry/category labels shown on the event page. |
| `edition` | Numbered edition of the event (e.g. `5` for "5th edition"), when stated. |
| `frequency` | Recurrence word parsed from the page (e.g. Annual, Biennial), when stated. |
| `followers` | Follower/interested count shown on the event page. |
| `rating` | Rating out of 5, when the page shows one. |
| `estimatedVisitors` | Estimated visitor/attendee count, when published. |
| `estimatedExhibitors` | Estimated exhibitor count, when published. |
| `ogType` | Open Graph type of the page, when present. |
| `countryCode` | ISO 2-letter country code for the event, derived from the listing page it was discovered through. May be absent for events found in worldwide mode. |
| `location` | Object with `name`, `addressLocality`, `addressRegion`, `addressCountry`, `streetAddress`, `postalCode`, `latitude`, `longitude` — only the keys the event page provides. |
| `organizer` | Object with `name`, `url`, `email`, `telephone` — only the keys the event page provides. |
| `pricing` | Object with `price`, `priceCurrency`, `availability`, `url` — only when the event page publishes ticket pricing. |
| `scrapedAt` | ISO 8601 timestamp of when this actor fetched the record. |

If every URL in a run comes back blocked, the actor writes a single record of `type: "event_10times_blocked"` with the attempted URLs instead of leaving the dataset empty.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `startUrls` | Array of strings | – | 10times URLs. Event URLs (`https://10times.com/<event-slug>`) are scraped directly; city/listing URLs (`https://10times.com/<city>-<country>`) are enumerated for events. |
| `query` | String | – | Free-text search term, used to build a 10times search URL. |
| `city` | String | – | City slug (e.g. `berlin`, `new-york`) used to build a 10times city listing URL. |
| `country` | String (select) | `"WW"` | Restrict results to this country. `WW` = worldwide. When set to a specific country, events from other countries are dropped and that country's city listing pages are followed automatically to find more matches. Options: Worldwide, US, UK, Germany, France, Spain, Italy, Netherlands, Australia, Canada, Japan, India, Brazil, Mexico, China, Singapore. |
| `eventType` | String (select) | `"all"` | Keep only events matching this type: `tradeshow`, `conference`, `workshop`, `festival`, or `all`. |
| `onlineOnly` | Boolean | `false` | Keep only online/virtual events. |
| `startDate` | String | – | Keep only events starting on or after this date (`YYYY-MM-DD`). |
| `endDate` | String | – | Keep only events starting on or before this date (`YYYY-MM-DD`). |
| `category` | String (select) | `"all"` | Keep only events matching this industry category (e.g. `technology`, `health`, `building`). |
| `sortBy` | String (select) | `"date"` | Accepted but not currently applied to the output order (see FAQ). |
| `sortType` | String (select) | `"asc"` | Accepted but not currently applied to the output order (see FAQ). |
| `maxItems` | Integer | `20` | Maximum number of events to return. |

### Example: enumerate a city's events in one country

```json
{
    "city": "berlin",
    "country": "DE",
    "maxItems": 50
}
```

### Example: free-text search filtered by type and date

```json
{
    "query": "artificial intelligence",
    "eventType": "conference",
    "startDate": "2026-01-01",
    "endDate": "2026-06-30",
    "maxItems": 30
}
```

### Example: scrape specific event pages directly

```json
{
    "startUrls": [
        "https://10times.com/ces-las-vegas",
        "https://10times.com/mwc-barcelona"
    ]
}
```

## Use cases

- **Event calendar building** — pull upcoming trade shows and conferences for a city, industry, or date window.
- **Exhibitor/sponsor prospecting** — collect organizer contact details and estimated visitor/exhibitor counts to prioritize outreach.
- **Travel and venue planning** — gather venue location, dates, and attendance mode (online/in-person) for events you may attend or sponsor.
- **Competitive and industry tracking** — monitor which conferences recur annually in a category and how their follower counts or ratings change.
- **Market research feeds** — export structured event data into a spreadsheet or BI tool for industry-event landscape reports.

## FAQ

**Can I scrape a specific event page directly?**
Yes — pass its URL in `startUrls`; it's scraped directly without needing a city or search.

**Why do some events lack a `countryCode`?**
10times event pages don't always carry a country signal directly; this actor derives it from the listing page an event was discovered through. Events found via a specific `country` filter always carry that code; events found in worldwide mode sometimes don't.

**What happens if I set `country` to a specific value?**
Only events located in that country are kept, and the actor automatically follows that country's city listing pages to surface more matches beyond whatever a general or worldwide listing returns.

**Why is my filtered result smaller than I expected?**
Narrow combinations of `country`, `eventType`, and `category` can legitimately have few matching events, since these filters compound.

**What does the "blocked" record mean?**
If 10times blocks every URL requested in a run, the dataset gets one record with `type: "event_10times_blocked"` and the list of URLs that failed, instead of coming back empty.

**Does `sortBy`/`sortType` reorder the output?**
Not currently — events are emitted in the order they're discovered/scraped, regardless of `sortBy`/`sortType`. Sort the dataset yourself after export if you need a specific order.

**Is this affiliated with 10times?**
No. This actor reads public 10times.com event pages and is not affiliated with or endorsed by 10times.
