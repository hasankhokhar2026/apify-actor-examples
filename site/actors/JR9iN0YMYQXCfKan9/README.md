# Naver Blog Post Search & Full Content Extractor

Search Naver Blog, South Korea's largest blogging platform, by keyword, pull every recent post from a specific blog, or fetch full post content and tags for a list of post URLs you already have.

## What this actor does

- Searches across all of Naver Blog by Korean or English keyword, sorted by relevance or by newest first
- Fetches recent posts published by a specific blog, given its blog ID
- Fetches the full text and tags for a list of specific post URLs
- Resolves each post's canonical URL and the blog ID it belongs to
- Omits any field that has no value for a given post rather than returning a null or empty placeholder

## Output per post

| Field | Description |
|---|---|
| `title` | Post title, HTML stripped |
| `summary` | Short description or excerpt, HTML stripped |
| `authorName` | Blog author's display name |
| `blogName` | Name of the blog |
| `blogId` | Blog's user identifier, e.g. "travel_lover" |
| `blogUrl` | URL of the blog's main page |
| `postUrl` | Canonical URL of the post |
| `publishDate` | Publish date, in `YYYY-MM-DD` format |
| `content` | Full post text, HTML stripped and capped at 2000 characters — only present in `postDetails` mode |
| `tags` | Hashtags or categories attached to the post, when available — only present in `postDetails` mode |
| `recordType` | Always `"blogPost"` |
| `scrapedAt` | UTC timestamp when the record was scraped |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string (required) | search | search (keyword search), blogPosts (posts from one blog), or postDetails (full content by URL list) |
| `query` | string | travel Korea | Keyword or phrase to search across Naver Blog — used in `search` mode |
| `blogId` | string | – | Naver blog user ID, e.g. "hello_world123" from blog.naver.com/hello_world123 — required for `blogPosts` mode |
| `postUrls` | array of strings | `[]` | Naver blog post URLs to fetch in full — used in `postDetails` mode |
| `sortBy` | string | sim | Sort order for search results: sim (relevance) or date (newest first) |
| `maxItems` | integer | 20 | Maximum number of records to return (1-1000) |

### Example: keyword search in Korean, newest first

```json
{
  "mode": "search",
  "query": "제주도 여행",
  "sortBy": "date",
  "maxItems": 50
}
```

### Example: recent posts from one blog

```json
{
  "mode": "blogPosts",
  "blogId": "korea_food_lover",
  "maxItems": 30
}
```

### Example: full content for specific posts

```json
{
  "mode": "postDetails",
  "postUrls": [
    "https://blog.naver.com/myuser/220000000001",
    "https://m.blog.naver.com/myuser/220000000002"
  ]
}
```

## Use cases

- **Consumer research** — read how Korean bloggers discuss a product, brand or place
- **Influencer discovery** — find active blogs writing about a specific niche, such as K-beauty or travel
- **Brand monitoring** — track mentions of a company or competitor across the Korean blogosphere
- **Content and trend tracking** — watch how post volume on a topic changes using `publishDate`
- **Local guides research** — collect first-hand Korean restaurant, travel and lifestyle write-ups

## FAQ

**Do I need a Naver account or API key?**
No. The actor reads Naver Blog's public search and blog pages; no login or key is required.

**Can I search using Korean text?**
Yes — both Korean and English queries work in `query`.

**What is a blog ID and how do I find one?**
It's the segment right after `blog.naver.com/` in a blog's URL. For `https://blog.naver.com/korea_food_lover`, the blog ID is `korea_food_lover`.

**What's the difference between `sim` and `date` sort?**
`sim` ranks results by Naver's own relevance scoring; `date` returns the newest posts first, useful when you want the latest content rather than the best match.

**Why do only some records have `content` and `tags`?**
Those two fields come from a post's own page and are only populated in `postDetails` mode; `search` and `blogPosts` results carry a summary instead of the full text.

**What happens if a blog or post is private or deleted?**
That entry is simply skipped and the actor moves on to the next one, rather than failing the whole run.

**Is this affiliated with Naver?**
No. This actor reads Naver's public blog pages and is not affiliated with, endorsed by, or sponsored by Naver Corporation.
