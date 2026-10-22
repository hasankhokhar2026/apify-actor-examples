# Google News Keyword & Full-Text Article Scraper

Search Google News for any keyword and get back real, resolved article links — not Google's redirect URLs — along with headline, source, and publish date. Turn on full-text and image extraction when a snippet isn't enough and you need the actual article body.

## What this actor does

- Searches Google News for one or more keywords in a single run and deduplicates articles that match more than one query
- Resolves each result to the publisher's real article URL instead of a Google redirect link whenever it can
- Filters results by recency, a custom date range, language, country, a specific publisher domain, or excluded words
- Can optionally fetch each article's page to pull the full body text and the main article image
- `fullText`, `imageUrl`, and `author` are always present on every record but come back `null` when the corresponding option is off or nothing was found; `publishedAt`, `snippet`, `source` and `domain` are empty strings when Google News doesn't supply them

## Output per article

- `query` — the search keyword that returned this article
- `title` — the article headline
- `url` — the publisher's actual article URL, resolved from Google News (if resolution fails, the Google News link is kept)
- `source` — the publisher name, e.g. `BBC`, `Reuters`
- `domain` — the publisher's domain, e.g. `bbc.com` (from the resolved URL, or from Google News' source link when unresolved)
- `publishedAt` — the article's publication date and time in ISO 8601, as listed by Google News
- `snippet` — the short summary Google News shows for the article
- `fullText` — the full article body text; `null` unless `extractFullText` is enabled
- `imageUrl` — the article's main image URL; `null` unless `includeImages` is enabled
- `author` — the article's byline; `null` unless `extractFullText` or `includeImages` is enabled (either one opens the article page) and the page publishes one
- `language` — the language code used for the search
- `scrapedAt` — when the actor started on that query

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `queries` | array of strings | – | Search keywords; each is searched separately and results are deduplicated across all of them. Required. |
| `maxResultsPerQuery` | integer | `20` | Maximum articles to return per query (1–100). |
| `language` | string | `en` | Language code for the search, e.g. `en`, `de`, `fr`, `es`. |
| `country` | string | `US` | Country code for regional news, e.g. `US`, `GB`, `DE`, `IN`. |
| `dateRange` | string | `any` | Recency filter: `1h`, `6h`, `1d`, `7d`, `1m`, `1y`, or `any`. Ignored when `dateFrom`/`dateTo` are set. |
| `dateFrom` | string | – | Only articles published on or after this date (`YYYY-MM-DD`); overrides `dateRange`. |
| `dateTo` | string | – | Only articles published on or before this date (`YYYY-MM-DD`); use together with `dateFrom`. |
| `siteFilter` | string | – | Restrict results to one publisher domain, e.g. `reuters.com`. |
| `excludeWords` | array of strings | – | Words or phrases added to the search as exclusions, so Google News leaves out matching articles. |
| `extractFullText` | boolean | `false` | Fetch each article's page and extract the full body text and author byline. |
| `includeImages` | boolean | `false` | Fetch each article's page and extract its main image URL (the author byline is picked up too when present). |
| `maxConcurrency` | integer | `5` | How many articles to process in parallel when `extractFullText`/`includeImages` is on (1–20). |

## Example: quick scan of today's headlines

```json
{
  "queries": ["artificial intelligence", "climate change"],
  "maxResultsPerQuery": 20,
  "dateRange": "1d"
}
```

## Example: full article text and images

```json
{
  "queries": ["renewable energy"],
  "maxResultsPerQuery": 10,
  "extractFullText": true,
  "includeImages": true
}
```

## Example: one publisher, custom date range, with exclusions

```json
{
  "queries": ["elections"],
  "siteFilter": "bbc.com",
  "dateFrom": "2026-01-01",
  "dateTo": "2026-02-28",
  "excludeWords": ["opinion", "editorial"],
  "maxResultsPerQuery": 50
}
```

## Example: non-English regional news

```json
{
  "queries": ["Nachrichten"],
  "language": "de",
  "country": "DE",
  "maxResultsPerQuery": 10
}
```

## Use cases

- **Media monitoring** — track coverage of your brand, competitors, or industry across the publishers Google News indexes
- **Market research** — pull news mentioning a company, product, or market trend for analysis
- **Newsletter curation** — build a themed news digest from one or more topics
- **Sentiment analysis** — feed full article text into an NLP pipeline to gauge coverage tone on a topic
- **Academic or policy research** — gather a dated, filtered news dataset for a study
- **Dataset building** — collect full article text at scale for downstream text-analysis work

## FAQ

**Does this return the real article link or a Google redirect?**
The real, resolved publisher URL, not the `news.google.com` redirect link Google News shows in its own results. In the rare case a link can't be resolved, the Google News link is returned in `url` instead.

**Why are `fullText`, `imageUrl`, or `author` null in my results?**
All three fields are always present on the record, but they only get a real value when you turn on `extractFullText` and/or `includeImages` and the article page actually has that data; otherwise they come back as `null`. Pages that fail to load also leave them `null`. By default (both options off) the actor returns headlines and snippets only, which is faster.

**Can full-text extraction read paywalled articles?**
No — sites behind a paywall (e.g. subscription-only news sites) won't return usable full text, since the actor only reads what's publicly visible on the page.

**Can I search multiple keywords at once?**
Yes, add as many entries as you like to `queries`; results across all of them are deduplicated by their Google News link, so an article found by an earlier query is not repeated for a later one.

**What's the difference between `dateRange` and `dateFrom`/`dateTo`?**
`dateRange` is a quick recency filter (e.g. "past week"). Setting `dateFrom` and/or `dateTo` gives you a custom date window instead and makes the actor ignore `dateRange`. Both are passed to Google News as search conditions, so the dates Google applies are what count.

**Can I restrict results to one news source?**
Yes, set `siteFilter` to that publisher's domain, e.g. `reuters.com`.

**How many articles can I get per query?**
Up to `maxResultsPerQuery`, capped at 100, limited by how many matching articles Google News returns for that query and filter combination in a single result list (there is no paging beyond it).

**Is this affiliated with Google?**
No. This is an independent, third-party actor that reads Google News' publicly available search results; it is not affiliated with or endorsed by Google.
