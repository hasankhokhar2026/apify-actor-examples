# StubHub Live Event & Venue Finder by Category

StubHub lists tens of thousands of live events across sports, concerts and theater at any given time. This actor searches that catalog by artist, team, venue or keyword, or browses one of 36 built-in categories, and returns each matching event's title, date, venue and location. No login, no cookies required.

## What this actor does

- **Two modes:** `search` (free-text keyword) and `byCategory` (taxonomy browse — 36 sports/concert/theater categories)
- **Filters:** event date range, country, confirmed-date-only, active-listings-only
- **Empty fields are omitted** — every record only contains data StubHub actually provided

## Output per event

- `eventId` — StubHub's internal numeric event ID
- `eventTitle` — event / performer / team name
- `eventDate`, `eventTime`, `dayOfWeek` — human-readable date/time as shown on StubHub
- `eventDateTime` — UTC ISO 8601 timestamp (when StubHub resolves one server-side)
- `venueName`, `venueId`, `venueCity`, `venueState`, `venueLocation`
- `country`, `countryCode`
- `isDateConfirmed`, `isTimeConfirmed`, `hasActiveListings`
- `unavailabilityMessage` — StubHub's own reason text when the event currently has no active listings (e.g. `"Sold out for now"`), when shown
- `isDateTbd` — the exact date/time is still to-be-determined (event is scheduled but not fully pinned down)
- `eventCountdown` — StubHub's human-readable countdown/urgency message for the event (e.g. `"This weekend"`), when shown
- `allowPublicPurchase` — whether the general public can currently buy tickets for this event (`false` for e.g. presale-restricted or unlisted events)
- `isMultidayEvent` — event spans multiple days (festivals, multi-night residencies, etc.)
- `rescheduledFromDate` — the event's original date, when StubHub shows it was rescheduled (omitted when not rescheduled)
- `listingUrl` / `sourceUrl` — canonical StubHub event page
- `recordType: "event"`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `byCategory` |
| `searchQuery` | string | – | Free-text query (required for `search`; optional refinement for `byCategory`) |
| `category` | select | – | Event category (required for `byCategory`; optional search hint for `search` — StubHub does not guarantee results are restricted to it) |
| `country` | select | – | `US` or `CA` — records missing country data are not excluded |
| `dateFrom` / `dateTo` | string (ISO 8601) | – | Event date-range filter |
| `confirmedDateOnly` | bool | `false` | Only include events with a confirmed date (excludes TBD) |
| `activeListingsOnly` | bool | `false` | Only include events that currently have active ticket listings (excludes sold-out events) |
| `maxItems` | int | `20` | Hard cap on emitted records (1–100) |

### Example: search by artist

```json
{
  "mode": "search",
  "searchQuery": "Taylor Swift",
  "maxItems": 20
}
```

### Example: browse NBA tickets

```json
{
  "mode": "byCategory",
  "category": "6453",
  "maxItems": 20
}
```

### Example: search with category and date-range filters

```json
{
  "mode": "search",
  "searchQuery": "concert",
  "category": "260542",
  "dateFrom": "2026-08-01T00:00:00+00:00",
  "confirmedDateOnly": true
}
```

## Use cases

- **Ticket / availability monitoring** — track when new events go on sale for a favorite artist or team
- **Event discovery** — feed StubHub's live event catalog into an events aggregator
- **Fan tooling** — build alerts for a favorite artist's or team's tour dates
- **Market research** — track event density and calendar coverage by category

## Limitations

- **Result size per query:** StubHub's search endpoint (`/search?q=...`) returns up to ~20 results per keyword query server-side, regardless of `maxItems`. This is an upstream limit of the search-results page itself, not a bug — the actor faithfully reports every result the page returns. For broader coverage, run multiple `search` / `byCategory` calls with different keywords or categories.
- **Ticket price and ticket-count are not available.** StubHub renders these fields client-side, after the page loads, via a request gated by the site's DataDome bot-protection layer — the same protection that blocks individual event ticket-listing pages and StubHub's city/geography browse pages entirely (HTTP 403, confirmed from both a direct connection and Apify's free AUTO proxy). Rather than ship unreliable or fabricated pricing data, the actor focuses on the event metadata (title, date, venue, location) that StubHub serves reliably and consistently on every request.
- **`listingUrl` loads fine in a real browser but returns HTTP 403 to plain HTTP clients** (curl, `requests`, etc.) — StubHub's DataDome protection requires executing the page's JS challenge, which only a real browser (or a JS-capable engine) can do. The URL itself is correct and canonical; simply open it in a browser rather than fetching it programmatically.
- **No dedicated city-browse mode.** An earlier version of this actor included a `byCity` mode backed by StubHub's per-metro-area browse pages; those pages returned HTTP 403 consistently from Apify's cloud infrastructure (both direct and via the free AUTO proxy group), so the mode was removed rather than ship an unreliable feature. To find events in a specific city, include the city name in `searchQuery` (e.g. `"concerts in Chicago"`) — result relevance depends on StubHub's own search ranking.
- **Global coverage:** StubHub's search index spans many countries; the `country` filter currently offers a curated `US`/`CA` shortlist since those are the two markets consistently observed in test data. Events from other countries still appear in `search` / `byCategory` results (see the `country` / `countryCode` output fields) — they're just not filterable via the dropdown yet.
- **`category` is a search hint, not a guaranteed filter.** StubHub's `/search` endpoint does not reliably restrict results to the requested `categoryId` server-side — e.g. a `category=NBA` search can still return college-football or lacrosse events that merely match the keyword. Because StubHub never reports an individual event's own category in the scraped data, the actor does not fabricate a `category`/`categoryGroup` output field from the input filter; only fields StubHub actually returns per-event are included.

## FAQ

**Do I need a StubHub account or cookies?**  No. Both modes hit publicly server-rendered pages that don't require login.

**Why isn't there a ticket price field?**  StubHub only renders ticket pricing after client-side JavaScript executes a request that's protected against automated access (DataDome). The actor reports rich event metadata (title, date, venue, location) reliably instead of guessing at prices.

**What's the difference between `search` and `byCategory`?**  `search` runs StubHub's free-text search; `byCategory` runs the same search pre-filtered to one of StubHub's 36 curated categories (e.g. `NBA`, `Pop/Rock`, `Comedy`), optionally refined with your own `searchQuery`.

**Can I get more than 20 results for a single keyword?**  Not from a single call — that's StubHub's own page-level cap. Run multiple calls with different keywords/categories for broader coverage.

**How fresh is the data?**  Real-time — every run fetches StubHub's live search/browse pages directly.

**Can I exclude sold-out events?**  Yes — set `activeListingsOnly` to `true` to only return events that currently have active ticket listings.

**Is this affiliated with StubHub?**  No. This is an independent data extraction tool and has no connection to StubHub or viagogo.
