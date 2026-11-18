# Skiplagged Route Fare & Booking Provider Finder

Scrape **Skiplagged** — the flight fare-comparison search engine known for surfacing hidden-city and self-transfer itineraries that other search engines don't show. Search a single route, batch many routes in one run, or feed it Skiplagged search-page URLs directly. Get real prices, airlines, flight numbers, timings, layovers, and the cheapest booking provider for every itinerary. No login, no proxy, no cookies required.

## What this actor does

- **Three modes:** `search` (single route), `byRoutes` (batch multiple routes in one run), `byUrls` (paste Skiplagged search-page links)
- **One-way and round-trip** — round-trip searches return the outbound and return legs as separate priced itineraries, each tagged with `legType`, matching how Skiplagged itself prices them
- **Passenger mix:** adults, children, and infants (lap or seated)
- **Filters:** direct-only, max stops, price range, airline allow-list, sort order
- **Booking providers:** every itinerary lists which travel site(s) currently offer its lowest price
- **Empty fields are omitted**

## Output per flight itinerary

- `flightId`, `legType` — `outbound` or `inbound`
- `originAirport`, `originCity`, `originState`, `originCountry`, `destinationAirport`, `destinationCity`, `destinationState`, `destinationCountry`
- `departureTime`, `arrivalTime` — ISO 8601 with timezone offset
- `durationMinutes`, `duration` — human-readable (e.g. `7h 30m`)
- `stops`, `direct`
- `airlines[]`, `airlineCodes[]`, `primaryAirline`
- `segments[]` — one entry per flight leg: `airlineCode`, `airlineName`, `flightNumber`, `departureAirport`, `departureTime`, `arrivalAirport`, `arrivalTime`, `durationMinutes`
- `layovers[]` — one entry per connection: `airport`, `durationMinutes`, `duration` (human-readable). Omitted on direct itineraries.
- `price`, `currency`
- `fareClass` — cabin actually returned by Skiplagged for this itinerary
- `requestedCabinClass` — the cabin class you asked for
- `adults`, `children`, `infantsLap`, `infantsSeat`
- `bookingProviders[]` — travel site(s) offering the lowest listed price
- `minRoundTripPrice` — combined round-trip total, present on `outbound` records for round-trip searches
- `sourceUrl` — the Skiplagged search-results page for this route/date
- `recordType: "skiplaggedFlight"`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` / `byRoutes` / `byUrls` |
| `origin` | string | `NYC` | Origin IATA airport or metro code (mode=search) |
| `destination` | string | `LON` | Destination IATA airport or metro code (mode=search) |
| `departDate` | string | – | `YYYY-MM-DD`; defaults to 6 weeks from today if blank |
| `returnDate` | string | – | `YYYY-MM-DD`; omit for one-way |
| `routes` | array | – | Batch of `{origin, destination, departDate, returnDate}` objects (mode=byRoutes) |
| `startUrls` | array | – | Skiplagged flights-search URLs (mode=byUrls) |
| `tripType` | string | `auto` | `auto` / `one-way` / `round-trip` |
| `cabinClass` | string | `economy` | `economy` / `premium-economy` / `business` / `first` |
| `adults` | int | `1` | Adult passengers (1-9) |
| `children` | int | `0` | Child passengers (0-8) |
| `infantsLap` | int | `0` | Lap infants (0-8) |
| `infantsSeat` | int | `0` | Seated infants (0-8) |
| `directOnly` | bool | `false` | Only nonstop itineraries |
| `maxStops` | int | `3` | Drop itineraries with more stops |
| `minPrice` | int | – | Drop itineraries cheaper than this (USD) |
| `maxPrice` | int | – | Drop itineraries pricier than this (USD) |
| `airlines` | array | – | Only itineraries flying at least one of these IATA airline codes |
| `sortBy` | string | `price` | `price` / `duration` / `departureTime` / `stops` |
| `maxItems` | int | `50` | Hard cap on emitted records (1-1000) |

### Example: one-way search

```json
{
  "mode": "search",
  "origin": "JFK",
  "destination": "LAX",
  "departDate": "2026-09-15",
  "directOnly": true
}
```

### Example: round-trip with passenger mix and price cap

```json
{
  "mode": "search",
  "origin": "NYC",
  "destination": "LON",
  "departDate": "2026-09-01",
  "returnDate": "2026-09-08",
  "adults": 2,
  "children": 1,
  "maxPrice": 800,
  "sortBy": "duration"
}
```

### Example: batch multiple routes in one run

```json
{
  "mode": "byRoutes",
  "routes": [
    { "origin": "NYC", "destination": "LON", "departDate": "2026-09-01" },
    { "origin": "SFO", "destination": "TYO", "departDate": "2026-10-05", "returnDate": "2026-10-19" }
  ],
  "maxItems": 100
}
```

### Example: from a pasted Skiplagged URL

```json
{
  "mode": "byUrls",
  "startUrls": ["https://skiplagged.com/flights/NYC/LON/2026-09-01/2026-09-08"]
}
```

## Use cases

- **Fare monitoring** — track route prices over time for travel alerts or dashboards
- **Travel agencies** — compare provider pricing across a batch of client routes in one run
- **Corporate travel** — bulk-check fares for multiple employee itineraries
- **Price-comparison tools** — feed real fare data into your own travel search product
- **Market research** — analyze airline pricing and route competitiveness

## FAQ

**What's the data source?** Skiplagged's public flight-search results (skiplagged.com), which aggregate fares from multiple online travel agencies and airlines.

**Is this affiliated with Skiplagged?** No — this is an independent, third-party actor that reads Skiplagged's public search results. It is not affiliated with or endorsed by Skiplagged.

**Why does a round-trip search return separate outbound/inbound records instead of one combined itinerary?** Skiplagged prices round-trips as two independently-booked one-way tickets (its well-known self-transfer/hidden-city model), not as a single bundled fare. Each leg is returned as its own record with `legType` set to `outbound` or `inbound`, plus `minRoundTripPrice` on the outbound record showing the combined total Skiplagged currently quotes.

**Why doesn't `cabinClass` always change the results?** Skiplagged's public search primarily returns economy inventory for most routes regardless of the requested cabin. The actor always reports the real `fareClass` Skiplagged returned alongside your `requestedCabinClass`, so you can see when the two differ.

**Why do `adults`/`children`/`infantsLap`/`infantsSeat` on output records not always match my requested passenger counts?** The `price` shown is always a real per-passenger fare, and the `adults`/`children`/etc. fields reflect exactly what Skiplagged's search response reports for that itinerary — which for its public (non-logged-in) search is typically `1 adult` regardless of the passenger counts you request. The actor never fabricates these fields; it passes your requested counts to Skiplagged and reports back only what Skiplagged's API actually returns.

**What does `bookingProviders` mean?** Skiplagged compares prices across several travel sites (airlines, OTAs, meta-search partners) for the same itinerary. This field lists whichever provider(s) are currently offering the lowest price shown.

**What are `originState`/`destinationState`?** Skiplagged reports a state or region for the queried city/metro area (e.g. `New York` for a US search, `England` for a UK search). This field is omitted when Skiplagged doesn't report one for that country.

**Can I search by city instead of a specific airport?** Yes — 3-letter metro codes like `NYC` (covers JFK/LGA/EWR) or `LON` (covers LHR/LGW/STN/LTN/LCY) are supported alongside single-airport codes like `JFK` or `LHR`.

**How fresh are the prices?** Prices reflect what Skiplagged's search API returns at the moment the actor runs — the same live pricing shown to a visitor on skiplagged.com.
