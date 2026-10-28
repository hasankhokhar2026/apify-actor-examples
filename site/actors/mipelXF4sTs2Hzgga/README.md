# X Trends Lookup by Country, City & WOEID

Get ranked trending topics from X (Twitter) for any country or city, or for every location X serves in one run — no login, no cookies, no API key. Each trend comes back with its rank, type, a ready-made search link, and the approximate post volume when X publishes it.

## What this actor does

- Looks up trends for a list of locations by name, common alias, or numeric WOEID
- Collects trends for every location X serves (around 467 countries and cities) in a single run when asked
- Keeps each trend's rank, name and type — hashtag, cashtag, or topic
- Builds a ready-made X search link for every trend
- Omits any field that has no value for a given row rather than returning a null or placeholder

## Output per row

Every row carries a `type` of `trend` or `status`.

| Field | Description |
|---|---|
| `type` | `trend` for a trending topic, `status` for a problem or summary row |
| `location` | The location you asked for, with its WOEID appended when two places share a name |
| `woeid` | X's numeric location identifier |
| `country` / `countryCode` | Country name and ISO code X reports for the location, when available |
| `placeType` | X's place type, e.g. Country, Town, or Metro |
| `rank` | Position in the trending list (1 = top trend) |
| `trend` | Trend name, hashtag, or cashtag |
| `trendType` | hashtag, cashtag, or topic |
| `searchUrl` / `trendUrl` | Ready-made X search link for the trend |
| `tweetVolume` | Approximate number of posts using the trend, only when X publishes it |
| `promoted` | Whether the trend is a promoted one |
| `asOf` | When X calculated this trending list |
| `collectedAt` | When this row was collected |

Status rows carry a `status` value (such as `unknownLocation`, `notAvailable`, or `rateLimited`) and a human-readable `message`, plus `didYouMean` suggestions for likely typos. When collecting every location, problems are also summarized into one `collectionSummary` row with `trendCount`, `locationsWithTrends`, `locationsTotal`, `locationsWithoutTrends`, `notAvailableLocations`, and `failedLocations`.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `locations` | array of strings | – | Countries or cities to get trends for — names, aliases (USA, UK, NYC), or numeric WOEIDs. Put "all" to collect every location. |
| `allLocations` | boolean | false | Collect trends for every location X serves (around 467 countries and cities); ignores `locations` when on |
| `includeTweetVolume` | boolean | true | Include the approximate post volume for a trend, when X publishes it |
| `includeSearchUrls` | boolean | true | Include a ready-made X search link for every trend |
| `maxTrendsPerLocation` | integer | 50 | How many ranked trends to keep per location (1-50) |
| `proxyConfiguration` | object | – | Optional proxy override, useful for large or repeated runs |

### Example: a handful of countries

```json
{
  "locations": ["United States", "United Kingdom", "Japan"],
  "maxTrendsPerLocation": 20
}
```

### Example: cities and a WOEID together

```json
{
  "locations": ["London", "New York", "Dubai", "23424977"],
  "includeTweetVolume": true
}
```

### Example: every location in one run

```json
{
  "allLocations": true,
  "maxTrendsPerLocation": 50
}
```

## Use cases

- **Social listening** — track what's breaking out in any market, hour by hour
- **Newsroom monitoring** — spot emerging stories by city or country early
- **Content scheduling** — plan posts around live trends using the ready-made search links
- **Cross-country comparison** — compare trending topics across markets to study regional interest
- **Automated reporting** — capture timestamped trend snapshots for recurring client or team reports

## FAQ

**Do I need an X/Twitter account?**
No. This actor works without login, cookies, or an API key.

**How many locations can I get trends for?**
X currently serves trends for around 467 countries and cities; `allLocations` covers every one of them in a single run.

**Can I look up a city instead of a country?**
Yes — major cities like London, New York, Tokyo, Dubai, and Sydney work by name, as do countries worldwide. For a location not in the friendly list, paste its numeric WOEID, or run `allLocations` and filter the results by `location` afterward.

**How do I use a WOEID?**
Paste the number directly into `locations`. Rows for a WOEID you entered are still labeled with the place name X returns, so the dataset stays readable.

**Why is `tweetVolume` missing on some rows?**
X only publishes a post-volume figure for a subset of trends. When X doesn't provide one, the field is left out rather than showing a misleading number.

**What does a `status` row mean?**
It means the location wasn't recognized, X temporarily limited the request, or X doesn't serve trends for that location at all (China, for example). The `message` field explains what happened so a run never fails silently.

**How big is a full `allLocations` run?**
It can return roughly 22,000 rows (around 467 locations times up to 50 trends each), plus one `collectionSummary` row reporting how many locations succeeded, failed, aren't served by X, or returned no trends.

**How fresh is the data?**
X recalculates trends continuously; the `asOf` field tells you exactly when X computed the list for each location.

**Is this affiliated with X?**
No. This actor reads X's publicly visible trending data and is not affiliated with, endorsed by, or sponsored by X Corp.
