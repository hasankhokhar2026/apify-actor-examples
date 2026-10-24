# Booking.com Hotel Price & Amenity Search Scraper

Search Booking.com for a destination and your travel dates, and get back one row per property with price, guest rating, review count, amenity keywords, and breakfast availability. Booking.com's own property-type and review-score filters are applied to the search itself.

## What this actor does

- Runs one Booking.com search for your destination, check-in/check-out dates, guest count, and room count, and reads the property cards on the results page
- Returns current price alongside the original price when a discount is shown
- Reports guest rating, review count, and the rating label Booking.com displays (e.g. "Excellent")
- Picks out amenity keywords mentioned on each card and whether breakfast is included
- Applies Booking.com's property-type filter (hotels, apartments, hostels, guesthouses, villas, resorts) and its review-score filter (6+, 7+, 8+ or 9+)
- Every record includes every field, using an empty string, `0`, or `false` when Booking.com doesn't show that detail for a property

## Output per hotel

- `name` — property name
- `url` — direct Booking.com link
- `price`, `originalPrice`, `currency` — the price shown on the card for your dates and guests (Booking.com usually shows the total for the whole stay), the struck-through pre-discount price (`0` when there is none), and the currency symbol as displayed (e.g. `$`, `€`)
- `rating`, `reviewCount`, `reviewWord` — guest rating out of 10, number of reviews, and Booking.com's rating label (`0`/empty for properties without reviews)
- `address`, `city`, `distance` — address text from the card, the city taken from the property's Booking.com URL (e.g. `paris`; falls back to your `location`), and the distance text Booking.com shows (e.g. from the centre)
- `photoUrl` — main listing photo
- `amenities` — lowercase amenity keywords found in the card's text (e.g. `wifi`, `parking`, `pool`, `kitchen`); a card only mentions a few highlights, so this isn't the property's full facility list
- `breakfastIncluded` — `true` when the card says breakfast is included
- `checkin`, `checkout` — the stay dates used for this search
- `scrapedAt` — ISO 8601 collection timestamp

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `location` | string | – | **Required.** City, region, or destination to search |
| `checkinDate` | string | – | Check-in date (`YYYY-MM-DD`); defaults to tomorrow when left empty |
| `checkoutDate` | string | – | Check-out date (`YYYY-MM-DD`); when left empty it is set to 4 days from today (a 3-night stay with the default check-in), so set it whenever you set `checkinDate` |
| `adults` | integer | `2` | Number of adult guests (1–30) |
| `rooms` | integer | `1` | Number of rooms needed (1–30) |
| `currency` | string | `USD` | Currency code Booking.com should show prices in |
| `propertyType` | string | `all` | `all` / `hotels` / `apartments` / `hostels` / `guesthouses` / `villas` / `resorts` |
| `minRating` | number | `0` | Minimum guest review score (0–10), rounded down to Booking.com's 6+/7+/8+/9+ filter; values below 6 apply no filter |
| `maxResults` | integer | `50` | Maximum hotel listings to return (1–500); the actor loads more results up to 10 times, so very high values may not be reached |
| `proxyConfiguration` | object | – | Strongly recommended (the form is prefilled with a residential proxy); Booking.com blocks data-center IPs, and runs without a proxy usually fail |

### Example: weekend stay in Paris

```json
{
  "location": "Paris",
  "checkinDate": "2026-06-12",
  "checkoutDate": "2026-06-14",
  "adults": 2,
  "maxResults": 30
}
```

### Example: budget hostels for a group

```json
{
  "location": "Bangkok",
  "propertyType": "hostels",
  "adults": 4,
  "rooms": 2,
  "minRating": 7,
  "maxResults": 50
}
```

### Example: top-rated resorts in a different currency

```json
{
  "location": "Cancun",
  "propertyType": "resorts",
  "minRating": 8,
  "currency": "EUR",
  "maxResults": 20
}
```

## Use cases

- **Price comparison** — pull current rates across a destination for your exact travel dates
- **Rate tracking** — run on a schedule to watch how a market's prices move over time
- **Travel planning tools** — feed search results into a trip-planning app or spreadsheet
- **Market research** — compare amenities and ratings across property types in a city
- **Deal hunting** — spot properties where `originalPrice` is well above `price`

## FAQ

**Does this need a Booking.com account?**
No. All data comes from Booking.com's public search results — no login required.

**Why use a residential proxy?**
Booking.com blocks data-center IP traffic, so keep the prefilled residential proxy for reliable results. If no properties can be loaded at all, the run ends with a failed status instead of an empty dataset.

**What property types can I filter by?**
Hotels, apartments, hostels, guesthouses, villas, resorts, or all types together. The filter is Booking.com's own, so the results match what you'd see after ticking that box on the site.

**Why do I see properties rated below my `minRating`?**
The rating filter uses Booking.com's score buckets. `minRating: 7.5` becomes Booking.com's "7+" filter, so properties rated 7.0–7.4 can appear. Filter the `rating` field afterwards if you need an exact cutoff.

**How accurate are the prices?**
Prices reflect what Booking.com shows for the dates and guest count you specify at the time of the run; they can change based on availability and demand.

**Why is `originalPrice` sometimes `0`?**
It's only filled when the card shows a struck-through price; full-price listings don't have a separate original price.

**Why are some fields empty or `0`?**
Every record has every field. When a card doesn't show something, such as an address, a photo or a review score, the field holds an empty string, `0` or `false`.

**Can I search multiple destinations in one run?**
Each run searches one `location`. Run the actor again with a different location to cover additional destinations.

**Is this affiliated with Booking.com?**
No. This is an independent, third-party actor that reads Booking.com's public search results; it isn't affiliated with or endorsed by Booking.com.
