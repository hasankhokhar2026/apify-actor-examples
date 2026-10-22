# Google Maps Popular Times & Live Busyness Scraper

Scrape **Google Maps Popular Times** for any restaurant, shop, gym, bar or attraction: the hourly **busy-hours** chart for every day of the week, the **live busyness** reading ("Currently 52% busy, usually 34% busy"), Google's **open / closed status**, the place's address, coordinates, rating and review count, its **newest reviews with closure mentions**, and run-to-run **monitoring signals** for spotting places that may have closed. Works with Google Maps place URLs, search links or Google Place IDs, in any country, with no API key and no login.

## At a glance

| | |
|---|---|
| **What you get** | Hourly busyness (0–100%) for each day, live busyness vs the usual level (and their ratio), Google's live label, open-now line, listing status (operational / temporarily / permanently closed), stable place ID, address, coordinates, local time, category, rating, review count, phone, website; optionally the newest reviews with closure mentions and a run-to-run monitoring summary |
| **Input** | Google Maps place URLs, search links (`/maps/search/?api=1&query=…`), short links or Google Place IDs (`ChIJ…`) |
| **Output** | JSON, CSV, Excel, XML or HTML via the Apify dataset; ready-made "Popular Times", "Live monitoring" and "Closure signals" table views |
| **Coverage** | Any country where Google Maps shows Popular Times; Google Maps UI in 11 languages |
| **Requirements** | No Google API key, no Google account, no cookies |
| **Scale** | Up to 8 places in parallel; about 370 places per hour at 6 in parallel (measured October 2026) |
| **Automation** | Run from the Apify Console, the API, Python/JavaScript clients, schedules, webhooks and integrations |

## What is Google Maps Popular Times?

**Popular Times** is the bar chart Google Maps shows on a place's page to indicate how busy it usually is at each hour of each day. Google builds it from aggregated, anonymised location data and expresses each hour as a percentage of that place's typical peak (100 = as busy as it gets). While a place is open, Google often adds a **live** reading that compares how busy it is right now with how busy it usually is at this hour. This scraper turns both into structured data.

## What does this Popular Times scraper extract?

- **Per-day hourly busyness** (0–100%) for every day Google charts — a full week in one request
- **Live vs usual** — Google's live percentage (`currentBusyness`) next to its usual percentage for the same hour (`usualBusyness`), plus the chart day and hour the reading belongs to
- **Live label** — Google's wording such as *"Not too busy"*, *"Less busy than usual"* or *"As busy as it gets"*
- **Open / closed status** — whether the listing is operating, temporarily closed or permanently closed, plus Google's open-now line (e.g. *"Open · Closes 11 PM"*)
- **Typical time spent** when Google shows it (e.g. *"People typically spend 30 min to 1 hour here"*)
- **Business name and a stable place identity** — `featureId` / `cid` (and the canonical `ChIJ…` `placeId` when Google shows it) for every place, including places given as search links or short links, so readings from different runs can be joined
- **Listing details** — category, address, latitude/longitude, phone, website, rating and review count
- **Local time of each reading** — the place's time zone, the local date and hour of the scrape, and Google's usual value for that hour from the chart (also when there is no live reading)
- **Live vs usual, ready to compare** — `liveToUsualRatio` and `liveMinusUsual`, plus `liveReadingStatus` explaining why a live reading is missing (closed now, open but no live data, permanently closed…)
- **Newest reviews and closure mentions** (optional) — the newest Google reviews with exact dates, flagged when they say the place is closing or closed ("final weekend", "it was closed", "permanently closed", in 11 languages)
- **Run-to-run monitoring** (optional) — with a monitoring key, every record also compares the reading with the place's earlier readings: low-activity streaks, recent vs earlier live/usual ratio, listing status changes, Popular Times removed or changed, review-count change and new closure mentions
- **Every input accounted for** — each place is returned, or (when enabled) reported as an unavailable-place record with the reason; inputs that turn out to be the same place as an earlier input are returned once, and every outcome (including such duplicates) is counted in a run summary

## Use cases

- **Foot-traffic monitoring** — track live busyness against the usual level across a fixed list of restaurants or stores
- **Closure detection and early warning** — find restaurants that have stopped operating while Google still lists them as open: closure mentions in the newest reviews, live readings that stay far below usual or are missing during listed opening hours, Popular Times that disappear, and listings that turn "Temporarily closed" / "Permanently closed"
- **Site selection and competitor research** — compare busy hours of competing locations
- **Staffing and operations** — plan shifts, deliveries and field visits around quiet and peak hours
- **Travel and "when to go" apps** — recommend the best time to visit restaurants and attractions
- **Research and dashboards** — build time series of busyness by city, category or chain

## How to scrape Google Maps Popular Times

1. **Collect your places** — copy place URLs from Google Maps or use Google Place IDs (`ChIJ…`).
2. **Paste them** into *Place URLs* or *Google Place IDs* and pick the Google Maps language.
3. **Set speed and retries** (optional) — places in parallel, attempts per place, time limit per place, and whether to output unavailable places.
4. **Turn on closure monitoring** (optional) — include the newest reviews and set a monitoring key.
5. **Run** and download the results as JSON, CSV or Excel, or open the *Live monitoring* or *Closure signals* view. Use a schedule with the same monitoring key to repeat the list and build a time series.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `placeUrls` | Array of strings | – | Google Maps place URLs; short links, copied punctuation and tracking parameters are normalized. One of `placeUrls`/`placeIds` is required |
| `placeIds` | Array of strings | – | Canonical Google Place IDs beginning with `ChIJ`. One of `placeUrls`/`placeIds` is required |
| `language` | String | `en` | Google Maps language for labels and parsing: `en`, `es`, `fr`, `de`, `it`, `pt`, `ja`, `ko`, `zh`, `ar`, `ru` |
| `maxConcurrency` | Integer | 3 | Places scraped at the same time (1–8). Needs about 1 GB of run memory per parallel place; lowered automatically if the run has less memory |
| `maxAttemptsPerPlace` | Integer | 8 | Maximum attempts for one place before it is reported as unavailable (1–12) |
| `placeTimeoutSecs` | Integer | 240 | Time limit for one place across all of its attempts, in seconds (30–600) |
| `includeFailedPlaces` | Boolean | `false` | Also output one record per place that could not be retrieved, with the reason |
| `includeLatestReviews` | Boolean | `false` | Also return each place's newest reviews and flag closure mentions |
| `latestReviewsCount` | Integer | 10 | Newest reviews per place (1–60) |
| `monitoringKey` | String | – | Name of a monitoring list; readings are kept in your account between runs and each record gets a `monitoring` summary. Use the same key on every scheduled run |
| `lowActivityRatio` | Number | 0.25 | A live reading counts as low when live ÷ usual is at most this value (0.05–1) |
| `minUsualBusyness` | Integer | 30 | Busy-hour threshold: readings count toward the monitoring streaks and medians only when Google's usual level for that hour is at least this value (5–100) |
| `proxyConfiguration` | Object | – | Places are fetched directly first. If omitted, the last two attempts for a hard-to-reach place use Apify residential proxies (United States, then Canada). Choose "No proxy" to never use a proxy, or your own proxy for those fallback attempts |

### Input examples

**One place by URL**

```json
{
  "placeUrls": [
    "https://www.google.com/maps/place/McDonald%27s/@40.7577297,-73.9853627,17z/data=!3m1!4b1!4m6!3m5!1s0x89c2597777397641:0x4387a82ee10d3e3b!8m2!3d40.7577297!4d-73.9853627!16s%2Fg%2F11fld77pvs"
  ]
}
```

**Places by Google Place ID**

```json
{
  "placeIds": ["ChIJaXQRs6lZwokRY6EFpJnhNNE", "ChIJabtoT7hlwokRLECK0SW3_8I"]
}
```

**Live monitoring list (large, recurring)** — run with 8 GB of memory:

```json
{
  "placeIds": ["ChIJaXQRs6lZwokRY6EFpJnhNNE", "ChIJabtoT7hlwokRLECK0SW3_8I"],
  "maxConcurrency": 6,
  "maxAttemptsPerPlace": 6,
  "includeFailedPlaces": true
}
```

**Closure monitoring (scheduled several times a week)**

```json
{
  "placeIds": ["ChIJaXQRs6lZwokRY6EFpJnhNNE", "ChIJabtoT7hlwokRLECK0SW3_8I"],
  "includeLatestReviews": true,
  "latestReviewsCount": 10,
  "monitoringKey": "vancouver-restaurants",
  "includeFailedPlaces": true
}
```

**Localized labels**

```json
{
  "placeIds": ["ChIJaXQRs6lZwokRY6EFpJnhNNE"],
  "language": "es"
}
```

## Output

One record per place. A real record for an open place with a live reading (with `includeLatestReviews`; chart and review lists shortened):

```json
{
  "recordType": "popularTimes",
  "businessName": "Café de Flore",
  "featureId": "0x47e671d781fb9dab:0x18bba6dd45e173ff",
  "cid": "1782201546845549567",
  "googleMapsUrl": "https://www.google.com/maps?cid=1782201546845549567",
  "placeUrl": "https://www.google.com/maps/search/?api=1&query=Cafe+de+Flore+Paris",
  "category": "Coffee shop",
  "address": "172 Bd Saint-Germain, 75006 Paris, France",
  "latitude": 48.8541588,
  "longitude": 2.3326046,
  "timezone": "Europe/Paris",
  "phone": "+33145485526",
  "website": "https://cafedeflore.fr/",
  "rating": 3.9,
  "reviewCount": 14535,
  "businessStatus": "OPERATIONAL",
  "openStatusText": "Open · Closes 1:30 AM",
  "isOpenNow": true,
  "liveReadingStatus": "live",
  "currentBusyness": 18,
  "usualBusyness": 21,
  "liveToUsualRatio": 0.86,
  "liveMinusUsual": -3,
  "currentBusynessLevel": "Not busy",
  "currentBusynessText": "Currently 18% busy, usually 21% busy.",
  "currentBusynessDay": "friday",
  "currentBusynessHour": 8,
  "observedAtLocal": "2026-10-09T08:06:10+02:00",
  "observedLocalDay": "friday",
  "observedLocalHour": 8,
  "usualBusynessAtObservedHour": 21,
  "popularTimesHasData": true,
  "popularTimesSignature": "fe878c8c86fc16e5",
  "popularTimes": {
    "friday": [
      {
        "hour": 6,
        "busyness": 0
      },
      {
        "hour": 7,
        "busyness": 13
      },
      {
        "hour": 8,
        "busyness": 21
      },
      {
        "hour": 9,
        "busyness": 31
      },
      {
        "hour": 10,
        "busyness": 40
      },
      "..."
    ],
    "saturday": [
      "..."
    ]
  },
  "closureMentionCount": 0,
  "latestReviewAt": "2026-10-09T03:58:59+00:00",
  "daysSinceLatestReview": 0,
  "latestReviews": [
    {
      "publishedAt": "2026-10-08T22:56:12+00:00",
      "publishedAtText": "7 hours ago",
      "rating": 5,
      "text": "Ironic place with very good service and food.",
      "originalText": "Lugar irónico con muy buen servicio y comida."
    },
    "..."
  ],
  "sourceUrl": "https://www.google.com/maps/search/?api=1&query=Cafe+de+Flore+Paris",
  "scrapedAt": "2026-10-09T06:06:09.536970+00:00"
}
```

Fields Google does not show for a place are omitted — no `null` values appear in the dataset.

### Unavailable places

With `includeFailedPlaces` enabled, every place that could not be retrieved produces a record like this. It carries the Place ID or feature ID from your input when the input contains one, and has no `attempts` when the place was never started:

```json
{
  "recordType": "failed",
  "placeId": "ChIJaXQRs6lZwokRY6EFpJnhNNE",
  "placeUrl": "https://www.google.com/maps/search/?api=1&query=ChIJaXQRs6lZwokRY6EFpJnhNNE&query_place_id=ChIJaXQRs6lZwokRY6EFpJnhNNE",
  "failureReason": "limitedView",
  "attempts": 8,
  "scrapedAt": "2026-10-07T13:25:40+00:00"
}
```

| `failureReason` | Meaning |
|---|---|
| `limitedView` | Google showed only its restricted view on the final attempt(s) |
| `timeout` | The time limit was reached |
| `network` | The page could not be loaded |
| `unconfirmedEmpty` | The place showed no popular times once, but repeated attempts could not confirm it |
| `notResolved` | The input did not lead to a single matching Google Maps place |
| `notStarted` | The run's time limit was reached before this place could be started — raise the run timeout or split the list |
| `error` | An unexpected error occurred |

### Output fields

| Field | Description |
|---|---|
| `recordType` | `popularTimes` for a place record, `failed` for an unavailable place |
| `businessName` | Place name as shown on Google Maps |
| `placeId` / `featureId` | Canonical `ChIJ…` Place ID or legacy `0x…:0x…` token (see below) |
| `cid` / `googleMapsUrl` | Google's numeric place ID and a stable link to the place |
| `category`, `address`, `phone`, `website` | Listing details as shown on Google Maps |
| `latitude` / `longitude` | The place's pin (or, where Google shows no pin, as in South Korea, the centre of the place's Plus Code) |
| `rating` / `reviewCount` | Star rating and number of reviews |
| `placeUrl` / `sourceUrl` | The input URL, normalized |
| `popularTimesHasData` | Whether Google shows a Popular Times chart for the place |
| `popularTimes` | Hourly busyness per day: `{day: [{hour, busyness}]}` |
| `currentBusyness` | Google's live reading at the moment of the scrape, exactly as displayed (0–100) |
| `usualBusyness` | Google's usual level for the same hour, as displayed beside the live reading |
| `currentBusynessLevel` | Google's live label, e.g. "Not too busy", "Less busy than usual", "As busy as it gets" |
| `currentBusynessDay` / `currentBusynessHour` | The chart day and hour the live reading belongs to (the place's local time) |
| `currentBusynessText` | Google's full live text, e.g. "Currently 52% busy, usually 34% busy." |
| `liveToUsualRatio` / `liveMinusUsual` | Live ÷ usual (e.g. 0.08) and live − usual in points (e.g. −22), when Google shows both |
| `liveReadingStatus` | `live`, `closedNow` (outside listed hours), `openNoLiveData` (listing says open, no live reading), `noPopularTimes`, `temporarilyClosed`, `permanentlyClosed` or `noLiveData` |
| `timezone`, `observedAtLocal`, `observedLocalDay`, `observedLocalHour` | The place's time zone and the local time of the scrape |
| `usualBusynessAtObservedHour` | Google's usual value for that local hour, read from the chart (also when there is no live reading). Just after the hour turns, Google can still show the previous hour's live reading; `currentBusynessDay` / `currentBusynessHour` name the hour a live value belongs to, and `usualBusyness` is the usual value for that same hour |
| `popularTimesSignature` | Fingerprint of the weekly profile; it changes when Google updates the usual values |
| `businessStatus` | `OPERATIONAL`, `CLOSED_TEMPORARILY` or `CLOSED_PERMANENTLY`, as shown on the listing |
| `openStatusText` / `isOpenNow` | Google's open-status line (e.g. "Closed · Opens 8 AM") and whether it says the place is open now |
| `typicalTimeSpent` | Google's visit-duration text, when shown |
| `latestReviews` | With `includeLatestReviews`: newest reviews with `publishedAt`, `publishedAtText`, `rating`, `text` (in the chosen language), `originalText` (when translated) and `closurePhrase` (when the review mentions a closure) |
| `latestReviewAt` / `daysSinceLatestReview` | Date of the newest review and days since |
| `closureMentionCount` / `latestClosureMentionAt` | Newest reviews mentioning a closure, and the date of the latest one |
| `monitoring` | With `monitoringKey`: run-to-run summary (see [Closure monitoring](#closure-monitoring)) |
| `failureReason` / `attempts` | Only on `failed` records: the reason and the number of attempts used |
| `scrapedAt` | Time of the scrape (UTC, ISO 8601) |

### Hourly busyness format

Each day in `popularTimes` is an array of `{hour, busyness}` pairs: `hour` is 0–23 in the place's local time and `busyness` is 0–100 relative to that place's peak. Each day follows Google's chart, which runs from early morning through the small hours of the next day (for example 4 AM to 3 AM), so late-night hours appear at the end of the day they belong to. Hours with no data are omitted, and days for which Google shows no data (usually days the place is closed) are omitted.

The chart slot for the current hour always holds Google's **usual** value; the live reading is only in `currentBusyness`. In the example above, the Friday 8 AM slot holds `21` (the usual level) while `currentBusyness` is `18`.

### Place identity

A canonical `ChIJ…` token is reported as `placeId` and a legacy `0x…:0x…` token as `featureId`; a legacy token is never relabelled as a Place ID. Google exposes a canonical Place ID for some places and only the legacy token (or neither) for others, so `placeId` is legitimately absent on many place records — the actor never invents or back-fills it. Records for unavailable places carry the identity contained in your own input.

### Run summary

Every run stores a `RUN_SUMMARY` record in its key-value store with: places requested, records produced, places without popular times, duplicates, failures by reason, attempts, attempts that used a proxy, places not started because of the time limit, parallelism and run duration (plus places whose newest reviews could not be read, and the monitoring store name, when those options are on).

## Closure monitoring

Google can keep a restaurant listed as open for a while after it stops trading, and diners often notice first, writing reviews such as *"It was closed, looked permanently."* or *"Went on final weekend"*. This actor collects those signals, together with changes in live busyness and listing status, so you can review the places that need a closer look.

**Recommended setup**

1. Use stable inputs: Place IDs or place URLs (search links also work; every record carries a stable `featureId` / `cid`).
2. Turn on `includeLatestReviews` and set a `monitoringKey` (one key per list).
3. Schedule the actor several times a week at the same local hours, including each place's usual busy hours (see `popularTimes`) — a quiet reading at a quiet hour says little.
4. Enable `includeFailedPlaces` so every place appears in every run.
5. Review the *Closure signals* view, or filter on `monitoring.signals`.

**Monitoring summary (`monitoring`)**

| Field | Meaning |
|---|---|
| `readingsCount`, `firstReadingAt`, `previousReadingAt` | How many readings are stored for the place and when |
| `liveReadingsCount` | Readings that had a live value |
| `busyHourReadingsCount` / `busyHourLiveReadingsCount` | Readings taken at busy hours (usual level ≥ `minUsualBusyness`), and how many of them had a live value |
| `lowActivityStreak` | Latest consecutive busy-hour live readings at or below `lowActivityRatio` × usual |
| `openNoLiveDataStreak` | Latest consecutive busy-hour readings where the listing said open but Google showed no live reading |
| `recentMedianRatio` / `baselineMedianRatio` | Median live ÷ usual of the last 5 busy-hour live readings vs the 20 before them (needs 3+ readings each) |
| `statusChange` | Listing status change since the previous reading, e.g. `OPERATIONAL` → `CLOSED_PERMANENTLY` |
| `popularTimesRemoved` / `popularTimesChanged` | The weekly chart disappeared, or its usual values changed |
| `reviewCountChange` | New reviews since the previous reading |
| `newClosureMentions` | Closure-mentioning reviews not seen in earlier runs |
| `signals` | Plain flags: `statusChanged`, `closedOnGoogle`, `popularTimesRemoved`, `popularTimesChanged`, `newClosureMentions`, `lowActivityStreak` (3+), `openWithoutLiveDataStreak` (3+), `belowBaseline` (recent median ≤ 70% of baseline) |

**Busy hours only.** A low or missing reading at an hour the place is usually quiet says little (2% live when the usual level is 10% is noise; 2% when it is usually 79% is not). Streaks and medians therefore use only readings taken when Google's usual level for that hour is at least `minUsualBusyness` (default 30%). Readings at quiet hours are kept in the history but neither extend nor break a streak.

**Reading the signals**

- *Sudden collapse*: `lowActivityStreak` or `openWithoutLiveDataStreak` at the place's usual busy hours, often together with closure mentions.
- *Gradual decline*: `belowBaseline` over several weeks of readings at consistent hours, with a slowing `reviewCountChange`.
- *Confirmed by Google*: `statusChanged` / `closedOnGoogle`, usually with `popularTimesRemoved` (Google drops the chart from closed listings).

These are indicators to investigate, not proof: Popular Times comes from Google's aggregated location data, not visitor counts, single readings swing widely, and closure mentions are matched by phrase (each flagged review keeps the matched `closurePhrase` and its text so you can check it).

The history is kept in a key-value store named `popular-times-monitor-<your key>` in your Apify account (up to 500 readings per place). Avoid running two runs with the same key at the same time.

## Speed at scale

Measured in October 2026 on 100 restaurants in 20 cities without proxies:

| Places in parallel (memory) | Places per hour | Time per 1,000 places |
|---|---|---|
| 1 (2 GB) | about 95–100 | about 10.5 hours |
| 3 (4 GB, default) | about 220 | about 4.5 hours |
| 6 (8 GB) | about 370 | about 2.7 hours |

Each place also waits for Google to settle its place link (for a stable ID) and reads the listing details, which adds to the time per place above. `includeLatestReviews` adds one small request per place after the place is scraped; it never makes a place fail. These requests are paced (at most one every 2 seconds) and, if Google ever limits them, paused for two minutes rather than retried; `RUN_SUMMARY` counts places whose reviews could not be read (`latestReviewsUnavailable`) and such pauses (`latestReviewsBlocked`). `monitoringKey` adds two key-value store operations per place.

## FAQ

### What is the difference between `currentBusyness` and `usualBusyness`?
`currentBusyness` is Google's live reading at the moment of the scrape; `usualBusyness` is Google's usual level for the same hour, shown beside it. Both are read verbatim from Google — the actor never estimates or interpolates.

### Why is `currentBusyness` sometimes missing?
Google only shows live data while the place is open and has enough recent visits, and places without a Popular Times chart never have one. `liveReadingStatus` tells you which case applies.

### What happens to live data when a business is closed?
When the listing shows the place as closed (outside listed hours, temporarily or permanently closed), Google normally shows no live reading and the field is omitted. `isOpenNow`, `openStatusText` and `businessStatus` tell you what the listing says.

### Why can a closed business still show a small live percentage?
Google states that live busyness comes from aggregated, anonymised location data and does not publish its model. Staff, neighbouring businesses in the same building, deliveries or passers-by can plausibly produce small readings, especially in dense areas. Treat low single-digit readings as "near the floor", not as proof of customers.

### How do I detect a drop in activity at a location?
Set a `monitoringKey` and run the same list on a schedule at consistent local hours. Each record then reports `lowActivityStreak`, `openNoLiveDataStreak` and the recent vs earlier median of `liveToUsualRatio`, with plain `signals` when they cross their thresholds. Sustained low ratios, or live readings that are repeatedly missing during listed opening hours, are stronger signals than any single value. Google's usual profile is a multi-month average, so it lags real change.

### Can it find restaurants that closed but are still listed as open?
It surfaces the evidence: newest reviews that mention a closure (`closureMentionCount`, `closurePhrase`), missing or very low live readings during listed opening hours, Popular Times that disappear, and status changes between runs. Treat these as reasons to check a place, not as proof.

### Why did a place's Popular Times disappear?
Google removes the chart from listings it marks as temporarily or permanently closed, and from places with too little recent visit data. With a `monitoringKey`, the summary reports `popularTimesRemoved` when a chart seen in an earlier run is gone.

### Which phrases count as a closure mention?
Specific phrases that state a closure, such as "permanently closed", "it was closed", "out of business", "final weekend", "shame you're closing" or "will miss this place", in all 11 supported languages; Google's own translation is checked too. A bare "closed" (as in "closed on Mondays") does not count. Each flagged review keeps `closurePhrase` and its text.

### Where is the monitoring history stored?
In your own Apify account, in a key-value store named `popular-times-monitor-<your key>` (the key is lowercased, other characters become hyphens, and the full name is cut to 63 characters). Delete the store to start the history again.

### How stable is the usual profile between runs?
The weekly profile is Google's long-run average, so it normally stays the same between runs and only shifts when Google updates it; `popularTimesSignature` changes when that happens. The live reading, by contrast, can move a lot from hour to hour.

### Which places have Popular Times data?
Restaurants, cafés, bars, retail stores, gyms, grocery stores and major attractions usually do. Small businesses, services without foot traffic and very new listings often do not.

### Which input should I use for reliable monitoring?
Use Place IDs (`placeIds`) or the full place URL copied from Google Maps. Search links (`/maps/search/?api=1&query=…`) work too, and the record then carries the place's stable `featureId` and `cid` for joining runs. A query with the name and street address opens the place directly. When a query matches several places, Google shows a list: the actor opens the listed place whose full name appears in your query (e.g. "ICHIRAN Shibuya" for "Ichiran Shibuya Tokyo"; for duplicate listings at one address, the one with the most reviews), and reports branches of a chain at different addresses as unavailable (`notResolved`) rather than guessing — add the street address to such queries. A short name-plus-map-position URL can be ambiguous when several places share a name, and Google leaves permanently closed places out of its search results, so such places can only be reached by their Place ID or full place URL. An input that cannot be matched to exactly one place is reported as unavailable (`notResolved`) rather than guessed.

### Can it handle thousands of places on a schedule?
Yes. Raise `maxConcurrency` (6 with 8 GB of memory is recommended for large lists) and set a run timeout long enough for your list; see [Speed at scale](#speed-at-scale). The actor stops starting new places shortly before the run's time limit, counts them in `RUN_SUMMARY` and, with `includeFailedPlaces`, outputs a `notStarted` record for each. Split very large lists into several runs and schedule them at consistent local times.

### What if none of my places can be retrieved?
If a run produces no place records and at least one place failed, the run is marked as failed with a status message saying whether the inputs could not be matched to a place or Google did not return Popular Times. With `includeFailedPlaces` on, the `failed` records are still in the dataset.

### Can I limit retries for places that fail?
Yes. `maxAttemptsPerPlace` and `placeTimeoutSecs` cap the effort per place, "No proxy" avoids all proxy usage, and inputs that do not resolve to a place stop after two tries. Enable `includeFailedPlaces` to get a record for every unavailable place.

### Do I need a proxy, cookies or a Google API key?
No. Places are fetched directly first; by default only the last two attempts for a hard-to-reach place use Apify residential proxies. No cookies, Google account or API key are needed.

### Is a live label without a percentage still captured?
Yes. When Google states the live level only in words (e.g. "Currently as busy as it gets"), you get the wording in `currentBusynessText` and `currentBusyness` is omitted rather than guessed.

### Why is `typicalTimeSpent` often missing?
Google shows visit duration only for some places, and rarely for restaurants. The actor only outputs the text Google displays.

### Which languages are supported?
English, Spanish, French, German, Italian, Portuguese, Japanese, Korean, Chinese, Arabic and Russian. Labels are accepted only when their localized meaning is recognized; otherwise the field is omitted.

### Does this use the Google Places API?
No. It reads the same public Google Maps page you see in your browser, so no API key, billing account or quota is needed.

## Data source

Public Google Maps web pages (`google.com/maps`). You are responsible for using the extracted data lawfully and in line with Google's terms.
