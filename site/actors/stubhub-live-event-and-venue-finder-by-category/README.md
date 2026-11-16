# StubHub Live Event & Venue Finder by Category

StubHub lists thousands of sports, concert, theater and festival events at any time. This actor
turns the public search and metro-explore data of the StubHub US/Canada marketplace
(`www.stubhub.com` and `www.stubhub.ca`) into clean event records: title, date, venue, city,
country, category, availability flags, an optional lowest from-price, and a direct event link.
It runs with plain HTTP, no login, no cookies, no proxy setup, and no browser.

## What this actor does

- **Search by keyword** — artist, team, venue or event name. Paginates past the first page and
  splits large result sets into date windows to get closer to StubHub's full index.
- **Explore by city** — 36 verified metro areas across North America, Europe, Australia and Asia,
  with a 1-500 km radius, top-level category filter, and date range.
- **Filter** by date, country, confirmed-date-only, and active-listings-only.
- **Optional from-price** — lowest current price for active US/Canada listings, in USD or CAD.
- **Omit-empty output** — fields StubHub does not provide for an event are left out, never set to
  `null`, `""`, `"N/A"` or another sentinel.

## Output per event

| Field | Meaning |
|---|---|
| `eventId` | StubHub numeric event ID |
| `eventTitle` | Event, performer or matchup name |
| `eventDate`, `eventTime`, `dayOfWeek` | Date/time text as StubHub shows it |
| `eventDateTime` | UTC ISO 8601 timestamp when the search payload has one |
| `eventDateIso` | Event date as `YYYY-MM-DD`, taken from the dated event URL or timestamp |
| `venueName`, `venueId` | Venue |
| `venueCity`, `venueState`, `venueLocation` | Venue city/state and full location text |
| `country`, `countryCode` | Country name and ISO code when resolvable |
| `categoryId` | StubHub category/performer ID when the payload or search result provides one |
| `imageUrl` | Event image (city explore records) |
| `priceClass` | StubHub price class (city explore records) |
| `priceFrom`, `priceCurrency` | Lowest current from-price and currency when available |
| `isDateConfirmed`, `isTimeConfirmed`, `isDateTbd` | Date/time confirmation flags |
| `hasActiveListings` | Whether StubHub reports active listings (search records) |
| `allowPublicPurchase` | Whether public purchase is allowed |
| `isMultidayEvent`, `isParkingEvent` | Event type flags |
| `eventCountdown`, `rescheduledFromDate` | StubHub's countdown text / original date when shown |
| `unavailabilityMessage` | StubHub's own no-tickets message when the payload includes it |
| `listingUrl`, `sourceUrl` | Canonical event page |
| `recordType`, `scrapedAt` | Record metadata |

Every record is the same shape unless a field is genuinely absent for that event.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `search` | `search` by keyword, `byCity` metro explore, or legacy `byCategory` browse |
| `searchQuery` | text | - | Artist, team, venue or event name (required for `search`; optional refinement for `byCategory`) |
| `city` | select | `New York` | Metro area (used by `byCity`) |
| `browseCategory` | select | `all` | `all`, `sports`, `concerts`, `theater` or `festivals`; a real `tlcId` filter only in city explore, otherwise a price hint |
| `radiusKm` | integer | `50` | City search radius, 1-500 km |
| `category` | select | - | Required for legacy `byCategory`; optional search hint otherwise. StubHub search does not strictly filter by leaf category |
| `country` | select | - | 40 observed country codes, applied client-side; the request `cc` value is only a locale hint |
| `dateFrom` / `dateTo` | text | - | `YYYY-MM-DD` or ISO 8601; used in server windows and checked again per record |
| `sort` | select | `relevance` | `relevance` or `date` for search; city explore is always date-ordered |
| `includePrices` | boolean | `true` | Fetch lowest from-price for US/Canada records |
| `maxItems` | integer | `20` | Hard cap on saved records, 1-5000 |
| `confirmedDateOnly` | boolean | `false` | Exclude TBD-date events |
| `activeListingsOnly` | boolean | `false` | Exclude search records without active listings; city records pass through |

The daily prefill searches `Taylor Swift` with category `260542`, saves at most 3 records and
turns price requests off.

### Example: search an artist

```json
{
  "mode": "search",
  "searchQuery": "Taylor Swift",
  "maxItems": 100,
  "includePrices": false
}
```

### Example: explore concerts in New York

```json
{
  "mode": "byCity",
  "city": "New York",
  "browseCategory": "concerts",
  "radiusKm": 10,
  "dateFrom": "2026-11-15",
  "dateTo": "2026-12-15",
  "includePrices": true,
  "maxItems": 50
}
```

### Example: search with date and country filters

```json
{
  "mode": "search",
  "searchQuery": "Hamilton",
  "country": "US",
  "dateFrom": "2026-11-15",
  "dateTo": "2027-01-31",
  "sort": "date",
  "includePrices": true,
  "maxItems": 20
}
```

### Legacy category mode

`"mode": "byCategory"` remains a visible third option for older tasks. It maps to the search flow
using the category title as the query, exactly as before. `category` is required for this mode;
`searchQuery` is an optional refinement. This is a query hint, not a server-side category filter.

## Prices

- Prices come from StubHub's public `EventPrices` endpoint, requested in batches of 20 with
  browser TLS impersonation.
- US and Canada records, plus records whose country cannot be resolved, are requested.
  `www.stubhub.com` prices are USD; `www.stubhub.ca` prices are CAD.
- Search records without active listings are not requested. City explore has no reliable
  availability flag, so its records are requested and unpriced ones stay unpriced.
- The price is a lowest "from" price, not a seat quote. Far-future events, deferred prices and
  events without inventory simply omit `priceFrom`/`priceCurrency`.
- Pricing adds requests and time; turn `includePrices` off for the fastest, cheapest run.

## Search pagination and date windows

StubHub's search JSON returns 20 items per page and stops after roughly 500 rows even when it
reports a higher total. This actor:

1. Paginates page by page.
2. If a query reports more rows than the page cap, splits the requested date range in half and
   repeats, deduplicating by event ID.
3. Stops on `maxItems`, an empty page, or source exhaustion.

In live probes this recovered 629 of 634 unique Taylor Swift events. A single day/window that
contains more than the cap can still under-deliver; narrow the date range or add a category hint
to split further. Relevance ordering across multiple date windows is approximate; date ordering
is exact within each window.

## City explore

City explore uses StubHub's public Explore endpoint with `Size=1000`. It supports 36 verified
metros and top-level categories. Explore reports a total that can include grouped/venue entries,
so row counts can be slightly below the displayed total. Empty pages with missing `total` or
`remaining` are retried and skipped rather than treated as the end; pagination stops on a
positive `remaining: 0`, two consecutive empty pages after retries, `maxItems`, or the hard
page cap. This recovers rows after transient empty pages, including a 996 -> empty -> 587
sequence observed for New York.

## Limitations

- **Event-page scope is the US/Canada marketplace (`.com`/`.ca`).** Search on `.com` still returns
  global inventory, but event-page/listing enrichment is scoped to `.com`/`.ca`. Country hosts
  such as `www.stubhub.co.uk`, `www.stubhub.de` and `www.stubhub.ie` expose address, venue and
  listing-level data through `__INITIAL_STATE__` and `/bfx/api/catalog/events/v3`. That is a
  separate market surface and is not implemented here; it is a documented future/scope gap, not
  a claim that the data is unreachable.
- **No ticket-level inventory on `.com`/`.ca`.** These event pages return HTTP 403 to automated
  HTTP clients behind DataDome. This actor does not fetch them, so it cannot provide section,
  row, seat, quantity, listing count or deal score there. It does not fabricate them.
- **No venue address, map, seating chart, lineup, parking or set times on `.com`/`.ca`.** Those
  live on the blocked event pages. Country hosts are a separate, unimplemented surface.
- **No URL/ID lookup mode.** Searching a raw event ID returned no matches in probes, and
  slug-derived lookup was inconsistent. Use the event title or performer name.
- **`category` is a hint, not a guaranteed filter.** StubHub search ignores leaf category IDs as
  a strict server-side filter. Use `mode=byCity` + `browseCategory` when you need a true
  top-level category browse.
- **`activeListingsOnly` applies to search records.** Explore's `hasActiveListings` flag was
  false for every event in a 990-event probe, so city records omit it and the filter passes
  city records through.
- **City sort is always date order.** Explore's relevance sort returned HTTP 500 in probes.
- **Country filtering is client-side.** Search filters on StubHub's `countryCode` field; city
  records use the country parsed from the venue location. The request `cc` hint is a locale
  value and did not change result sets in probes. Events whose country cannot be resolved are
  not excluded.
- **Date range defaults.** Search defaults to today through five years ahead; city explore
  defaults to today through 90 days ahead. Set `dateFrom`/`dateTo` for other horizons. Past
  events are not fetched.
- **Event price currency is marketplace-based.** Only USD and CAD are emitted.

## FAQ

**Do I need a StubHub account, cookies or a proxy?** No. The actor uses public endpoints and
plain HTTP.

**Why is there no ticket price for some events?** StubHub only returns a from-price when the
marketplace has an active, quotable listing. Far-future, deferred, inactive and non-US/Canada
records are not price-requested or return no price; the fields are then omitted.

**Can I get more than 500 results for one artist?** Usually yes, because the actor splits large
queries into date windows and deduplicates. A single window above StubHub's cap is the residual
limit.

**Can I get every event in a city?** City explore paginates the public metro feed. The feed's
reported total can include grouped/venue entries, so the returned row count may be slightly
lower.

**Why does `hasActiveListings` not appear on city records?** StubHub's Explore feed reports
`false` for every event we probed, including events with known inventory, so the field is not
reliable there and is omitted.

**Does this actor cover the UK, Germany or Ireland?** Not currently. This revamp targets the
US/Canada marketplace (`.com`/`.ca`). Country hosts have a different address/venue/listing
surface and are tracked as a future scope gap.

**Is this affiliated with StubHub?** No. This is an independent data extraction tool.
