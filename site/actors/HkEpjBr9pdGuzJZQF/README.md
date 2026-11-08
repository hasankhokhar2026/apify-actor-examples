# LinkedIn Learning Course & Learning Path Finder

Search the [LinkedIn Learning](https://www.linkedin.com/learning/) catalog by keyword and get back structured data for the matching courses, learning paths, or videos — no LinkedIn login or Learning subscription needed.

## What this actor does

- Searches LinkedIn Learning's public catalog by keyword, with an optional topic to narrow it further
- Visits each matching course/path/video page and extracts its published schema.org course data
- Filters by difficulty level and asset type (course, learning path, video)
- Returns instructor name/profile, duration, topics and the skills it teaches, when LinkedIn Learning lists them
- Empty fields are omitted from records rather than returned as null

## Output per course

- `title`, `description` — course name and overview text
- `courseUrl` — direct LinkedIn Learning URL
- `courseId` — numeric ID parsed from the URL, when the slug ends in one
- `thumbnailUrl` — cover image
- `language` — content language reported by the page
- `difficultyLevel` — `BEGINNER`, `INTERMEDIATE`, or `ADVANCED`
- `durationSeconds`, `durationFormatted` (e.g. `"2h 15m"`), `duration` (minutes, rounded)
- `instructorName`, `instructorUrl`, `instructor` — object with `name`, `profileUrl`, `bio` when available
- `assetType` — `COURSE`, `LEARNING_PATH`, or `VIDEO`
- `releaseDate` — publish date reported by LinkedIn Learning
- `popularityScore`, `learnerCount` — aggregate rating value and rating/review count, when LinkedIn Learning publishes them
- `topics` — subject areas the course is filed under
- `skillsTaught` — specific skills the course teaches
- `certificate` — `true` when a completion certificate is awarded
- `scrapedAt` — ISO timestamp of when the record was collected

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `searchQuery` | string | `Python machine learning` | Keyword or skill to search for (required) |
| `maxResults` | integer | `50` | Maximum courses to return (1–500) |
| `difficultyLevel` | string | – (all levels) | `BEGINNER`, `INTERMEDIATE`, or `ADVANCED` |
| `assetType` | string | `COURSE` | `COURSE`, `LEARNING_PATH`, or `VIDEO` |
| `sortBy` | string | `RELEVANCE` | `RELEVANCE` or `RECENCY` — accepted but not currently applied; results come back in the order LinkedIn Learning's search page returns them |
| `topic` | string | – | Extra keyword appended to `searchQuery` to narrow results, e.g. "Cloud Computing" |
| `language` | string | `en` | Content language / search locale: `en`, `es`, `fr`, `de`, `pt` |
| `proxyConfiguration` | object | `{"useApifyProxy": false}` | Optional Apify proxy — not required for most searches |

### Example: beginner Python courses

```json
{
  "searchQuery": "Python machine learning",
  "difficultyLevel": "BEGINNER",
  "assetType": "COURSE",
  "maxResults": 50
}
```

### Example: learning paths on a topic

```json
{
  "searchQuery": "cloud computing",
  "topic": "AWS",
  "assetType": "LEARNING_PATH",
  "maxResults": 20
}
```

### Example: videos in Spanish

```json
{
  "searchQuery": "diseño gráfico",
  "assetType": "VIDEO",
  "language": "es"
}
```

## Use cases

- **Curriculum planning** — survey what courses and learning paths already exist for a skill before building internal training
- **Skill-gap research** — pull the topics and skills taught across a batch of search queries to map a domain
- **L&D catalog building** — compile course metadata (duration, difficulty, instructor) into an internal learning catalog
- **Instructor research** — find which instructors are teaching in a given subject area
- **Competitive content tracking** — monitor how LinkedIn Learning's catalog for a topic changes over time

## FAQ

**Do I need a LinkedIn account or Learning subscription?** No. The search page and individual course pages used by this actor are publicly accessible without logging in.

**Why do some records have fewer fields than others?** Course pages don't all publish the same schema.org fields — things like `popularityScore`, `learnerCount`, `releaseDate` and `certificate` depend on what LinkedIn Learning itself has published for that particular course.

**Why is `courseId` sometimes missing?** It's parsed from a numeric suffix in the course's URL slug; some slugs don't end in one, so there's nothing to extract.

**What's the difference between `topics` and `skillsTaught`?** `topics` are the broader subject areas a course is filed under; `skillsTaught` are the specific skills LinkedIn Learning lists as learning outcomes.

**How is `assetType` different from a learning path search?** Setting `assetType` to `LEARNING_PATH` searches LinkedIn's curated multi-course paths instead of individual courses or standalone videos; the rest of the fields are extracted the same way.

**Does `language` translate the results?** No — it selects the LinkedIn Learning locale used for the search and reflects whatever language the matching content was actually published in.

**Why did I get fewer results than `maxResults`?** LinkedIn Learning's catalog for a given keyword and asset type may simply have fewer matches than the limit you set.

**Is this affiliated with LinkedIn?** No. This actor reads LinkedIn Learning's public catalog pages; it is not operated by or affiliated with LinkedIn.
