# Chrome Web Store Extension Manifest & Permissions Scraper

The Chrome Web Store doesn't offer a bulk export of its listings, so comparing extensions at scale usually means opening each page by hand. This actor looks up Chrome Web Store extensions by direct URL, category page, search query, or top-charts ranking, and returns every listing as a structured record — ratings, install count, manifest permissions, supported locales and related extensions included.

## What this actor does

- Fetches specific extensions directly from their Chrome Web Store URLs or IDs
- Walks a category page to collect every extension listed under it
- Searches the Chrome Web Store by free-text keyword
- Pulls the top-charts ranking for a category, or the global top list when no category is set
- Filters results by minimum rating, minimum install count, verified-developer status, and a developer-name substring
- Empty fields are omitted from records — a field only appears when the Chrome Web Store actually publishes that data for the extension

## Output per extension

- `extension_id`, `name`, `url` — identifier, name, and detail page link
- `version`, `manifest_version` — current version string and manifest schema version
- `rating`, `rating_count`, `install_count`
- `category`, `category_group`
- `short_description`, `long_description`
- `developer`, `developer_email`, `verified_developer` — developer identity and whether they hold Chrome's D-U-N-S-verified business badge
- `featured` — `true` when the Chrome Web Store "Featured" badge is shown
- `website_url` — developer's homepage, when listed
- `permissions`, `host_permissions` — manifest permission arrays
- `supported_languages`, `supported_locales` — display names and locale codes the extension supports
- `icon_url`, `cover_url`, `screenshots` — listing images
- `bug_tracker_url`, `privacy_policy_url`
- `package_size`, `min_chrome_version`
- `last_updated_at` — ISO-8601 UTC timestamp of the extension's last update
- `related_extensions` — array of `{id, name, icon}` for similar extensions shown on the listing
- `relatedExtensionIds` — flat list of related extension IDs, capped at 10
- `recordType` — always `extension`
- `scrapedAt` — ISO-8601 UTC timestamp when the record was collected

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `urls` | `urls` (direct lookup), `category` (walk a category page), `search` (search query), or `topCharts` (popular extensions) |
| `extensionUrls` | array | `["https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh"]` | Direct extension URLs or IDs, used in `urls` mode |
| `categoryUrls` | array | `[]` | Chrome Web Store category page URLs, used in `category` mode |
| `searchQuery` | string | `ad blocker` | Free-text search term, used in `search` mode |
| `topChartsCategory` | string | `productivity/tools` | Category slug for `topCharts` mode (e.g. `productivity/developer_tools`, `make_chrome_yours/themes`); leave empty for the global top list |
| `maxItems` | integer | `50` | Maximum number of extensions to return (1–5000) |
| `minRating` | number | – | Drop extensions with an average rating below this value (0.0–5.0) |
| `minInstalls` | integer | – | Drop extensions with fewer installs than this |
| `verifiedOnly` | boolean | `false` | Only return extensions whose developer has the verified badge |
| `developerNameContains` | string | – | Only return extensions whose developer name contains this substring (case-insensitive) |

### Example: look up a specific extension

```json
{
  "mode": "urls",
  "extensionUrls": [
    "https://chromewebstore.google.com/detail/ublock-origin-lite/ddkjiahejlhfcafbddmgiahcphecmpfh"
  ],
  "maxItems": 1
}
```

### Example: top developer-tools extensions with 1M+ installs

```json
{
  "mode": "topCharts",
  "topChartsCategory": "productivity/developer_tools",
  "minInstalls": 1000000,
  "maxItems": 50
}
```

### Example: search with a rating floor

```json
{
  "mode": "search",
  "searchQuery": "password manager",
  "minRating": 4.5,
  "maxItems": 40
}
```

## Use cases

- **Competitive analysis** — pull every extension in a category to study install and rating distribution
- **Version tracking** — monitor a competitor's `version` and `manifest_version` for changes over time
- **Permissions auditing** — scan extensions whose `host_permissions` include `<all_urls>` for a security review
- **Developer outreach** — filter by `developerNameContains` to build a contact list of extension makers
- **Install-leader research** — set a high `minInstalls` to surface only the most widely adopted extensions in a niche

## FAQ

**Does this need a login or cookies?** No — the Chrome Web Store is public, and no login or API key is required.

**What happens if an extension ID isn't found?** It's skipped and the run finishes cleanly; if nothing at all was found, the run's status message explains why.

**What if my filters reject every result?** The run finishes without fabricating rows and sets a status message so you know to loosen the filters.

**How do I search by exact description text?** Use `mode: "search"` with that text as `searchQuery` — the Chrome Web Store's own search ranks results by relevance.

**What value does `topChartsCategory` expect?** The exact schema slug, not a human label — for example `productivity/tools`, `productivity/communication`, or `make_chrome_yours/themes`.

**Why is `related_extensions` sometimes empty?** Not every listing shows a "similar extensions" carousel; when the Chrome Web Store doesn't show one, the field is omitted.

**Is this affiliated with Google or the Chrome Web Store?** No. This is an independent, third-party actor that reads the Chrome Web Store's publicly available listing pages; it is not operated by or affiliated with Google.
