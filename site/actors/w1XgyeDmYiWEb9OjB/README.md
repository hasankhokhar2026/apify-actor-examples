# Coursera Courses and Specializations Lookup

Coursera's public catalog API exposes two kinds of listings: standalone courses and multi-course specializations. This actor pages through either catalog and returns each entry as a flat record, so you can build a course dataset without opening Coursera's site yourself.

## What this actor does

- Browses either the course catalog or the specialization catalog, chosen with the `mode` input
- Pages through the catalog automatically, stopping once `maxItems` is reached or the catalog runs out of entries
- Narrows results to entries whose title or description matches a keyword
- Builds a direct `coursera.org/learn/<slug>` URL for every entry that has a slug
- Omits any field Coursera's catalog doesn't publish for a given entry instead of returning an empty value

## Output per entry

- `courseId` — Coursera's internal numeric ID for the course or specialization
- `title` — catalog name
- `slug` — URL slug used to build `courseUrl`
- `description` — catalog description text, truncated to 500 characters
- `workload` — estimated time commitment as published by Coursera (e.g. `"4-6 hours/week"`)
- `level` — difficulty level (e.g. `Beginner`, `Intermediate`, `Advanced`)
- `courseType` — Coursera's internal course-type code
- `courseUrl` — direct link to the course or specialization page on coursera.org
- `recordType` — always `course`
- `scrapedAt` — ISO 8601 timestamp of when the record was fetched

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `courses` | `courses` to browse the course catalog, or `specializations` to browse the specialization catalog |
| `searchQuery` | string | – | Keyword to narrow results by title or description |
| `maxItems` | integer | `20` | Maximum number of entries to return (1–200) |

### Example: browse courses matching a keyword

```json
{
  "mode": "courses",
  "searchQuery": "machine learning",
  "maxItems": 20
}
```

### Example: browse specializations

```json
{
  "mode": "specializations",
  "maxItems": 15
}
```

### Example: larger pull of general courses

```json
{
  "mode": "courses",
  "maxItems": 150
}
```

## Use cases

- **EdTech research** — build a dataset of Coursera's current course and specialization offerings for comparison against other platforms
- **Content curation** — find courses on a given topic to recommend or link to from a learning resource site
- **Catalog monitoring** — track how Coursera's workload and difficulty-level labeling changes for a topic over time
- **Market analysis** — compare the depth of course vs. specialization offerings across subject areas

## FAQ

**What's the difference between `courses` and `specializations` mode?**
`courses` returns individual Coursera courses. `specializations` returns Coursera's bundled multi-course programs instead — the output fields are the same, but the catalog and the records in it are different.

**Does `searchQuery` run a real search on Coursera?**
It narrows the browsed catalog to entries whose title or description contains your keyword; it does not call a separate search endpoint, since Coursera's public catalog API only exposes browse-style access.

**Why is `description` cut off at 500 characters?**
That's the catalog's own summary length as returned by the API; the actor doesn't fetch each course's individual page for the full-length description.

**Why might a record be missing `workload` or `level`?**
Not every catalog entry has those fields populated on Coursera's side — the actor only includes a field when the catalog actually provides a value for it.

**How current is the data?**
Every run queries Coursera's public catalog live, so results reflect whatever is published at run time.

**Is this affiliated with Coursera?**
No. This is an independent tool that reads Coursera's publicly accessible catalog API and is not affiliated with or endorsed by Coursera.
