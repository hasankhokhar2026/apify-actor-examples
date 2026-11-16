# Zonaprop Argentina Property Search & Geolocation Scraper

Zonaprop is Argentina's leading property portal, listing apartments, houses, land, PH units and commercial properties for sale and rent from Buenos Aires to every province. This actor runs a Zonaprop search — either from a pasted search URL or from location/property/operation filters — and returns each listing as a structured record with price, GPS coordinates, surface area, rooms, photos and publisher contact details.

## What this actor does

- Scrapes any Zonaprop search results URL you paste in directly, respecting all filters already embedded in it (price range, rooms, neighborhood, etc.)
- Builds a search from structured filters instead — operation type (sale, rent, temporary), property type, and location slug
- Extracts full address-level location data, including neighborhood, city, province and GPS coordinates
- Captures publisher details (agent, owner or agency name, type and phone) and the complete photo gallery for each listing
- Empty fields are omitted from records — a field only appears when Zonaprop actually published that data for the listing

## Output per listing

- `title`, `description` — listing headline and full description text
- `url` — direct link to the listing on Zonaprop
- `listingId` — unique Zonaprop listing identifier
- `listingType` — `sale`, `rent`, or `temporary`
- `propertyType` — `apartment`, `house`, `land`, `ph`, or `commercial`
- `publishDate` — date the listing was published
- `daysOnMarket` — days since publication
- `price` — listing price
- `currency` — `USD` or `ARS`
- `pricePerSqm` — price per square meter
- `address` — street address
- `neighborhood` — neighborhood (barrio)
- `city`, `province`
- `latitude`, `longitude` — GPS coordinates
- `rooms` — total ambientes (main living spaces)
- `bedrooms`, `bathrooms`
- `totalArea`, `coveredArea` — total and covered surface area in m²
- `garages` — number of garage spaces
- `yearBuilt`
- `images` — array of listing photo URLs
- `mainImage` — primary photo URL
- `publisherName` — agent or agency name
- `publisherType` — `agent`, `owner`, or `agency`
- `publisherPhone`
- `scrapedAt` — UTC timestamp when the record was collected

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchUrl` | string | – | A Zonaprop search results URL; takes priority over the filter fields below when provided |
| `propertyType` | string | `all` | `all`, `apartment`, `house`, `land`, `ph`, or `commercial`; ignored when `searchUrl` is set |
| `operationType` | string | `sale` | `sale`, `rent`, or `temporary`; ignored when `searchUrl` is set |
| `location` | string | – | City or neighborhood slug as it appears in Zonaprop URLs, e.g. `capital-federal`, `palermo`, `cordoba`; ignored when `searchUrl` is set |
| `maxResults` | integer | `100` | Maximum number of listings to return (1–1000) |
| `proxyConfiguration` | object | – | Proxy settings; Argentina residential proxy is recommended for reliable access |

### Example: paste a search URL directly

```json
{
  "searchUrl": "https://www.zonaprop.com.ar/departamentos-venta-capital-federal.html",
  "maxResults": 100
}
```

### Example: houses for rent in Córdoba by filters

```json
{
  "propertyType": "house",
  "operationType": "rent",
  "location": "cordoba",
  "maxResults": 60
}
```

### Example: commercial properties for sale in Rosario

```json
{
  "propertyType": "commercial",
  "operationType": "sale",
  "location": "rosario",
  "maxResults": 40
}
```

## Use cases

- **Market research** — track asking prices and days-on-market across Buenos Aires neighborhoods or other Argentine cities
- **Investment analysis** — compare `pricePerSqm` across barrios to spot under- or over-priced areas
- **Rental monitoring** — collect rental listings across CABA and Greater Buenos Aires to analyze going rates
- **Agency lead generation** — gather `publisherName`/`publisherPhone` for agencies active in a target area
- **Portfolio tracking** — watch competing listings for developers and property managers in specific neighborhoods

## FAQ

**How do I use a Zonaprop search URL instead of the filter fields?** Apply whatever filters you want on zonaprop.com.ar (neighborhood, price range, rooms, etc.), copy the resulting page URL, and paste it into `searchUrl`. The actor follows that exact search, including every filter embedded in the URL.

**What property types are covered?** All of Zonaprop's major categories: apartments (departamentos), houses (casas), land (terrenos), PH units, and commercial properties (locales, offices, warehouses).

**What does `rooms` ("ambientes") mean?** It's the Argentine term for a property's total main living spaces — typically bedrooms plus living/dining area, not counting bathrooms. A 3-ambiente apartment usually has 2 bedrooms plus a combined living/dining room; this is captured in the `rooms` field.

**Why are some prices in USD and others in ARS?** Zonaprop sellers choose which currency to list in; the `currency` field tells you which applies to that listing's `price`, so always check it before comparing prices across records.

**How many listings can one run return?** Up to `maxResults`, capped at 1000. For broader coverage, run multiple searches with different locations or filters.

**Do I need a proxy to run this?** An Argentina residential proxy is recommended for reliable access to Zonaprop's pages; set it via the `proxyConfiguration` input.

**Is this affiliated with Zonaprop?** No. This is an independent, third-party actor that reads Zonaprop's publicly available listing pages; it is not operated by or affiliated with Zonaprop/Navent.
