# GitHub Repository Metadata & README Extractor

Pull one clean, flat row per public GitHub repository: identity and owner, stars, forks, the real watcher count, topics, license, language byte counts, README text, and optional releases, contributors, and 52 weeks of commit activity. Find repositories with a GitHub search expression, your own URL list, a user/organisation listing, or a topic. No token, cookie, or proxy setup is required.

## What this actor does

- **Four discovery modes** — search by query, fetch an explicit list of URLs or `owner/repo` slugs, list every repository of a user or organisation, or browse a topic.
- **Search qualifiers become form fields** — language, license, minimum stars/forks, created/pushed dates, `in:` scope, fork/archive toggles, sort key, and sort direction. You can also paste any native GitHub qualifier into the query itself.
- **Complete repository metadata** — every reliable field from GitHub's repository payload, including visibility, clone/git/ssh URLs, feature flags, topics count, license identifiers, and the real subscriber (watcher) count.
- **README text** — fetched from GitHub's raw content host first, then the API when the file uses another name, decoded as UTF-8, and capped at 500 KB.
- **Optional enrichment** — releases, ranked contributors, 52-week commit activity, and the latest commit, each independently switchable.
- **Rate-limit aware** — reads GitHub's headers, reports the remaining budget in the run status, and keeps the base records if the anonymous core budget runs out mid-run.
- **HTML fallback** — in direct mode, if the core API budget is exhausted, repository counters are recovered from the public repository page so the run still returns real rows.

## Output per repository

- `sourceUrl`, `htmlUrl`, `recordType`, `scrapedAt` — canonical page URL and provenance
- `id`, `nodeId`, `name`, `fullName` — identity
- `owner` — `login`, `id`, `avatarUrl`, `htmlUrl`, `type`
- `description`, `homepage`, `primaryLanguage`, `visibility`, `defaultBranch`
- `stars`, `forks`, `watchersCount`, `watchers` (real watcher count, when known), `subscribersCount`, `networkCount`, `openIssues`, `size`
- `topics[]`, `topicsCount`
- `license` — `spdxId`, `name`, `url`, `key`
- `createdAt`, `updatedAt`, `pushedAt`
- `isFork`, `isArchived`, `isDisabled`, `isTemplate`, `isPrivate`
- `hasIssues`, `hasProjects`, `hasDownloads`, `hasWiki`, `hasPages`, `hasDiscussions`, `allowForking`, `webCommitSignoffRequired`
- `cloneUrl`, `sshUrl`, `gitUrl`, `svnUrl`, `mirrorUrl`
- `readme` — `name`, `path`, `content`, `size`, `htmlUrl`, `downloadUrl`
- `languages{}` — byte count per language, plus `languageCount`
- `latestRelease`, `releases[]` — tag, name, draft/prerelease flags, dates, asset count
- `contributors[]` — login, id, type, contributions, profile URL; plus `contributorCount` and `hasMoreContributors`
- `commitActivity[]`, `commitActivityTotal`, `activeWeeks`, `latestCommit` — 52-week history and the newest default-branch commit
- `searchScore` — GitHub's relevance score, search mode only

Empty fields are omitted at every depth; a field a repository genuinely lacks is never returned as `null`. A repository that cannot be fetched produces an error row with `type: "github_repo_intelligence_error"`, a `reason` (`not_found`, `invalid_url`, `fetch_failed`, `rate_limit`), a `message`, and the identifier that failed, so one bad URL does not stop the batch.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `"search"` | `search`, `direct`, `owner`, or `topic` |
| `searchQuery` | string | `""` | GitHub search expression (mode=search); optional keyword filter in owner/topic mode |
| `repositoryUrls` | array | `[]` | Repository URLs or `owner/repo` slugs (mode=direct) |
| `owner` | string | `""` | User or organisation to list (mode=owner) |
| `topic` | string | `""` | Topic tag to browse (mode=topic) |
| `sortBy` | string | `"stars"` | `stars`, `forks`, `updated`, or `help-wanted-issues` |
| `sortOrder` | string | `"desc"` | `desc` or `asc` |
| `language` | string | `""` | Common language dropdown; empty means any |
| `languageCustom` | string | `""` | Any other GitHub language name; overrides the dropdown |
| `license` | string | `""` | License dropdown; empty means any |
| `searchIn` | string | `""` | Where the free text matches: name/description/readme/topics |
| `minStars` | integer | `0` | Minimum star count; 0 means no filter |
| `minForks` | integer | `0` | Minimum fork count; 0 means no filter |
| `createdAfter` | string | `""` | Only repositories created on/after `YYYY-MM-DD` |
| `pushedAfter` | string | `""` | Only repositories pushed on/after `YYYY-MM-DD` |
| `includeForks` | boolean | `false` | Include forks in search/owner/topic results |
| `includeArchived` | boolean | `true` | Keep archived repositories in the results |
| `maxResults` | integer | `30` | Hard cap on repositories returned (1–1,000) |
| `includeReadme` | boolean | `true` | Include the decoded README |
| `includeTopics` | boolean | `true` | Include topic tags |
| `includeLanguages` | boolean | `true` | Include language byte counts |
| `includeRepoDetails` | boolean | `false` | Add real watcher/network counts in search, owner, and topic modes |
| `includeReleases` | boolean | `false` | Include the newest releases |
| `releasesLimit` | integer | `10` | Releases kept per repository (1–100) |
| `includeContributors` | boolean | `false` | Include the ranked contributor list |
| `contributorsLimit` | integer | `30` | Contributors kept per repository (1–500) |
| `includeActivity` | boolean | `false` | Include 52-week commit activity and the latest commit |
| `githubToken` | string | `""` | Optional personal access token; only raises limits |

The daily test prefill is `mode=search`, `searchQuery="stars:>10000 language:python"`, `repositoryUrls=["https://github.com/apify/crawlee"]`, `maxResults=30`; it uses no token and returns 30 rows.

### Example: search for maintained Rust projects

```json
{
  "mode": "search",
  "searchQuery": "language:rust stars:>5000",
  "pushedAfter": "2025-01-01",
  "sortBy": "stars",
  "maxResults": 100
}
```

### Example: fetch a known list

```json
{
  "mode": "direct",
  "repositoryUrls": [
    "https://github.com/apify/crawlee",
    "pallets/flask",
    "git@github.com:psf/requests.git"
  ],
  "includeReleases": true,
  "includeContributors": true,
  "includeActivity": true
}
```

### Example: every repository of an organisation

```json
{
  "mode": "owner",
  "owner": "apify",
  "language": "python",
  "minStars": 100,
  "sortBy": "updated"
}
```

### Example: browse a topic

```json
{
  "mode": "topic",
  "topic": "llm",
  "includeForks": false,
  "maxResults": 200
}
```

## Use cases

- **Dependency due diligence** — check license, archived status, last push, latest release, contributor depth, and commit activity before adopting a library.
- **Ecosystem mapping** — enumerate `topic:llm`, `language:rust`, or an organisation's repository portfolio.
- **Leaderboards and dashboards** — rank a repository set by stars, forks, or recent activity with stable numeric fields.
- **LLM and RAG pipelines** — pair structured metadata with the full README text for retrieval or code analysis.
- **Release and community tracking** — follow release cadence and contributor counts over time.

## Rate limits and behaviour

GitHub allows about **60 core requests per hour** and **10 search requests per minute** without a token. This actor:

- tracks `X-RateLimit-Remaining`, `X-RateLimit-Limit`, and the reset time on every response and reports them in the run status;
- fetches READMEs from GitHub's raw content host, which does not consume the core budget;
- keeps emitting base records and skips only optional enrichment when the core budget is exhausted;
- retries `429` and `5xx` responses with backoff, handles secondary rate limits, and retries a `202` statistics response once;
- treats a rejected optional token as a soft failure and continues anonymously.

A personal access token raises the limits to 5,000 core requests per hour and 30 search requests per minute. It is optional and never used by the daily test.

## Limitations

- **Search is capped at 1,000 results per query** by GitHub. Split a large universe into `stars:` ranges (for example `stars:10000..50000`, then `stars:5000..9999`) and run once per range.
- **The contributor endpoint is capped at 500 entries** by GitHub. `hasMoreContributors` is set when GitHub's `Link` header shows more pages.
- **Commit activity can take a moment to compute.** If GitHub still returns `202` after one retry, the field is omitted for that repository instead of invented.
- **Private repositories** require a token with access to them. The actor never asks for cookies or a login.
- **Sorting by "Recently updated" follows GitHub's own ordering, which is approximate.** Re-sort on the `updatedAt` field if you need a strict order. Rows are pushed as enrichment finishes, so use `index` (the search rank) to restore the source order.
- **`license.url` points at GitHub's license API** (`api.github.com/licenses/<id>`). Like any API URL it returns 403 while the anonymous hourly quota is exhausted; the dataset itself is unaffected.
- **No issues, pull requests, discussions, or trending data.** This actor focuses on repository metadata and README content.

## FAQ

**Do I need a GitHub token?** No. Small runs work anonymously. Supply a token only for larger batches or private repositories.

**Why is `watchers` missing on some rows?** GitHub aliases `watchers_count` to stars in search payloads, so that value is published as `watchersCount` (not as a misleading watcher count). `watchers` and `subscribersCount` are the real watcher count, filled in direct mode and when `includeRepoDetails` is on.

**Do I need a proxy?** No. GitHub limits requests by IP and token, not by blocking this actor.

**Can I use my own search qualifiers?** Yes. The query field accepts the full GitHub repository-search grammar; the form filters are appended to it.

**What happens if a repository is missing?** The actor emits an error row for that repository and continues with the rest.

**Is this affiliated with GitHub?** No. It reads GitHub's public REST API and public repository pages.

## Data source

GitHub's public REST API (`api.github.com`), its raw content host (`raw.githubusercontent.com`), and public repository pages on `github.com`. No authentication is required for public data.
