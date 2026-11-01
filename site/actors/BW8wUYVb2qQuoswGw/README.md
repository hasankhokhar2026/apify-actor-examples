# Zillow For-Sale, Rent & Sold Listing Extractor

Scrape **Zillow** for active for-sale, rental and recently sold listings. Search by city, ZIP, neighborhood, county or state, paste property, building or search URLs, or look up properties by ZPID and street address. Apply Zillow's own price, size, property-type, amenity and rental filters, then enrich each record with detail data such as tax history, schools, MLS attribution, open houses, photos, floor plans and listing flags when Zillow exposes them.

This actor is independent and is not affiliated with Zillow. It reads publicly visible pages and requires no login, cookie or proxy configuration.

## What this actor does

- **Three search modes:** active for-sale (`BUY`), rental (`RENT`) and recently sold (`SOLD`) listings by location.
- **Flexible lookups:** property detail URLs, `/apartments/` building URLs, Zillow search URLs, ZPIDs and full street addresses.
- **Deep filters:** price, beds, baths, square footage, lot size, year built, HOA, parking, property type, days on Zillow, sort order, listing flags, keyword, amenities and rent-only filters.
- **Rich detail:** tax history, schools, RESO features, price history, MLS data, open houses, photos, virtual tours, building floor plans and walk/transit/bike scores.
- **Empty fields are omitted** — records contain only populated values, and duplicate properties are merged by ZPID and canonical URL.

## Output per property

Each property or rental building produces one record. Fields with no available data are omitted, never emitted as `null`, `N/A`, `-` or an empty container. Meaningful zero and false values are kept.

### Core fields

| Field | Type | Description |
|---|---|---|
| `url` | String | Absolute Zillow detail URL. |
| `zpid` | Number or String | Numeric for properties; string for buildings. |
| `status` | String | Listing status such as `FOR_SALE`, `FOR_RENT`, `RECENTLY_SOLD` or `SOLD`. |
| `price` | Integer | Listing price; never zero. For sold records, the sold price when disclosed. |
| `zestimate` | Integer | Zillow estimated value. |
| `rentZestimate` | Integer | Zillow estimated monthly rent. |
| `beds` | Integer | Bedrooms. |
| `baths` | Number | Bathrooms. |
| `sqft` | Integer | Living area in square feet. |
| `lotSize` | String | Formatted lot size, for example `1,846 sqft` or `0.27 acres`. |
| `yearBuilt` | Integer | Construction year. |
| `propertyType` | String | `SINGLE_FAMILY`, `CONDO`, `TOWNHOUSE`, `BUILDING`, etc. |
| `stories` | Integer | Stories when Zillow provides them. |
| `parking` | String | Parking features or capacity. |
| `address`, `city`, `state`, `zipCode` | String | Address components. |
| `latitude`, `longitude` | Number | Coordinates. |
| `daysOnZillow` | Integer | Days on Zillow. |
| `brokerName`, `agentName`, `agentPhone` | String | Listing attribution. |
| `description` | String | Property or building description. |
| `photos` | Array | Absolute photo URLs. |
| `priceHistory` | Array | Price events with `date`, `event`, `price`, `pricePerSqft`, `priceChangeRate` and `source`. |
| `taxHistory` | Array | Tax records with `year`, `taxPaid`, `value`, `taxIncreaseRate` and `valueIncreaseRate`. |
| `schools` | Array | Assigned schools preferred; each entry keeps `name`, `level`, `type`, `grades`, `distance` and `rating`. |
| `features` | Object | Expanded RESO facts: heating, cooling, appliances, flooring, basement, parking, pool, views, construction, lot and similar details when present. |
| `hoaFee` | Number | Monthly HOA fee. |
| `pricePerSqft` | Number | Price per square foot. |
| `scrapedAt` | String | ISO timestamp; always present. |

### Additive fields

| Field | Type | Description |
|---|---|---|
| `soldPrice` | Integer | Sold price when the market discloses it. |
| `lastSoldPrice` | Integer | Most recent recorded sold price from the property payload. |
| `dateSold` | String | ISO sold date. |
| `taxAssessedValue` | Integer | Tax assessed value. |
| `taxAnnualAmount` | Integer | Annual property tax amount. |
| `parcelId` | String | County parcel or assessor ID, preserving leading zeros. |
| `builderName` | String | Home builder or developer when exposed. |
| `agentEmail` | String | Listing agent email when Zillow exposes it. |
| `propertyTaxRate` | Number | Percentage tax rate (`1.75` means 1.75%). |
| `priceChange` | Integer | Signed price change. |
| `priceChangeDate` | String | ISO date of the last price change. |
| `openHouse` | Array | Entries with `startTime`, `endTime` and optional `description`. |
| `mlsName`, `mlsId` | String | MLS attribution. |
| `photoCount` | Integer | Number of photos. |
| `virtualTour` | String | Virtual tour or 3D home URL. |
| `homeInsights` | Array | Insight phrases. |
| `neighborhood`, `county` | String | Location context. |
| `garageSpaces` | Integer | Garage capacity. |
| `unit` | String | Unit number. |
| `has3DModel` | Boolean | Whether a 3D model is available. |
| `listingFlags` | Object | `isForSaleByOwner`, `isForeclosure`, `isAuction`, `isNewConstruction`, `isPending`, `isListedByOwner`, `isComingSoon`, `isBankOwned`. |
| `building` | Object | Rental-building detail; see below. |

### Building object

| Field | Type | Description |
|---|---|---|
| `building.name` | String | Building name. |
| `building.type` | String | Building type. |
| `building.phone` | String | Leasing phone number. |
| `building.agentName` | String | Leasing contact name. |
| `building.availabilityCount` | Integer | Number of available units. |
| `building.rentRange` | Object | `min` and `max` monthly rent. |
| `building.floorPlans` | Array | Available units; see below. |
| `building.walkScore` | Integer | Walk Score. |
| `building.transitScore` | Integer | Transit score. |
| `building.bikeScore` | Integer | Bike score. |
| `building.amenities` | Array | Building and community amenities. |
| `building.petPolicy` | String | Pet policy. |
| `building.specialOffers` | Array | Leasing specials. |
| `building.neighborhoodDescription` | String | Neighborhood overview. |

Each `building.floorPlans` entry can include `floorPlanName`, `unitNumber`, `beds`, `baths`, `sqft`, `price`, `baseRent`, `availableFrom`, `leaseTerm`, `deposit` and `fees` (`min` and `max`).

## Input

All inputs are optional individually, but at least one source is required: `search`, `startUrls`, `zpids` or `addresses`.

| Field | Type | Default | Description |
|---|---|---|---|
| `search` | String | – | City, ZIP, neighborhood, county or state to search. Prefill: `Houston, TX`. |
| `mode` | Select | `BUY` | `BUY`, `RENT` or `SOLD`. Applies to `search` and bare location URLs. |
| `maxItems` | Integer | `50` (prefill `3`) | Maximum records for the whole run (1-5000), across all sources. |
| `endPage` | Integer | `5` (prefill `1`) | Maximum search pages per task (1-24). Zillow returns up to 41 listings per page. |
| `startUrls` | URL list | `[]` | Property detail URLs, `/apartments/` building URLs or Zillow search-page URLs. Search URLs keep their own filters and mode. |
| `zpids` | String list | – | ZPID values or URLs containing `_zpid`. Each is resolved to its detail page. |
| `addresses` | String list | – | Full street addresses, for example `1306 Castle Ct, Houston, TX 77006`. |
| `priceMin` | Integer | – | Minimum listing price in US dollars. |
| `priceMax` | Integer | – | Maximum listing price in US dollars. |
| `bedsMin` | Select | `any` | Minimum bedrooms: `any`, `1`, `2`, `3`, `4`, `5`. |
| `bathsMin` | Select | `any` | Minimum bathrooms: `any`, `1`, `1.5`, `2`, `2.5`, `3`, `4`, `5`. |
| `sqftMin` | Integer | – | Minimum living area in square feet. |
| `sqftMax` | Integer | – | Maximum living area in square feet. |
| `lotSizeMin` | Select | `any` | Minimum lot size: `any`, `2000`, `5000`, `10890`, `21780`, `43560`, `87120` square feet. |
| `lotSizeMax` | Select | `any` | Maximum lot size: `any`, `2000`, `5000`, `10890`, `21780`, `43560`, `87120` square feet. |
| `yearBuiltMin` | Integer | – | Earliest construction year. |
| `yearBuiltMax` | Integer | – | Latest construction year. |
| `hoaMax` | Integer | – | Maximum monthly HOA fee. |
| `parkingSpotsMin` | Integer | – | Minimum parking spots (1-10). |
| `propertyTypes` | Multi-select | – | `house`, `condo`, `townhouse`, `multiFamily`, `manufactured`, `lotLand`, `apartment`. Empty means all homes. |
| `daysOnZillow` | Select | `any` | `any`, `1`, `7`, `14`, `30`, `90`, `180`, `365`, `730`, `1095` days. |
| `sortBy` | Select | `relevance` | `relevance`, `priceLow`, `priceHigh`, `newest`, `zestimate`, `zestimateLow`. RENT relevance uses Zillow's priority order. |
| `fsboOnly` | Boolean | `false` | Only for-sale-by-owner listings. |
| `foreclosureOnly` | Boolean | `false` | Only foreclosure listings. |
| `auctionOnly` | Boolean | `false` | Only auction listings. |
| `newConstructionOnly` | Boolean | `false` | Only new-construction listings. |
| `includePending` | Boolean | `false` | Add pending and under-contract listings to active results. |
| `openHouseOnly` | Boolean | `false` | Only listings with an open house. |
| `priceReducedOnly` | Boolean | `false` | Only listings with a price reduction. |
| `keyword` | String | – | Free-text keyword, for example `pool`. |
| `amenities` | Multi-select | – | `pool`, `garage`, `airConditioning`, `waterfront`, `cityView`, `threeDHome`, `age55Plus`, `singleStory`, `basementFinished`, `basementUnfinished`, `waterView`, `mountainView`, `parkView`. |
| `rentalFilters` | Multi-select | – | Rent-only: `pets`, `furnished`, `parking`, `inUnitLaundry`, `shortTerm`, `noPets`, `byOwner`, `incomeRestricted`, `studentHousing`, `onlyRentalSeniorHousingType`, `hasFitnessCenter`, `hasDishwasher`, `onlyRentalInstantTourAvailable`, `hasAcceptingBackupOffers`. |
| `scrapeDetails` | Boolean | `true` (prefill `false`) | Enrich search results with detail data. Explicit URLs, ZPIDs and addresses are always enriched. |

Inverted ranges (`priceMin > priceMax`, `sqftMin > sqftMax`, `yearBuiltMin > yearBuiltMax`, `lotSizeMin > lotSizeMax`) are ignored with a status note instead of failing the run. Rental filters are ignored outside `RENT` mode.

### Example: buy search with filters

```json
{
  "search": "Houston, TX",
  "mode": "BUY",
  "maxItems": 100,
  "endPage": 5,
  "priceMin": 500000,
  "priceMax": 800000,
  "bedsMin": "3",
  "bathsMin": "2",
  "amenities": ["pool"],
  "daysOnZillow": "30",
  "sortBy": "newest",
  "scrapeDetails": true
}
```

### Example: pet-friendly rentals with rental filters

```json
{
  "search": "Miami, FL",
  "mode": "RENT",
  "maxItems": 50,
  "rentalFilters": ["pets", "parking", "furnished"],
  "scrapeDetails": false
}
```

### Example: recently sold comps

```json
{
  "search": "Miami, FL",
  "mode": "SOLD",
  "maxItems": 50,
  "endPage": 2,
  "scrapeDetails": true
}
```

### Example: direct property, building and ZPID lookups

```json
{
  "startUrls": [
    {"url": "https://www.zillow.com/homedetails/1306-Castle-Ct-Houston-TX-77006/126296894_zpid/"},
    {"url": "https://www.zillow.com/apartments/houston-tx/the-briscoe-river-oaks/5Xhrvw/"}
  ],
  "zpids": ["126296894"],
  "addresses": ["1306 Castle Ct, Houston, TX 77006"],
  "maxItems": 10
}
```

## Use cases

- **Real estate investors** — pull for-sale, pending and price-reduced listings with tax, HOA and price-history context for deal screening.
- **Real estate agents and brokers** — track new construction, open houses, FSBO and auction inventory in target neighborhoods.
- **Property managers and landlords** — compare rental inventory, amenities, pet policies and floor-plan pricing in a market.
- **Appraisers and analysts** — collect recently sold comps with sold dates, assessed values and school assignments for valuation work.
- **Proptech and data teams** — feed normalized Zillow listing, tax and building data into CRMs, dashboards and valuation models.
- **Relocation and home-search services** — build filtered shortlists by price, commute-relevant location, schools and amenities.

## FAQ

### Do I need a proxy, cookie or API key?

No. The actor reads publicly visible Zillow pages, chooses a working connection automatically and requires no credential or proxy setup.

### What is the difference between BUY, RENT and SOLD?

`BUY` searches active for-sale listings, `RENT` searches rentals, and `SOLD` searches recently sold listings. The mode applies to `search` and bare location URLs; pasted search URLs keep their own mode and filters.

### How many listings can one search return?

Zillow's search exposes at most about 975 unique listings per query, across 24 pages of 41 rows. When `maxItems` is above 975 and Zillow reports more results, the actor splits the search into smaller price bands — and for rentals, by monthly payment, beds and days on Zillow — so it can keep collecting listings. Searches at or below that ceiling return the listings Zillow exposes directly.

### Why is `soldPrice` missing for some sold listings?

Some markets, including Houston, are non-disclosure markets, and Zillow does not publish a sold price there. The record keeps the sold date and status, and the actor never invents a price from Zestimate or price history.

### Why are tax history, schools or HOA details missing on some records?

Zillow only publishes those details for some listings and markets. When a value is absent it is omitted from the record rather than filled from another field. Tax-history years are reported as calendar years.

### Can I paste a Zillow search URL?

Yes. The actor reads the URL's search state and keeps its filters. If the URL points to page N, the actor starts from page 1 and pages forward up to `endPage`.

### Can I use a `/b/` building URL?

Zillow blocks `/b/` building URLs for public access. Use the `/apartments/` URL for the same building instead; `/b/` URLs are skipped with a status note.

### How current is the data?

Every record is read live at run time and includes a `scrapedAt` timestamp. Zillow's result count and ordering can drift between requests, so duplicates are removed within each run.

### Are zero values removed?

No. Meaningful zero values such as `beds: 0` for a studio and false listing flags are kept. Only empty, null, sentinel and non-finite values are removed.

### Are building reviews included?

No. Zillow does not expose building reviews on public building pages, so the actor does not emit them. Building details, floor plans, amenities and scores are included when available.
