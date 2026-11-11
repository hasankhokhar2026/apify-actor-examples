# Quora Space Activity & Content Change Monitor

This actor watches public Quora Spaces (topic communities) and individual Quora pages — questions, answers, profiles, topics, or posts — for content-level changes between runs. Point it at one or more Space URLs for the richer community-level view (metadata, feed, contributors), or at any other public Quora URL for a lighter title/content change check. Run it on a schedule and it only reports what actually changed.

## What this actor does

- Monitors a Quora Space's metadata (name, description, follower/member/post counts, rules, topics) and reports whether it changed since the last run.
- Monitors a Space's visible feed (posts, questions, answers) and, optionally, the people with an explicitly labeled role in that Space (owner, moderator, admin, contributor).
- Monitors any other public Quora URL — a question, answer, profile, topic, or standalone post — for title/content changes via `urls`.
- Discovers additional Space and entity links from native Quora search queries, within a bounded cap.
- Reports an explicit status row (login-required, Cloudflare-blocked, removed, etc.) instead of guessing when a page can't be read, and every row only contains the fields this actor actually observed — nothing is filled in with a placeholder.

## Output fields

Every run emits rows that share a common set of identity/status fields, plus extra fields depending on what kind of row it is (Space metadata, feed item, contributor, discovery result, generic URL event, or run/status row).

### Every row

| Field | Description |
|-------|-------------|
| `content_type` | What kind of row this is, e.g. `space`, `space_feed_item`, `space_contributor`, `space_discovery`, `monitor_event`, `status` |
| `record_id` | Stable identifier for this row |
| `url` / `source_url` | The row's own URL and the URL it was observed from |
| `final_url` | URL after following any redirects |
| `title` | Unified human-readable label for the row (Space name, feed item title, contributor name, etc.) |
| `date_precision` | `exact` when a machine-readable date was found, `relative` when only a label like "3h ago" was available |
| `access_state` | What access state was observed, e.g. `public`, `login_required`, `cloudflare`, `unavailable`, `network_error` |
| `http_status` | HTTP status code observed |
| `error` | Error description, when the fetch failed |
| `scrape_timestamp` | When this row was captured |
| `matched_input` / `matched_input_kind` | The exact input URL or search query that produced this row |
| `source_observations` / `source_observation_count` | Bounded history of exact URLs/queries retained for this Space |
| `source_query` / `source_kind` | The query or source type that produced this row, when applicable |
| `requested_depth` / `observed_depth` | The traversal depth you asked for vs. what was actually achieved |
| `detail_expansion_state` | Whether detail-level traversal completed, was bounded, blocked, or not applicable |
| `localized_numeric_fields` | Parsed numeric values for any `*_count`/`*_count_text` field present on the row |
| `normalized_date_fields` | UTC-normalized companions for every date field present on the row |
| `date_interpretations` | Bounded interval interpretation of a relative date label, when present |
| `field_sources` / `fields_present` | Evidence of where each field's value came from and which fields are present on this row |
| `parser_strategy` / `parser_version` | Which extraction path and version produced this row |
| `output_projection` | `full` or `selected`, depending on whether `outputFields` filtered this row |
| `max_items_per_source` / `source_cap` / `source_items_observed` / `source_items_emitted` / `source_cap_reached` | The configured per-source cap and how it applied to this row's source |

### Space metadata row

| Field | Description |
|-------|-------------|
| `space_url` / `space_id` / `canonical_url` | The Space's URL, ID and canonical link |
| `name` / `description` | Space name and description |
| `image_url` | Space image URL |
| `created_at` / `updated_at` | Space creation/update timestamps, when shown |
| `space_visibility` / `space_type` | `public`/`private`/`restricted`/`unknown`, and the Space type |
| `follower_count` / `follower_count_value` | Follower count, as shown and as a parsed number |
| `member_count` / `member_count_value` | Member count, as shown and as a parsed number |
| `post_count` / `post_count_value` | Post count, as shown and as a parsed number |
| `contributor_count` / `contributor_count_value` | Contributor count, as shown and as a parsed number |
| `owner_name` / `owner_url` | Space owner's name and profile link |
| `website_url` | Linked external website, when shown |
| `moderator_records` | Moderators found in an explicitly labeled moderator region |
| `topics` / `topic_links` | Topic names, and topic name/URL pairs |
| `rules` | Space rules/guidelines text, when visible |

### Space settings (opt-in via `includeSettings`)

| Field | Description |
|-------|-------------|
| `space_settings_state` | Whether the settings probe was skipped, found nothing, or observed settings |
| `space_allowed_content_types` | Explicitly named content types the Space allows, e.g. posts, questions |
| `space_comment_permission` | Who can comment, when explicitly stated |
| `space_submission_policy` | Who can submit content, when explicitly stated |
| `space_content_requirements` | Raw lines describing content/link/text requirements |
| `space_distribution_state` | Distribution scope, when explicitly stated |
| `space_contributor_request_state` | Whether contributor requests are enabled or disabled |
| `space_settings_text` | Raw text from the labeled settings region |

### Feed item row

| Field | Description |
|-------|-------------|
| `feed_url` / `feed_type` / `feed_title` / `feed_text` | The feed item's link, type, title and visible text |
| `feed_author_name` / `feed_author_url` / `feed_author_image_url` / `feed_author_id` | The feed item author's identity |
| `feed_author_credentials` / `author_credentials` | Credential or tagline text shown next to the author, when present |
| `feed_author_is_verified` / `feed_author_is_anonymous` | Positive-only markers when an explicit verified badge or Anonymous label is visible |
| `feed_created_at` / `feed_timestamp` | The feed item's date, machine-readable or as a relative label |
| `feed_age_days` / `feed_age_state` | Age in days, computed only when a machine-readable date was available |
| `media_urls` / `image_urls` / `video_urls` | Media attached to the feed item, when `includeMedia` is on |
| `outbound_links` | Outbound links found on the feed card, when `includeOutboundLinks` is on |
| `feed_tab` / `observed_feed_tab` | The tab you requested and whether it was actually selected |
| `space_feed_limit_reached` | Whether `maxFeedItems` was reached |

### Question expansion (when `maxFeedQuestionExpansions` > 0)

| Field | Description |
|-------|-------------|
| `question_id` | The expanded question's ID |
| `question_answer_count` / `question_answer_count_value` | Answer count, as shown and as a parsed number |
| `question_view_count` / `question_view_count_value` | View count, as shown and as a parsed number |
| `question_details` | Question description/details text |
| `question_created_at` / `question_updated_at` | Question timestamps |

### Contributor row (opt-in via `includeContributors`)

| Field | Description |
|-------|-------------|
| `contributor_url` / `contributor_name` / `contributor_image_url` / `contributor_id` | The contributor's identity |
| `contributor_role` / `role_label` / `role_source` | Their role and where that role label was found |

### Discovery row (from `searchQueries`)

| Field | Description |
|-------|-------------|
| `discovered_spaces` | Space links found by the query |
| `discovered_entities` | Question/answer/profile/topic/post links found by the query |
| `discovery_cap_reached` | Whether `maxDiscoveryResults` was reached |
| `observed_tabs` | Tabs actually seen on the page |

### Change tracking (when `stateStoreId` is set)

| Field | Description |
|-------|-------------|
| `event_type` | `new`, `unchanged`, or `changed` |
| `content_hash` / `previous_content_hash` | The row's current and prior content fingerprint |
| `previous_snapshot_available` | Whether a prior snapshot existed to compare against |
| `change_evidence` | Details of the comparison that produced `event_type` |
| `field_change_summary` | Names of fields that changed, when `diffMode` includes a summary |
| `previous_field_values` / `current_field_values` | Before/after values of changed fields, when `diffMode` is `field_values` |

### Run diagnostics

| Field | Description |
|-------|-------------|
| `scrape_duration_ms` / `run_duration_ms` | Time spent on this row and on the overall run |
| `navigation_attempts` / `navigation_retries` / `navigation_retry_delays_seconds` | Navigation attempt and retry accounting |
| `proxy_used` / `proxy_resolution_state` | Whether proxy was used and how it resolved |
| `session_cookie_count` / `session_input_state` / `session_cookie_expiry_state` | Session/cookie accounting |
| `request_delay_seconds` / `browser_locale` / `requested_result_types` | Request pacing and locale settings applied |
| `records_emitted` / `source_pages_attempted` | How many rows and source pages this run covered |
| `content_type_counts` / `access_state_counts` | Row counts broken down by type and access state |
| `input_accounting` | How each input item was resolved |
| `state_entries_pruned` / `state_retention_days` / `diff_mode` | State-store pruning and diff settings applied |
| `manifest_version` | Version of this actor's output contract |
| `space_scroll_attempts` / `space_scroll_state` | Scroll traversal accounting for the feed |
| `space_load_more_attempts` / `space_load_more_clicks` / `space_load_more_state` | Load-more button traversal accounting |
| `space_continuation_state` | Combined continuation-traversal evidence |
| `contributor_limit_reached` | Whether `maxContributors` was reached |

## Projection, depth and session notes

- **Compact rows.** `outputFields` keeps only the fields you list; an empty list keeps the full row. Nested projection is supported with bounded dotted paths such as `topic_links.topic_name` or `discovered_entities.name`, and child identity/URL fields inside those collections are kept. Change evidence, state-store diagnostics, identity, access and source fields are never removed, and `output_projection` reports `full` or `selected`. `includeFieldEvidence` decides whether `field_sources`/`fields_present` stay on each row.
- **Depth.** `scrapeDepth: "overview"` captures Space metadata and status only, with no feed, contributor, scroll or load-more work; `detail` (default) runs the capped monitoring traversal. `requested_depth`, `observed_depth` and `detail_expansion_state` are on every row, and `bounded` means a scroll or load-more cap was reached, not that the Space's whole history was read.
- **Author credentials.** `feed_author_credentials` (and the shared `author_credentials`) carry a credential or tagline only when it is printed inside the feed card's own author block; ambiguous text is left out and it never verifies expertise.
- **Session input.** Use structured `cookies` or the secret `cookieString` header (`name=value; name2=value2`). Structured cookies win on duplicate names, malformed pairs are ignored, and the raw header is never emitted or logged. This is an access input for content your account can already see, not a bypass guarantee.
- **Exact field names.** Every output field this actor can emit is listed under [Output fields](#output-fields) above.

## Fixture-backed examples (synthetic)

Two synthetic, trimmed rows that show the output shape; they are not live Space observations. The first is a Space row from a run with `maxItemsPerSource` set, the second is the status row for a Space that showed a login wall.

```json
{"content_type":"space","space_url":"https://example-space.quora.com/","name":"Fixture Space","space_visibility":"public","follower_count":"12K","follower_count_value":12000,"access_state":"public","requested_depth":"detail","observed_depth":"detail","detail_expansion_state":"completed","source_cap":20,"source_items_observed":8,"source_items_emitted":8,"source_cap_reached":false,"field_sources":{"space_visibility":"visible_dom_or_structured_data","follower_count_value":"derived_signals","access_state":"runtime_or_access"}}
```

```json
{"content_type":"status","access_state":"login_required","http_status":200,"requested_depth":"detail","observed_depth":"status","detail_expansion_state":"blocked","field_sources":{"access_state":"runtime_or_access","http_status":"runtime_or_access"}}
```

## Complete schema input inventory

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `spaceUrls` | array | `[]` | Direct `/q/` Space routes or Space subdomain URLs to monitor |
| `urls` | array | `[]` | Any public Quora URL (question, answer, profile, topic, or post) to monitor for content changes; requires `stateStoreId` |
| `startUrls` | array | `[]` | Request-list objects for any public Quora URL, routed the same way as `spaceUrls`/`urls` |
| `searchQueries` | array | `[]` | Native Quora search queries used to discover additional Space/entity links |
| `maxDiscoveryResults` | integer | `20` | Maximum Space links returned per discovery query (1–500) |
| `includeMetadata` | boolean | `true` | Emit a Space metadata row for each successfully observed Space |
| `includeFeed` | boolean | `true` | Emit feed item rows |
| `scrapeDepth` | select | `detail` | `overview` (metadata/status only) or `detail` (adds feed/contributor/scroll traversal) |
| `feedTab` | select | `all` | Which feed tab to select: `all`, `posts`, `questions`, `top`, `unanswered`, `about`, or `rules` |
| `includeContributors` | boolean | `false` | Emit contributor rows found inside explicitly labeled role regions |
| `contributorRoles` | array | `["owner","moderator","admin","contributor"]` | Role labels accepted for contributor rows |
| `maxFeedItems` | integer | `50` | Maximum feed rows per Space (0–5000) |
| `maxContributors` | integer | `50` | Maximum contributor rows per Space (0–5000) |
| `maxFeedQuestionExpansions` | integer | `0` | Number of question-type feed items to expand into full question fields, when `scrapeDepth` is `detail` (0–500) |
| `includeFeedText` | boolean | `true` | Include visible feed text |
| `includeMedia` | boolean | `false` | Include media URLs from feed cards |
| `includeOutboundLinks` | boolean | `false` | Include outbound links from feed cards |
| `includeRules` | boolean | `true` | Include Space rules/guidelines text |
| `includeTopics` | boolean | `true` | Include Space topic links |
| `includeSettings` | boolean | `false` | Include explicitly labeled Space settings/content-permission evidence |
| `maxScrollAttempts` | integer | `5` | Maximum scroll attempts for feed traversal (0–20) |
| `maxLoadMoreAttempts` | integer | `5` | Maximum "load more" button activations (0–20) |
| `onlyNewItems` | boolean | `false` | Suppress unchanged rows; requires `stateStoreId` |
| `includeUnchanged` | boolean | `true` | Keep unchanged rows when `onlyNewItems` is enabled |
| `stateStoreId` | string | `""` | Key-value store name used to remember previous snapshots; required for `onlyNewItems` or `urls` |
| `stateRetentionDays` | integer | `0` | Age-based pruning for stored snapshots; `0` disables pruning (0–3650) |
| `diffMode` | select | `hash_and_summary` | Change-evidence detail level: `hash_only`, `field_summary`, `field_values`, or `hash_and_summary` |
| `maxItems` | integer | `0` | Global output row cap; `0` means no cap (0–50000) |
| `requestDelay` | number | `2` | Delay between source pages, in seconds (0–30) |
| `maxConcurrency` | integer | `1` | Source pages processed concurrently (1–3) |
| `maxNavigationRetries` | integer | `2` | Retries for transient navigation failures (0–3) |
| `language` | select | `auto` | Browser language hint; doesn't translate content |
| `cookies` | array | `[]` | Optional structured session cookies |
| `cookieString` | string | – | Optional `name=value; name2=value2` cookie header, parsed locally |
| `proxyConfiguration` | proxy | RESIDENTIAL | Apify proxy configuration; defaults to the residential group for reliable access |
| `outputFields` | array | `[]` | Optional allowlist of field names (including dotted nested paths) to keep in each row |
| `includeFieldEvidence` | boolean | `true` | Keep `field_sources`/`fields_present` on each row |
| `maxItemsPerSource` | integer | `0` | Maximum rows emitted per individual source URL/query; `0` means no per-source cap (0–5000) |

## Example inputs

### Example: monitor a Space's metadata and feed

```json
{
  "spaceUrls": ["https://cryptocurrency.quora.com/"],
  "includeMetadata": true,
  "includeFeed": true,
  "maxFeedItems": 50
}
```

### Example: track changes on a specific question over time

```json
{
  "urls": ["https://www.quora.com/What-is-the-future-of-AI"],
  "stateStoreId": "my-quora-watchlist",
  "onlyNewItems": true
}
```

### Example: discover Spaces by topic and list their contributors

```json
{
  "searchQueries": ["machine learning"],
  "includeContributors": true,
  "maxContributors": 20
}
```

## Use cases

- **Community monitoring** — get notified only when a Space you follow actually changes, instead of re-reading it every time.
- **Research tracking** — watch a specific question or answer for edits over weeks or months.
- **Topic discovery** — use search queries to surface Spaces and discussions around a subject you're researching.
- **Moderator/owner mapping** — list the explicitly labeled roles in a community you're studying.
- **Content audit trails** — keep a changed-fields history of a Space's rules or settings over time.

## FAQ

**Is this affiliated with Quora?**
No. This actor reads Quora's public pages and is not operated by or affiliated with Quora.

**Do I need to log in?**
No for public content. Optional `cookies`/`cookieString` let you supply your own session if you want to monitor content that requires one, but this is not a guarantee of access to private content.

**Why do I see a `status` row instead of data?**
Quora returned something this actor can't read as content — a login wall, a Cloudflare challenge, a removed page, or a network error. The row reports `access_state` and `http_status` instead of guessing.

**What's the difference between Space URLs and other Quora URLs?**
Space URLs (`/q/...` or a Space subdomain) get the full metadata/feed/contributor treatment. Any other Quora URL (question, answer, profile, topic, post) only gets a lighter title/content-hash change check via `urls`.

**Why didn't a field like `follower_count` show up?**
Fields are only populated from explicit, visible evidence on the page. If a count or label isn't shown, the field is simply absent rather than guessed.

**What does `onlyNewItems` actually suppress?**
With a `stateStoreId` set, rows whose content hasn't changed since the last run are dropped when `onlyNewItems` is `true`, unless `includeUnchanged` keeps them.

**Can I get just a few specific fields back?**
Yes — `outputFields` lets you allowlist field names (including nested paths like `topic_links.topic_name`) for a compact row; identity, access and source-accounting fields always stay.

**Does `scrapeDepth: overview` still check for changes?**
Yes for Space metadata, but it skips feed, contributor, scroll and load-more traversal, so you won't get feed-level change rows.
