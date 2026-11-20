# Eniro.se Company Directory & Contact Finder

Eniro.se is Sweden's largest public business and phone directory. This actor turns it into a structured lead source: search one or many categories across one or many Swedish cities, scrape Eniro search/profile URLs directly, and optionally open every company's own profile page for the contact and trust details that only live there.

No login, cookie, API key or proxy setup is needed. The actor handles Eniro's bot protection itself.

## What you can do

- **Multi-term, multi-city searches.** Cross every `searchTerms` entry with every `locations` entry in one run (e.g. `rörmokare` + `elektriker` in Stockholm + Göteborg = four searches), or use the single `query` + `city` pair.
- **Nationwide or nearby.** Leave the city list empty for all of Sweden, or pass a `latitude,longitude` point to use Eniro's own nearby filter.
- **Scrape URLs.** Paste Eniro search URLs (`/rörmokare+stockholm/företag`) and/or company profile URLs (`/<name>/<id>/firma`) into `startUrls`.
- **Enrich each hit.** Turn on `fetchDetails` to add multiple phone numbers, email, full rating counts, every opening-hours group, category codes, promotional links, cover photo, free text, coordinates, images and organization number.
- **Filter for usable leads.** Keep only companies with a phone, an email, a website, a rating, a minimum rating, or exclude one-person sole traders.
- **Sort and cap.** Order by Eniro relevance, rating or name, and stop each search after a configurable number of pages.

Every output field is omitted when Eniro does not publish it. Nothing is emitted as `null`, `""` or an empty list.

## Output per company

| Field | Description |
|---|---|
| `businessId` | Eniro's internal company ID |
| `slug` | Human-readable Eniro URL slug |
| `name` | Company name |
| `businessType` | schema.org type, e.g. `Restaurant`, `HairSalon`, `Dentist` |
| `category` / `categories` | Primary category and the full category chain |
| `categoryCodes` | Eniro category codes matching `categories` |
| `street`, `postalCode`, `city` | Postal address |
| `municipality`, `province`, `region`, `urbanArea`, `district`, `country` | Administrative area fields, when Eniro publishes them |
| `phone` | Primary phone number |
| `phones` | Every published number as `{number, label?}` |
| `email` | Published company email |
| `website` | Company website |
| `organizationNumber` | Swedish organization number, `NNNNNN-NNNN` |
| `facebookUrl`, `instagramUrl`, `linkedinUrl`, `twitterUrl`, `youtubeUrl`, `tiktokUrl`, `snapchatUrl`, `whatsappUrl` | Social profiles Eniro has on file |
| `description` | Short company description |
| `freeText` | Longer promotional text, when different from `description` |
| `keywords` | Services, brands or tags attached to the listing |
| `rating` | Average rating (1-5) |
| `ratingCount` | Number of ratings behind `rating` |
| `reviewCount` | Eniro's rating count, kept for existing integrations (same value as `ratingCount`) |
| `openingHours` | Main weekly schedule as `{day, opens, closes}` entries with Swedish day names |
| `openingHoursText` | One-line summary of the main schedule |
| `openingHoursGroups` | All schedule groups (e.g. main + seasonal), each `{title, hours}` |
| `latitude`, `longitude` | Coordinates |
| `mapUrl` | Eniro map/directions link |
| `logoUrl` / `logoUrlOriginal` | Logo re-hosted for a stable public link, plus the original Eniro URL |
| `images` / `imagesOriginal` | Photo gallery re-hosted the same way |
| `coverImageUrl` / `coverImageUrlOriginal` | Cover photo, re-hosted the same way |
| `links` | Promotional links from the profile, e.g. `{label: "Meny", url: ...}` |
| `searchQuery`, `searchCity` | The term and city that produced the record |
| `sourceUrl` | Canonical Eniro company page |
| `lastUpdated` | When Eniro last changed the listing |
| `recordType` | Always `"business"` |
| `scrapedAt` | UTC timestamp of the scrape |

Search results without `fetchDetails` contain the fields Eniro puts on the result card (name, address, phone, type, and any rating/description/logo the card carries). Profile-only fields fill in when you enable enrichment or use `mode=detail` / profile URLs.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `search` | `search` (terms + cities), `detail` (profile URLs/IDs), or `urls` (a mixed list of Eniro search and profile URLs). |
| `query` | string | `pizzeria` | Single category/keyword from the curated list, or `custom` to use `customQuery`. |
| `customQuery` | string | – | Free-text category/keyword, overriding `query` when set. Use correct å/ä/ö spelling. |
| `searchTerms` | array | – | One or more categories/keywords; each is combined with every city. Overrides `query`/`customQuery`. |
| `city` | string | `Stockholm` | Single Swedish city; leave empty for nationwide. Overridden by `locations`. |
| `locations` | array | – | One or more Swedish cities; each is combined with every search term. |
| `searchCoordinates` | string | – | Optional `"lat,lon"` point for Eniro's nearby search. |
| `sortBy` | string | `relevance` | Result order: `relevance`, `rating`, or `name`. |
| `ratedOnly` | boolean | `false` | Keep only companies with at least one rating. |
| `minRating` | string | – (no minimum) | Keep only companies rated at least `1`-`5` stars. |
| `hasWebsiteOnly` | boolean | `false` | Keep only companies with a published website (requires `fetchDetails`). |
| `hasPhoneOnly` | boolean | `false` | Keep only companies with a published phone number. |
| `hasEmailOnly` | boolean | `false` | Keep only companies with a published email (requires `fetchDetails`). |
| `includeSoleTraders` | boolean | `true` | Keep person-named one-person firms; turn off for company-only lists. |
| `fetchDetails` | boolean | `false` | Open each search hit's profile page for the full field set. |
| `businessUrls` | array | – | Eniro profile URLs or numeric IDs for `mode=detail`. |
| `startUrls` | array | – | Eniro search and/or profile URLs for `mode=urls`. |
| `maxPagesPerSearch` | integer | `20` | Stop each term/city after this many 25-result pages. |
| `maxItems` | integer | `50` | Hard cap across all searches and URLs. |

### Example: one trade in one city

```json
{
  "mode": "search",
  "query": "frisör",
  "city": "Göteborg",
  "maxItems": 50
}
```

### Example: several trades and cities, enriched and filtered

```json
{
  "mode": "search",
  "searchTerms": ["rörmokare", "elektriker"],
  "locations": ["Stockholm", "Göteborg"],
  "fetchDetails": true,
  "hasEmailOnly": true,
  "minRating": "3",
  "includeSoleTraders": false,
  "maxPagesPerSearch": 5,
  "maxItems": 200
}
```

### Example: nationwide category with full profiles

```json
{
  "mode": "search",
  "customQuery": "veterinär",
  "city": "",
  "fetchDetails": true,
  "maxItems": 100
}
```

### Example: paste Eniro URLs

```json
{
  "mode": "urls",
  "startUrls": [
    "https://www.eniro.se/rörmokare+i+stockholm/företag",
    "https://www.eniro.se/pizzeria+florida+viskafors/14839034/firma"
  ],
  "maxItems": 100
}
```

### Example: direct profile lookup

```json
{
  "mode": "detail",
  "businessUrls": [
    "https://www.eniro.se/pizzeria+florida+viskafors/14839034/firma",
    "14839034"
  ]
}
```

## Use cases

- **B2B lead generation** - build contact lists for one or many trades in one or many Swedish cities.
- **Local SEO auditing** - compare a client's or competitor's categories, rating, hours and profile links.
- **Market mapping** - measure how a category is distributed across cities or nationwide.
- **CRM enrichment** - look up phone numbers, addresses, emails and organization numbers for companies you already know.
- **Franchise research** - survey existing competitors in a category before opening a new location.

## FAQ

**Where does the data come from?**
The public Eniro.se business directory.

**Why are some fields missing on search-only runs?**
Eniro puts contact and trust details on each company's profile page, not on the search card. Enable `fetchDetails` (or use profile URLs) to collect them.

**How many results can I get?**
Eniro returns 25 companies per result page. `maxPagesPerSearch` bounds each term/city, and `maxItems` caps the whole run at 1,000 records. Split very broad categories by city or search term to reach deeper than one run's cap.

**Can I search by coordinates?**
Yes. Set `searchCoordinates` to `"latitude,longitude"`; the actor passes it to Eniro's own nearby filter.

**Can I search for private persons or reverse-lookup a phone number?**
No. Eniro's person search and "who called" service are separate products and are not part of this company-directory actor.

**Are written reviews included?**
No. Eniro exposes an aggregate rating and rating count, not review text.

**Why do some companies lack an email, website or social link?**
Those fields exist only when the company published them with Eniro.

**Do I need a proxy or an Eniro API key?**
No. The actor handles Eniro's bot protection and any proxy choice automatically.

## Limitations

- Company data only; no person records and no reverse phone lookup.
- Written review text is not exposed by Eniro; only the aggregate rating and rating count are available.
- `lastUpdated` is emitted when Eniro publishes its `tracestamps.clusterWrite` change stamp. It was present on 35/35 sampled 2024-2025 profile pages and 30/36 sampled 2026 profile pages; some listings publish no stamp, so the field stays omitted for those.
- Search-card fields are limited to what Eniro renders on the card; profile-only fields require `fetchDetails` or profile URLs.
- Eniro fronts the site with a JavaScript challenge. Plain HTTP clients, including current browser TLS fingerprints, are rejected; the actor uses its browser tier automatically, so no proxy or API key is required.
- A run is capped at 1,000 records. Split very broad nationwide categories by city or term to collect more.
- The browser tier runs at 2,048 MB of memory. This is the tested configuration for Chromium under xvfb; it is not a user input.
- Eniro's directory contents and markup can change; the actor falls back from enriched server data to the page's structured data so a partial page still yields a record.
- Logos, gallery images and cover photos are re-hosted for stable public links. If a re-host fetch fails, the original URL is kept as the fallback.

## Data source

Eniro.se, Sweden's public business directory. This actor is independent and is not affiliated with, endorsed by, or sponsored by Eniro AB. Users are responsible for ensuring their use complies with Eniro's terms and applicable data-protection law.
