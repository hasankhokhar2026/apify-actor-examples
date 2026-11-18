# Skiplagged Route Fare & Booking Provider Finder

Scrape **Skiplagged** flight fares — including the hidden-city and self-transfer itineraries Skiplagged is known for — and get one clean record per itinerary with the price, airlines, flight numbers, layovers, stops, hidden-city flag and every booking provider that quotes the fare. Search one route, batch many routes in one run, paste Skiplagged search links, or pull a flexible-date price calendar. No login, no cookies, no proxy setup.

## What this actor does

- **Four modes:** `search` (one route), `byRoutes` (many routes in one run), `byUrls` (paste Skiplagged flight-search links), `calendar` (daily prices for the next 61 days)
- **Hidden-city aware:** every itinerary records whether the ticket ends beyond your destination, where you actually get off, and the true ticketed airport
- **Self-transfer aware:** `virtualInterline` marks separately ticketed/virtual-interline combinations from Skiplagged's itinerary-level `vi` flag
- **Real cabin and passenger pricing:** economy, premium economy, business and first; adults, children and lap/seated infants are sent correctly and the returned counts are reported
- **Failures stay visible:** a route whose retries are exhausted is named in the run status while successful routes are still emitted
- **Booking providers:** all providers with their prices (`bookingOptions`) plus the cheapest provider names (`bookingProviders`)
- **Filters:** nonstop, max stops, price band, include/exclude airlines, hidden-city include/only/exclude, departure/arrival time windows, max duration, max layover, sort direction
- **Whole-metro coverage:** airport codes, metro codes, city names and Skiplagged slugs; optional nearby-airport search and metro expansion for more than 300 rows
- **Empty fields are omitted** — no `null` values in the dataset

## Output per flight itinerary

- `flightId`, `legType` — `outbound` or `inbound`
- `originAirport`, `originAirportName`, `originCity`, `originState`, `originCountry`
- `destinationAirport`, `destinationAirportName`, `destinationCity`, `destinationState`, `destinationCountry` — the airport where you get off
- State/province is emitted only when Skiplagged returns that airport as a single-airport result. Metro and multi-airport searches omit it rather than mixing a metro-level state with an airport-level city (for example, Newark/EWR would otherwise contradict “New York”). Country is omitted when the source reports a multi-country list.
- `departureTime`, `arrivalTime` — ISO 8601 with timezone offset; `arrivalTime` is the deplaning arrival
- `durationMinutes`, `duration` — travel time to the deplaning airport (e.g. `7h 30m`)
- `stops`, `direct` — stops before the deplaning airport
- `hiddenCity` — `true` when the ticket continues past your destination
- `ticketedDestinationAirport`, `ticketedDestinationCity`, `ticketedStops` — present only on hidden-city rows: where the ticket really ends
- `virtualInterline` — `true` when Skiplagged marks the itinerary as a self-transfer/virtual-interline combination (`vi` in the source)
- `airlines[]`, `airlineCodes[]`, `primaryAirline`
- `segments[]` — one entry per flight leg: `airlineCode`, `airlineName`, `flightNumber`, `departureAirport`, `departureAirportName`, `departureTime`, `arrivalAirport`, `arrivalAirportName`, `arrivalTime`, `durationMinutes`; legs after the deplaning point carry `beyondTicket: true`
- `layovers[]` — one entry per connection before deplaning: `airport`, `airportName`, `durationMinutes`, `duration`
- `price`, `currency` — total price for the requested passenger mix, in USD
- `fareClass` — cabin Skiplagged actually priced; `requestedCabinClass` — what you asked for
- `adults`, `children`, `infantsLap`, `infantsSeat` — passenger counts Skiplagged returned
- `bookingOptions[]` — every provider and its price: `provider`, `price`
- `bookingProviders[]` — provider name(s) quoting the lowest price
- `minRoundTripPrice` — combined round-trip total when Skiplagged quotes one (outbound rows)
- `departDate`, `returnDate`, `originQuery`, `destinationQuery`, `searchedOriginAirports[]`, `searchedDestinationAirports[]` — the airport lists are the overall searched sets, including expansion rows
- `rank` — position within the route after filtering and sorting; `routeIndex` in batch modes
- `sourceUrl` — the Skiplagged search-results page for this route and date (Cloudflare-protected; works in a browser, bare HTTP clients may receive 403)
- `recordType: "skiplaggedFlight"`, `scrapedAt`

## Output per fare-calendar row (mode = `calendar`)

- `recordType: "skiplaggedFareCalendar"`, `calendarType` — `departure` or `return`
- `departDate`, `returnDate`, `tripType`
- `originCode`, `destinationCode`, `originCity`, `destinationCity`, `originAirports[]`, `destinationAirports[]`
- `price`, `currency` — round-trip total when a return date is involved, otherwise the one-way price
- `oneWayPrice` — one-way price when Skiplagged quotes it next to a round-trip total
- `priceLevel` — `low` or `high` when Skiplagged marks the day
- `fareClass`, `requestedCabinClass`, `adults`, `children`, `infantsLap`, `infantsSeat`
- `sourceUrl`, `rank`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `byRoutes` / `byUrls` / `calendar` |
| `origin` | string | `NYC` | Origin airport/metro code, city name or Skiplagged slug (mode=search, calendar) |
| `destination` | string | `LON` | Destination airport/metro code, city name or Skiplagged slug |
| `departDate` | string | – | `YYYY-MM-DD`; blank = six weeks from today; past dates advance to a future month and a past round-trip gap is preserved |
| `returnDate` | string | – | `YYYY-MM-DD`; blank = one-way |
| `originAirports` | array | `[]` | Exact airports to search instead of `origin`, e.g. `["JFK","EWR"]` |
| `destinationAirports` | array | `[]` | Exact airports to search instead of `destination` |
| `includeNearbyAirports` | bool | `false` | Also search airports near both ends; ignored when airport lists are set |
| `expandAirports` | bool | `false` | Split a metro route into the smaller side's airports to get past the 300-row cap; raise `maxItems` above 300 to see the extra rows |
| `routes` | array | `[]` | Batch of `{origin, destination, departDate, returnDate}` objects (mode=byRoutes) |
| `startUrls` | array | `[]` | Skiplagged flight-search URLs, codes or slugs, including single-word slugs such as `tokyo` (mode=byUrls) |
| `tripType` | string | `auto` | `auto` / `one-way` / `round-trip` |
| `cabinClass` | string | `economy` | `economy` / `premium-economy` / `business` / `first` |
| `adults` | int | `1` | Adults (1-9); prices are totals for the whole party |
| `children` | int | `0` | Children (0-8) |
| `infantsLap` | int | `0` | Lap infants (0-8) |
| `infantsSeat` | int | `0` | Seated infants (0-8) |
| `directOnly` | bool | `false` | Only nonstop itineraries to the deplaning airport |
| `maxStops` | int | `3` | Maximum stops before deplaning (0 = nonstop) |
| `minPrice` | int | – | Minimum total price in whole USD |
| `maxPrice` | int | – | Maximum total price in whole USD |
| `airlines` | array | `[]` | Only itineraries flying at least one of these IATA airline codes |
| `excludeAirlines` | array | `[]` | Drop itineraries flying any of these IATA airline codes |
| `hiddenCity` | string | `include` | `include` / `only` / `exclude` |
| `departAfter` | string | – | First departure at or after this local `HH:MM` |
| `departBefore` | string | – | First departure at or before this local `HH:MM` |
| `arriveAfter` | string | – | Deplaning arrival at or after this local `HH:MM` |
| `arriveBefore` | string | – | Deplaning arrival at or before this local `HH:MM` |
| `maxDurationMinutes` | int | – | Maximum minutes to the deplaning airport |
| `maxLayoverMinutes` | int | – | Maximum minutes for any layover |
| `sortBy` | string | `price` | `price` / `duration` / `departureTime` / `stops` |
| `sortOrder` | string | `asc` | `asc` / `desc` |
| `maxItems` | int | `50` | Run-wide record cap (1-1000) |
| `calendarStartDate` | string | – | First calendar date `YYYY-MM-DD` (mode=calendar) |
| `calendarDays` | int | `30` | Days per calendar type (mode=calendar); a round-trip calendar can return departure and return rows, up to twice this many |

Defaults: `[]` means empty; `–` means unset. Field names above are the exact JSON keys.

### Example: hidden-city only, nonstop to London

```json
{
  "mode": "search",
  "origin": "NYC",
  "destination": "LON",
  "departDate": "2026-12-12",
  "hiddenCity": "only",
  "maxStops": 0,
  "sortBy": "price",
  "maxItems": 20
}
```

Pinned control case (verified 2026-11-18): NYC→LON on `2026-12-12` returned 11 hidden economy rows (all nonstop to the deplaning airport) and 28/28 hidden business rows. Use that date and cabin for deterministic hidden-city checks; other dates can legitimately return zero hidden rows because the 300-row result set is source-variable.

### Example: round-trip business with filters

```json
{
  "mode": "search",
  "origin": "JFK",
  "destination": "LHR",
  "departDate": "2026-12-10",
  "returnDate": "2026-12-17",
  "cabinClass": "business",
  "adults": 2,
  "excludeAirlines": ["BA"],
  "departAfter": "18:00",
  "maxLayoverMinutes": 240,
  "sortBy": "duration"
}
```

### Example: batch routes with metro expansion

```json
{
  "mode": "byRoutes",
  "routes": [
    { "origin": "NYC", "destination": "LON", "departDate": "2026-12-10" },
    { "origin": "SFO", "destination": "TYO", "departDate": "2027-01-05", "returnDate": "2027-01-19" }
  ],
  "expandAirports": true,
  "maxItems": 500
}
```

### Example: pasted Skiplagged links

```json
{
  "mode": "byUrls",
  "startUrls": [
    "https://skiplagged.com/flights/NYC/LON/2026-12-10/2026-12-17",
    "https://skiplagged.com/flights/LON/dubai-emirate/2026-12-20"
  ]
}
```

### Example: flexible-date calendar

```json
{
  "mode": "calendar",
  "origin": "NYC",
  "destination": "LON",
  "calendarDays": 30,
  "cabinClass": "economy",
  "maxItems": 40
}
```

## Use cases

- **Fare monitoring** — schedule daily searches and compare price and provider changes on the same route
- **Hidden-city research** — isolate hidden-city fares, see the ticketed destination and the real deplaning airport, and measure how much they save
- **Travel agencies** — batch a client list of routes into one dataset with consistent filters
- **Corporate travel** — check cabin and passenger-mix pricing for employee itineraries
- **Price-comparison products** — feed live Skiplagged fares and provider quotes into your own search experience
- **Seasonality analysis** — use the flexible-date calendar to compare daily prices across a month

## FAQ

**What is the data source?** Skiplagged's public flight-search results (skiplagged.com), which aggregate fares from airlines and online travel agencies. Search is one JSON request per route, plus one per expanded or nearby airport when those options are enabled; the calendar is one request per route.

**Is this affiliated with Skiplagged?** No — this is an independent, third-party actor that reads publicly available Skiplagged search results.

**What is a hidden-city itinerary?** Skiplagged can show a cheaper fare where the ticket ends farther than your destination. You get off at your destination and skip the final leg. The record sets `hiddenCity: true`, keeps `destinationAirport` as the airport where you get off, and adds `ticketedDestinationAirport` for where the ticket really ends. Hidden-city travel has airline rules: do not check bags, and any later segments on the same ticket are cancelled if you skip a leg. Confirm the fare rules before booking.

**How do I spot self-transfer or virtual-interline itineraries?** `virtualInterline: true` is copied from Skiplagged's itinerary-level `vi` flag. These itineraries combine separately ticketed or virtual-interline segments, so check baggage transfer, recheck requirements and missed-connection rules before booking. The flag can occur even when all flown segments use one airline.

**Why do my passenger counts change the price now?** The actor sends Skiplagged's `counts[...]` parameters, so the returned itinerary and price reflect the whole party. `price` is the total, not a per-person fare. The `adults`, `children`, `infantsLap` and `infantsSeat` fields show what Skiplagged returned.

**Does the cabin class work?** Yes. `economy`, `premium-economy` (sent as `premium`), `business` and `first` are sent as Skiplagged's fare class, and `fareClass` on each record shows what was actually priced. Some routes have no inventory in a given cabin; those searches return fewer rows or none.

**Why does a round-trip search return separate outbound and inbound records?** Skiplagged prices round-trips as two one-way tickets. Each leg is a record with `legType` set, and outbound rows may include `minRoundTripPrice` for the combined total.

**How do I get more than 300 rows for a metro route?** Skiplagged caps a single search at about 300 itineraries per leg. Set `expandAirports: true`; the actor also searches the individual airports on the smaller side of the metro (for NYC: JFK, EWR and LGA) and merges unique itineraries. Raise `maxItems` above the default 50 if you want to keep more than 50 rows. It costs a few extra requests per route.

**What is the difference between `bookingProviders` and `bookingOptions`?** `bookingOptions` lists every provider and its price for the itinerary. `bookingProviders` lists only the provider name(s) quoting the lowest price.

**Do I need a proxy or an API key?** No. The actor uses Apify Proxy automatically and retries transient 403/429/5xx responses. There is no login, cookie or API key. A route whose retries are exhausted is reported in the run status instead of being silently dropped.

**Which currency are prices in?** USD, exactly as Skiplagged returns them. Skiplagged's public JSON API does not convert currencies.

**Can I search "anywhere"?** Skiplagged's public JSON API does not expose an anywhere-destination search; the actor therefore requires a destination. For cheap destinations, run a batch of routes from the same origin.

**Are hotel prices included?** No. This actor is focused on flight itineraries and fare calendars. Hotels are a separate product.

## Limitations

- A single search returns at most about 300 itineraries per leg, and that 300-row sample can vary between identical requests. `expandAirports` improves coverage by merging airport-level searches but does not paginate the whole inventory.
- Departure dates must be between yesterday and roughly 11 months ahead, as enforced by Skiplagged. Older past dates are advanced to a future month; round-trip gaps are preserved.
- `originState`/`destinationState` are omitted for metro and multi-airport searches because Skiplagged reports state at metro level. Use single-airport searches when you need state/province, or use the airport code/city fields.
- `sourceUrl` points at a Cloudflare-protected Skiplagged page. It works in a browser; bare HTTP clients may receive a 403 challenge.
- Currency conversion, hotel rates and an anywhere-destination search are not available from the public JSON API.
- Hidden-city itineraries carry airline policy risk: no checked bags, and skipped segments cancel the rest of the ticket. Self-transfer/virtual-interline itineraries (`virtualInterline: true`) carry separate-ticket and missed-connection risk.
