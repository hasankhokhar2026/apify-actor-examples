# Zillow For-Sale, Rent & Sold Listing Extractor

Enter a city, state, or ZIP code and choose active listings, rentals, or recently sold homes — this actor turns Zillow's own search results into structured property records. Search results give price, size and location; with detail scraping on, each listing also gets nearby schools, tax history, price history, agent details and property features.

## What this actor does

- Searches any US city, state, or ZIP code across three modes: for sale (`BUY`), for rent (`RENT`), or recently sold (`SOLD`)
- Returns core listing data from search results — price, Zestimate, rent Zestimate, beds, baths, square footage, lot size, address and coordinates
- Optionally opens each property's detail page for year built, HOA fee, agent, full description, all photos, nearby schools, price history, tax history, and property features
- Accepts direct Zillow property or search-page URLs alongside or instead of a location search; a property that appears in several searches is returned once
- Fields a listing doesn't have (e.g. no HOA fee, no Zestimate) are left out of the record rather than returned empty

## Output per property

Each property produces one record. Fields with no available data are left out automatically. Fields marked *detail* only appear when `scrapeDetails` is on and the property's detail page could be read; if a detail page fails, the record keeps its search-result data (for a direct property URL that can be just `url` and `zpid`).

### Core property data

| Field | Type | Description |
|-------|------|-------------|
| url | String | Property detail URL on Zillow.com |
| zpid | Number | Zillow property ID (a text ID for some apartment-building listings) |
| status | String | Listing status as Zillow reports it (e.g., FOR_SALE, FOR_RENT, RECENTLY_SOLD) |
| price | Number | Current listing price |
| zestimate | Number | Zillow's estimated market value |
| rentZestimate | Number | Zillow's estimated monthly rent value |
| beds | Number | Number of bedrooms |
| baths | Number | Number of bathrooms |
| sqft | Number | Living area in square feet |
| lotSize | String | Lot size (e.g., "8,000 sqft") |
| yearBuilt | Number | Year the property was constructed (*detail*) |
| propertyType | String | Property type (e.g., SINGLE_FAMILY, CONDO, TOWNHOUSE; BUILDING for apartment buildings) |
| stories | Number | Number of stories (*detail*) |
| parking | String | Parking details (e.g., "2 garage spaces") (*detail*) |
| hoaFee | Number | Monthly HOA fee (*detail*) |
| pricePerSqft | Number | Price per square foot (*detail*) |
| daysOnZillow | Number | Days the property has been listed on Zillow |

### Location

| Field | Type | Description |
|-------|------|-------------|
| address | String | Street address |
| city | String | City name |
| state | String | State code (e.g., "TX") |
| zipCode | String | ZIP code |
| latitude | Number | Latitude coordinate |
| longitude | Number | Longitude coordinate |

### Agent and broker

| Field | Type | Description |
|-------|------|-------------|
| brokerName | String | Brokerage company name |
| agentName | String | Listing agent name (*detail*) |
| agentPhone | String | Listing agent phone number (*detail*) |

### Rich data (from detail pages, when `scrapeDetails` is on)

| Field | Type | Description |
|-------|------|-------------|
| description | String | Full property description text (in search-only results for apartment buildings, this holds the building name) |
| photos | Array | Photo URLs for the listing (search results carry only the main photo) |
| priceHistory | Array | Price change events — date, event type, price, price per sqft, source |
| taxHistory | Array | Tax records — year, tax paid, assessed value, change rate |
| schools | Array | Nearby schools — name, level, grades, distance, rating, type |
| features | Object | Property features — heating, cooling, flooring, roofing, pool, fireplace, construction, and more |
| scrapedAt | String | ISO timestamp when data was collected (always present) |

### Sample output

```json
{
    "url": "https://www.zillow.com/homedetails/46-Kingwood-Greens-Dr-Kingwood-TX-77339/28065573_zpid/",
    "zpid": 28065573,
    "status": "FOR_SALE",
    "price": 318000,
    "zestimate": 325000,
    "rentZestimate": 2400,
    "beds": 5,
    "baths": 4,
    "sqft": 5526,
    "lotSize": "22,346 sqft",
    "yearBuilt": 2000,
    "propertyType": "SINGLE_FAMILY",
    "stories": 2,
    "parking": "3 garage spaces",
    "hoaFee": 150,
    "pricePerSqft": 58,
    "daysOnZillow": 14,
    "address": "46 Kingwood Greens Dr",
    "city": "Kingwood",
    "state": "TX",
    "zipCode": "77339",
    "latitude": 30.033194,
    "longitude": -95.180402,
    "brokerName": "REALHome Services and Solutions, Inc.",
    "agentName": "Lori Brown",
    "agentPhone": "(979) 255-0702",
    "description": "Spacious 5 bedroom home in Kingwood with pool and 3-car garage. Updated kitchen, hardwood floors throughout, and large backyard with mature trees...",
    "photos": [
        "https://photos.zillowstatic.com/fp/example1.jpg",
        "https://photos.zillowstatic.com/fp/example2.jpg"
    ],
    "priceHistory": [
        {
            "date": "2026-03-01",
            "event": "Listed",
            "price": 318000,
            "pricePerSqft": 58,
            "priceChangeRate": 0,
            "source": "HAR"
        },
        {
            "date": "2002-01-03",
            "event": "Sold",
            "price": 215000,
            "pricePerSqft": 39,
            "priceChangeRate": 0,
            "source": "Public Record"
        }
    ],
    "taxHistory": [
        {
            "year": 2025,
            "taxPaid": 8500,
            "value": 310000,
            "taxIncreaseRate": 0.02,
            "valueIncreaseRate": 0.03
        }
    ],
    "schools": [
        {
            "name": "Kingwood Park High School",
            "level": "High",
            "grades": "9-12",
            "distance": 1.2,
            "rating": 7,
            "type": "public"
        }
    ],
    "features": {
        "heating": ["Central"],
        "cooling": ["Central Air"],
        "flooring": ["Hardwood", "Tile"],
        "roofType": "Composition",
        "poolFeatures": ["In Ground"],
        "parkingFeatures": ["Attached Garage"]
    },
    "scrapedAt": "2026-03-25T12:00:00.000000+00:00"
}
```

## Input

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `search` | String | – | City and state (or ZIP) to search (e.g., "Houston, TX", "Miami, FL"). |
| `mode` | Select | `BUY` | `BUY` (for sale), `RENT` (for rent), or `SOLD` (recently sold). Applies to `search` only; search-page URLs keep their own filters. |
| `maxItems` | Integer | `50` | Max properties for the whole run (1–500), including direct property URLs. |
| `endPage` | Integer | `5` | Max result pages per search (1–20). Each page returns up to 40 properties. |
| `scrapeDetails` | Boolean | `true` | Fetch full detail pages for enriched data (schools, history, features, etc.). Disable for faster runs. |
| `startUrls` | URL List | – | Direct Zillow property detail URLs (`/homedetails/`, `_zpid`, `/apartments/`) or search page URLs. |

**Note:** at least one of `search` or `startUrls` must be provided.

### Example: buy properties

```json
{
    "search": "Houston, TX",
    "mode": "BUY",
    "maxItems": 50,
    "scrapeDetails": true
}
```

### Example: rental search

```json
{
    "search": "Miami, FL",
    "mode": "RENT",
    "maxItems": 25
}
```

### Example: recently sold

```json
{
    "search": "Denver, CO",
    "mode": "SOLD",
    "maxItems": 30,
    "endPage": 3
}
```

### Example: direct property URL

```json
{
    "startUrls": [
        { "url": "https://www.zillow.com/homedetails/123-Main-St-Houston-TX-77001/12345678_zpid/" }
    ],
    "scrapeDetails": true
}
```

## Use cases

- **Investment analysis** — compare listing prices, Zestimates, and price history to spot undervalued properties
- **Market research** — track listing and sold prices, and days on market, across neighborhoods
- **Rental analysis** — compare rental prices and rent Zestimates by location
- **School district research** — find properties near top-rated schools with distance and rating data
- **Agent and broker research** — identify which agents and brokerages are active in a target market
- **Price trend monitoring** — track price reductions, relists, and final sale prices for market timing

## FAQ

**Do I need to configure a proxy?**
No. There are no proxy settings to fill in.

**What is the difference between BUY, RENT, and SOLD modes?**
BUY searches active for-sale listings, RENT searches rental apartments and homes, and SOLD searches recently sold properties. The mode only changes which Zillow search is run; the record fields are the same.

**What is a Zestimate?**
A Zestimate is Zillow's proprietary estimated market value for a property. The rent Zestimate is a similar estimate for what a property could rent for monthly. Both are included in the output when available.

**How many properties can I scrape per run?**
Up to 500 properties per run. Each search page returns up to 40 listings, and you can configure up to 20 pages per search. A search stops early when Zillow returns a page with fewer than 40 listings.

**Why are some fields missing from certain properties?**
Not all Zillow listings have complete data — some may lack a Zestimate, tax history, school data, or an HOA fee depending on the property and location. Those fields are simply left out rather than returned empty.

**What happens if I set `scrapeDetails` to false?**
Runs finish significantly faster. You still get core listing data (price, beds, baths, sqft, address, Zestimate where shown) from search results, but not year built, HOA fee, agent details, schools, tax history, price history, full descriptions, or property features. Direct property URLs return only `url` and `zpid` in this case.

**Can I search a specific ZIP code or neighborhood?**
Yes. Enter it in `search` using formats like "77339" (ZIP code), "Kingwood, TX" (neighborhood and state), or any location Zillow recognizes.

**Can I scrape specific Zillow URLs directly?**
Yes. Paste any Zillow property detail or search results page URL into `startUrls`, combined with or instead of a location search. Search-page URLs are read with their own filters and paged with `endPage`; property URLs are added after the search results until `maxItems` is reached.

**How current is the data?**
The actor reads live data from Zillow.com at the time of each run. Every record includes a `scrapedAt` timestamp so you know exactly when it was collected.

**Is this affiliated with Zillow?**
No. It is an independent tool that reads publicly visible Zillow pages.
