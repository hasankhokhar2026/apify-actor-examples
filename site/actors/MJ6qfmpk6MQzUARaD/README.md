# Zillow Upcoming Open House Finder by City or ZIP

Collect upcoming open houses listed on Zillow for a city or ZIP code, with each showing's start and end time alongside the property's price, beds/baths, square footage and location. Search by free-text location or paste a Zillow search/open-houses URL directly.

## What this actor does

- Searches Zillow's open-house listings for a city or ZIP code, or reads a pasted Zillow search URL
- Returns the scheduled showings Zillow lists for each property, with a `nextOpenHouse` convenience field pointing to the soonest one
- Leaves out properties that have no showing schedule, so every record has at least one open house
- Filters results to a specific date range so you only get showings happening when you can attend
- Pulls core property data (price, beds, baths, square footage, year built, tax assessment, lot area) straight from the search results
- Empty fields are omitted from each record

## Output per property

- `url`, `zpid` — Zillow property page URL and ID
- `status` — listing status (e.g. `FOR_SALE`)
- `address`, `city`, `state`, `zipCode`
- `latitude`, `longitude`
- `price`, `zestimate`, `currency`
- `beds`, `baths`, `sqft`
- `yearBuilt`, `propertyType`, `daysOnZillow`
- `taxAssessedValue`, `lotAreaValue`, `lotAreaUnit`
- `openHouses[]` — each scheduled showing as `{startDateTime, endDateTime, openHouseType}`, sorted chronologically; times are the property's local time without a timezone offset
- `nextOpenHouse` — the earliest entry from `openHouses`, duplicated here for convenience
- `scrapedAt` — ISO timestamp of when the record was collected
- With `scrapeDetails` enabled, each property's own Zillow page is also visited, adding `lotSize`, `stories`, `hoaFee`, `pricePerSqft`, `brokerName`, `agentName`, `agentPhone`, `description`, and `photos[]`, and refining `address`, `city`, `state`, `zipCode`, `latitude`, `longitude`, `price`, `zestimate`, `beds`, `baths`, `sqft`, `yearBuilt`, `propertyType`, and `daysOnZillow` with the detail page's own values

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `search` | string | – | Free-text location, best as a city and state or a ZIP code (e.g. `Austin, TX`, `90210`) |
| `startUrls` | array | – | Zillow search or open-houses URLs (up to 25 result pages each). Listings without a showing schedule are skipped; individual property (`/homedetails/`) URLs are not supported |
| `dateFrom` | string | – | Only include showings on or after this date (`YYYY-MM-DD`); properties with no showing in range are dropped |
| `dateTo` | string | – | Only include showings on or before this date (`YYYY-MM-DD`) |
| `scrapeDetails` | boolean | `false` | Also visit each property's own Zillow page for lot size, stories, HOA fee, price per square foot, listing agent/broker name and phone, description, and photos. Slower; leave off for a quicker listing-only run |
| `maxItems` | integer | `100` | Maximum properties to return (1–500). Fewer come back when Zillow lists fewer open houses for the area |

At least one of `search` or `startUrls` is required.

### Example: open houses this weekend in Austin

```json
{
    "search": "Austin, TX",
    "dateFrom": "2026-05-04",
    "dateTo": "2026-05-05",
    "maxItems": 100
}
```

### Example: upcoming open houses in one ZIP code

```json
{
    "search": "78704",
    "maxItems": 50
}
```

### Example: scrape from a Zillow search URL

```json
{
    "startUrls": [
        "https://www.zillow.com/austin-tx/open-houses/"
    ]
}
```

## Use cases

- **Home buyers** — build a weekend viewing itinerary for a target neighborhood or ZIP code
- **Real estate agents** — track open house activity from competing listings in your market
- **Market researchers** — monitor how often properties in an area hold open houses and at what price point
- **Lead-generation teams** — surface actively-marketed listings that are hosting a showing soon

## FAQ

**Does this need a Zillow account or login?**
No. It reads Zillow's public open-house search results.

**Can I filter to a specific date range?**
Yes. Set `dateFrom`, `dateTo`, or both — leave either blank for no bound on that side.

**What does `nextOpenHouse` mean?**
It's the earliest entry in that property's `openHouses` array, duplicated at the top level so you don't have to sort the array yourself.

**What's the difference between `INPERSON` and `VIRTUAL` in `openHouseType`?**
`INPERSON` is an on-site walkthrough; `VIRTUAL` is an online showing. When Zillow's search data gives a showing time without a type, the actor labels it `INPERSON`, so treat that value as the default rather than a guarantee.

**Can I pass a Zillow URL instead of a location?**
Yes. Paste a Zillow search or open-houses URL into `startUrls`. The URL is read as-is, and any listing on it without a showing schedule is skipped, so an open-houses URL (such as `https://www.zillow.com/austin-tx/open-houses/`) gives the fullest results. Direct individual property URLs aren't supported.

**Why are fields like `zestimate`, `yearBuilt`, or `taxAssessedValue` missing on some properties?**
They come from the summary Zillow shows in its search results, and not every listing carries them there. Agent/broker name and phone, photos, and full descriptions are only collected when `scrapeDetails` is enabled.

**Which locations work in `search`?**
City-and-state pairs (`Austin, TX`) and ZIP codes (`78704`) work best, because the text is turned into Zillow's own open-houses page for that place. For neighborhoods or unusual areas, open the open-houses page on Zillow and paste its URL into `startUrls` instead.

**Is this affiliated with Zillow?**
No. This is an independent actor that reads Zillow's public open-house pages and is not operated or endorsed by Zillow.
