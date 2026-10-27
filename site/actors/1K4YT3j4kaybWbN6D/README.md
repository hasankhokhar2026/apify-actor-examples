# AutoScout24 Car Search Across 9 European Markets

Search AutoScout24's used and new car listings across nine European country domains, with the same filters (make, price, mileage, power, body type and more) AutoScout24's own search uses, or fetch full detail records for specific listing URLs.

## What this actor does

- Searches AutoScout24 by make, model, year, price, mileage, fuel type, transmission, body type, power, doors/seats and seller type, in any of nine country markets
- Fetches full detail records — including body type, color, doors and seats — for specific listing URLs you already have
- Normalizes fuel type and transmission into the same English values on every country domain
- Returns up to 20 photo URLs per listing
- Omits any field a listing doesn't carry rather than returning a null or placeholder value

## Output per listing

| Field | Description |
|---|---|
| `id` | Unique listing UUID |
| `make` / `model` / `variant` | Manufacturer, model name and trim/variant |
| `year` | First registration year |
| `condition` | `new` or `used` |
| `mileageKm` | Mileage in kilometres |
| `priceEur` | Listed price as a number. It is taken as shown on the chosen country site without currency conversion, so on a site that lists prices in another currency (such as Switzerland) the figure is in that currency |
| `fuelType` | `petrol`, `diesel`, `electric`, `hybrid`, `lpg`, `cng`, `hydrogen` or `ethanol` |
| `transmission` | `automatic`, `manual` or `semi-automatic` |
| `bodyType` | Body type (e.g. Saloon, SUV) — in practice only on `getCarDetails` records |
| `bodyColor` | Exterior color — in practice only on `getCarDetails` records |
| `powerKw` / `powerHp` | Engine power in kW and HP |
| `displacement` | Engine displacement in cc |
| `driveTrain` | Drive train (RWD, FWD, 4WD) |
| `cylinders` | Number of cylinders |
| `doors` / `seats` | Door and seat counts — in practice only on `getCarDetails` records |
| `firstRegistration` | First registration date |
| `fuelConsumption` | Published WLTP fuel consumption |
| `co2EmissionsGkm` | CO2 emissions in g/km |
| `location` | "City, Country" summary |
| `city` | City name |
| `countryCode` | Country code, e.g. DE, AT |
| `zip` | Postal code |
| `sellerType` | Dealer or Private |
| `sellerName` | Seller/dealer company name |
| `sellerContact` | Named contact person at the seller, when published |
| `sellerId` | Seller's AutoScout24 ID |
| `sellerRatingStars` | Dealer rating out of 5 |
| `sellerRatingCount` | Number of ratings behind that score |
| `photos` | Up to 20 photo URLs |
| `listingUrl` | Full listing URL |
| `sourceUrl` | Same as `listingUrl` |
| `modelGroup` | Manufacturer's broader model family/group, when published |
| `paintType` | Paint finish (e.g. metallic), when published |
| `crossReferenceId` | Legacy numeric AutoScout24 listing ID |
| `upholstery` / `upholsteryColor` | Interior upholstery material and color — populated on `getCarDetails` records only |
| `gears` | Number of gears — populated on `getCarDetails` records only |
| `hsnTsn` | German HSN/TSN type-approval numbers, when published — populated on `getCarDetails` records only |
| `description` | Seller's free-text listing description — populated on `getCarDetails` records only |
| `isDeliverable` | Whether the seller offers delivery — populated on `getCarDetails` records only |
| `isNew` | Boolean new/used flag from the detail page, alongside `condition` — populated on `getCarDetails` records only |
| `recordType` | Always `"carListing"` |
| `scrapedAt` | UTC ISO timestamp of when the record was scraped |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string (required) | searchCars | `searchCars` runs a filtered search; `getCarDetails` fetches specific listing URLs |
| `make` | string | – | Car brand from the list (32 makes), e.g. BMW, Volkswagen, Mercedes-Benz. Leave blank for any make. |
| `model` | string | – | Model name as AutoScout24 spells it in its URLs, e.g. "x5", "golf", "a4" (spaces become hyphens). Only used together with `make` |
| `yearFrom` / `yearTo` | integer | – | First registration year range (1900–2026) |
| `priceFrom` / `priceTo` | integer | – | Price range in EUR (0–10,000,000) |
| `mileageMax` | integer | – | Maximum mileage in kilometres (0–2,000,000) |
| `fuelType` | string | (any) | petrol, diesel, electric, hybrid, hydrogen, lpg, cng |
| `transmission` | string | (any) | automatic, manual, semi-automatic |
| `country` | string | `de` | Country site: de, at, be, fr, it, nl, pl, es, ch |
| `condition` | string | `""` (any) | New (`N`) or Used (`U`); search only |
| `bodyType` | string | (any) | Small car, Convertible/Cabrio, Coupe, SUV/Off-road/Pickup, Estate/Kombi, Sedan/Limousine, Van/Minibus, Panel van/Transporter, Other |
| `powerFrom` / `powerTo` | integer | – | Engine power range (0–2000), in the unit set by `powerUnit` |
| `powerUnit` | string | kw | Unit for `powerFrom`/`powerTo`: kw or hp |
| `doorsFrom` / `doorsTo` | integer | – | Door count range (2–7) |
| `seatsFrom` / `seatsTo` | integer | – | Seat count range (1–12) |
| `sellerType` | string | (any) | dealer or private |
| `listingUrls` | array | – | AutoScout24 listing URLs to fetch — used in `getCarDetails` mode |
| `maxItems` | integer | `100` | Maximum number of listings to return (1–1000; a single search stops at 400, see FAQ) |

### Example: filtered diesel BMW search in Germany

```json
{
  "mode": "searchCars",
  "make": "BMW",
  "fuelType": "diesel",
  "bodyType": "4",
  "powerFrom": 100,
  "powerTo": 250,
  "powerUnit": "kw",
  "sellerType": "dealer",
  "yearFrom": 2015,
  "yearTo": 2022,
  "priceFrom": 10000,
  "priceTo": 40000,
  "country": "de",
  "maxItems": 50
}
```

### Example: broad search in another market

```json
{
  "mode": "searchCars",
  "country": "nl",
  "fuelType": "electric",
  "maxItems": 100
}
```

### Example: fetch specific listings

```json
{
  "mode": "getCarDetails",
  "listingUrls": ["https://www.autoscout24.de/offers/bmw-318d-fa84e6e3"]
}
```

### Filter notes

- `bodyType`, `doorsFrom`/`doorsTo`, and `seatsFrom`/`seatsTo` narrow the search server-side, but AutoScout24's search-result data doesn't carry body type, doors or seats on individual listings — those output fields only populate when you fetch the listing with `getCarDetails`.
- `powerFrom`/`powerTo`/`powerUnit` and `sellerType` are applied server-side and match the `powerKw`/`powerHp`/`sellerType` output fields on every record.
- Exterior color is not a filterable search parameter on AutoScout24; `bodyColor` is still available as an output field on `getCarDetails` records.
- The price, year, mileage, fuel, transmission, power, doors, seats, body type and seller filters are also checked against each record, including in `getCarDetails` mode. A listing is only dropped when it has the value and it falls outside your filter; listings missing that value are kept.

## Use cases

- **Price and spec comparison** — pull listings for a make/model across markets to compare pricing and mileage
- **Dealer inventory monitoring** — track a dealer's stock over time using `sellerId` and `sellerName`
- **Lead sourcing for buyers** — filter by budget, power range and seller type to shortlist cars worth contacting
- **Market research** — compare fuel type and body type mix between countries
- **Listing enrichment** — pass previously collected listing URLs through `getCarDetails` to fill in doors, seats, body type and color

## FAQ

**Which countries are supported?**
Germany (de), Austria (at), Belgium (be), France (fr), Italy (it), Netherlands (nl), Poland (pl), Spain (es) and Switzerland (ch), each on its own AutoScout24 domain.

**Is the Switzerland market as reliable as the others?**
autoscout24.ch has occasionally returned a blocked response to non-browser requests; this is specific to that one country domain and doesn't affect the other eight markets. If a `country: "ch"` run comes back empty, retry later or use a different country.

**How many listings can one search return?**
The actor reads at most 20 result pages of 20 listings, so one search returns up to 400 listings even if `maxItems` is higher. Use make, model, price bands or other filters to split a broad search into several narrower runs.

**Can I search without make or model?**
Yes — leaving both blank returns listings for the chosen country with whatever other filters you've set.

**Do I need an AutoScout24 account or a proxy?**
No. All data comes from AutoScout24's public search and listing pages; there are no login, API key or proxy inputs.

**Why are some fields, like `bodyType` or `doors`, missing from search results?**
AutoScout24's search-result data doesn't include those details on every listing; they are filled in automatically when you fetch the same listing through `getCarDetails`.

**Is this affiliated with AutoScout24?**
No. This actor reads AutoScout24's public pages and is not affiliated with, endorsed by, or sponsored by AutoScout24.
