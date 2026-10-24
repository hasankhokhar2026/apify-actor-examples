# Quora Question, Answer & Relationship Dataset Builder

Build a structured Quora dataset from direct links or native Quora search terms. Point it at question, answer, profile, Topic, Space, or Post URLs — or a search phrase — and it returns normalized rows for every entity it finds, with the question → answer → comment chain and author/topic links kept intact. Choose how deep to go, how the rows are shaped, and which relationship data (followers, upvoters, Space roles) to include.

## What this actor does

- Accepts question, answer, profile, Topic, Space, and Post URLs directly, or a plain Quora search phrase
- Walks the question → answer → comment chain and keeps the links between them (`entity_edge` rows), so you can rebuild the conversation tree
- Offers four output shapes via `outputFormat`: `normalized` (separate rows per entity, default), `nested` (answers grouped under their question, comments under their answer), `flat`, and `edges` (relationship rows plus any status rows)
- Optionally expands follower, following, upvoter, and Space-role relationships for a profile, question, answer, or Space, with a privacy gate for identity-revealing collections
- Optionally re-scrapes the same inputs later and flags each row as `new`, `changed`, `unchanged`, or `scope_mismatch` against a saved state store
- Can restrict the returned fields to a smaller allowlist (`outputFields`) while still protecting identity and status fields
- Reports a `status` row (rather than guessing) whenever a page is blocked, login-gated, or otherwise inaccessible, and a `run_manifest` row summarizing the whole run; both are in the default `resultTypes`, so removing them from that list removes them from the output
- Leaves empty content fields out of each row rather than filling them with a guess (a few bookkeeping fields, such as `url_redactions`, may still appear as empty lists)

## Output per record

Every row carries `content_type` (`question`, `answer`, `comment`, `profile`, `profile_activity`, `topic`, `topic_post`, `space`, `space_feed_item`, `entity_edge`, `relationship_collection`, `status`, or `run_manifest`), plus shared fields: `record_id`, `title`, `url`, `canonical_url`, `source_url`, `access_state`, `scrape_timestamp`, `requested_depth`, `observed_depth`, `detail_expansion_state`, `output_format`, `matched_input`, `matched_input_kind`, and (when search seeds were used) `source_query`/`source_queries`.

Every row also carries run-context fields describing how it was collected: `source_observations`/`source_observation_count`, `redirect_chain`, `url_redaction_state`/`url_redactions`, `proxy_used`, `proxy_resolution_state`, `session_cookie_count`, `session_input_state`, `session_cookie_expiry_state`, `request_delay_seconds`, `browser_locale`, `requested_language`, `navigation_retries`/`navigation_retry_delays_seconds`, `parser_version` and `parser_strategy`. With `includeFieldEvidence` on (default), rows also get `field_sources` (where each value came from) and `fields_present`.

`access_state` is `public` for normal pages; other values include `login_required`, `cloudflare_challenge`, `not_found`, `removed`, `unavailable`, `quora_plus_or_gated`, `redirected_to_search`/`_topic`/`_space`, `unsupported_url` and `network_error`.

**Question row** — `question_url`, `question_answer_count` (label) / `question_answer_count_value` (parsed number) / `question_answer_count_scraped` (rows actually collected), `question_created_at`, `question_updated_at`, `question_age_days`/`question_age_state`, `last_answered_at` + `last_answered_at_evidence`, `question_author_name`/`_url`/`_image_url`/`_id`/`_is_verified`/`_is_anonymous`/`_credentials`, `question_image_urls`/`_video_urls`/`_outbound_links` (opt-in), `answer_count`, `answer_limit_reached`, `topics`, `topic_links`.

**Answer row** — `answer_id`, `answer_url`, `answer_text`, `answer_html` (opt-in), `answer_media_urls`/`_image_urls`/`_video_urls`/`_outbound_links` (opt-in), `answer_translation_state`/`_label`, `answer_original_url`, `answer_is_anonymous`, `answer_author_is_verified`, `answer_created_at`/`_updated_at`, `answer_age_days`/`_state`, `answer_visibility`, `answer_text_completeness`, `answer_is_collapsed`, `answer_is_quora_plus`, `answer_is_top_labeled`, `answer_rank`/`_rank_source`, `answer_upvote_count`/`_value`, `answer_comment_count`/`_value`, `answer_view_count`/`_value`, `answer_share_count`/`_value`, `reaction_breakdown` (opt-in), `is_ai_answer`/`ai_label_text`/`ai_label_source`, `related_content`/`_count`/`_observed_count`/`_limit_reached` (opt-in), `answer_jsonld_type`, `author_name`/`_url`/`_image_url`/`_id`/`_credentials`.

**Comment row** — `comment_id`, `comment_url`, `comment_text`, `comment_author_name`/`_image_url`/`_id`/`_credentials`/`_is_verified`, `comment_is_anonymous`, `comment_timestamp`/`_created_at`, `comment_age_days`/`_state`, `comment_visibility`, `comment_upvote_count`/`_value`, `comment_reaction_count`/`_value`, `comment_reply_count`/`_value`, `comment_reaction_breakdown`, `comment_media_urls`/`_image_urls`/`_video_urls`/`_outbound_links`, `comment_is_top_labeled`, `comment_rank`/`_rank_source`, `comment_sort_order`, `comment_depth`, `comment_depth_limit_reached`, `comment_is_reply`, `parent_comment_id`/`_url`, `comment_reply_path`.

**Profile row** — `profile_url`, `profile_name`, `profile_bio`, `profile_image_url`, `profile_author_id`, `profile_is_verified`, `profile_is_restricted`, `profile_snapshot_state`.

**Profile-activity row** — `activity_url`, `author_name`/`_url`/`_image_url`/`_id`/`_credentials`.

**Topic row** — `topic_url` plus the shared fields above.

**Topic-Post row** — `post_url`, `post_title`, `post_body`, `post_media_urls`/`_image_urls`/`_video_urls`/`_outbound_links` (opt-in), `post_author_name`/`_url`/`_image_url`/`_id`/`_credentials`/`_is_verified`/`_is_anonymous`, `post_created_at`/`_updated_at`, `post_age_days`/`_state`, `post_updated_age_days`/`_state`.

**Space row** — `space_url` plus the shared fields above.

**Space feed-item row** — `feed_url`, `feed_type`, `feed_title`, `feed_text` (opt-in), `feed_author_name`/`_url`/`_image_url`/`_id`/`_credentials`/`_is_verified`/`_is_anonymous`, `feed_created_at`, `feed_age_days`/`_state`, `media_urls`/`image_urls`/`video_urls`/`outbound_links`.

**Relationship row (`entity_edge`)** — `relationship`, `edge_id`, `from_record_id`/`_content_type`/`_url`/`_id`, `to_record_id`/`_content_type`/`_url`/`_id`/`_name`/`_image_url`, `node_image_url`, `edge_state`, `unresolved_reason`.

**Relationship-count row (`relationship_collection`)** — `relationship_collection_key`, `collection_total_text`, `collection_total_value`, `edge_evidence_field`.

**Status row** — `access_state`, `http_status`, `error`, `source_url`, and for pages that failed to load `final_url`, `scrape_duration_ms`, `navigation_attempts`, `navigation_retries`. Run-level status rows (`url: run://quora-dataset-builder`) report a state store that couldn't be read (`state_store_unavailable`) or state that wasn't saved because a source didn't finish (`state_store_uncommitted`).

**Option-dependent fields** — with a `stateStoreId`, entity rows add `event_type` (`new`/`changed`/`unchanged`/`scope_mismatch`), `state_snapshot_hash`, `previous_snapshot_hash`, `state_scope_fingerprint`, `state_store_state`, `only_new_items`, `include_unchanged`. With `includeRawEvidence`, page-level rows add `raw_html_sha256`, `raw_html_bytes`, `raw_evidence_state` and related size/redaction fields, plus `raw_html` when `includeHtml` is also on. In `nested` format, question rows carry `answers` arrays (each answer with its `comments`) and `nested_*` count fields. With `maxItemsPerSource` set, rows add `max_items_per_source` and per-source cap fields.

**Run-manifest row** — one per run, summarizing counts and the settings actually applied: `run_started_at`/`_finished_at`/`_duration_ms`, `records_emitted`, `source_pages_attempted`, `content_type_counts`, `access_state_counts`, `input_accounting`, `requested_result_types`, `requested_output_fields`, `dedupe_mode`, `duplicate_records_suppressed`, `relationship_collection_diagnostic`, and the per-run values of several of your own input settings (language, concurrency, caps) echoed back for reconciliation.

## Trimming rows, depth and sessions

- **Field allowlist.** `outputFields` keeps only the fields you name, applied after extraction; an empty list returns the full row. Nested projection is supported with bounded dotted paths such as `answers.answer_text` or `answers.comments.comment_text` in `nested` output, and child identity/URL fields stay in place. `content_type`, identity, access/status, depth, timing and parser fields are always protected so a trimmed row can still be traced. `output_projection` on each row reads `full` or `selected`, and the run manifest records the requested fields. `includeFieldEvidence` toggles the `field_sources`/`fields_present` maps.
- **Depth.** `scrapeDepth: "detail"` (default) runs the capped traversal; `overview` emits page-level summaries without answer, comment, profile-activity or Space-feed expansion. Every row reports `requested_depth`, `observed_depth` and `detail_expansion_state`. `bounded` means a configured cap was reached, not that Quora's full history was collected, and blocked pages report `observed_depth: "status"`.
- **Author credentials.** `question_author_credentials`, `comment_author_credentials`, `post_author_credentials`, `feed_author_credentials` and `author_credentials` are kept only when a credential or tagline is visibly shown in that author's own region of the page. Ambiguous text is dropped, and none of these fields verifies expertise.
- **Sessions.** Supply structured `cookies` or the secret `cookieString` header (`name=value; name2=value2`). Structured cookies win on duplicate names, malformed pairs are ignored, and the raw header is never emitted or logged. Cookies only open content your account can already see; they are not a bypass guarantee.
- **Exact field names.** Every output field this actor can emit is listed under [Output per record](#output-per-record) above.

## Fixture-backed examples (synthetic)

Synthetic, trimmed rows showing the output shape; they are not live Quora data. The first is a resolved question-to-topic edge from a run with `maxItemsPerSource` set, the second is the status row for a page that showed a Cloudflare challenge.

```json
{"content_type":"entity_edge","edge_id":"fixture-edge-1","relationship":"question_has_topic","from_content_type":"question","to_content_type":"topic","edge_state":"resolved","edge_evidence_field":"topic_links","access_state":"public","source_cap":50,"source_items_observed":12,"source_items_emitted":12,"source_cap_reached":false,"field_sources":{"relationship":"derived_relationships","edge_state":"derived_relationships","access_state":"runtime_or_access"}}
```

```json
{"content_type":"status","access_state":"cloudflare_challenge","http_status":403,"observed_depth":"status","detail_expansion_state":"blocked","field_sources":{"access_state":"runtime_or_access","http_status":"runtime_or_access"}}
```

## Complete schema input inventory

This actor has a large, modular input schema — most fields are optional toggles that only matter for a specific record type or feature.

| Field | Type | Default | Description |
|---|---|---|---|
| `startUrls` | array | `[]` | Question, answer, profile, Topic, Space, or Quora search URLs |
| `searchQueries` | array | `[]` | Plain Quora search terms |
| `questionUrls` / `answerUrls` / `topicUrls` / `spaceUrls` / `profileUrls` / `postUrls` | array | `[]` | Typed seed lists — use these instead of `startUrls` when you want unambiguous per-type accounting |
| `scrapeDepth` | string | `detail` | `overview` (page-level summary only: no answers, comments, scrolling or load-more) or `detail` (full traversal) |
| `resultTypes` | array | `["question", "answer", "comment", "profile", "profile_activity", "topic", "topic_post", "space", "space_feed_item", "entity_edge", "status", "run_manifest"]` | Which `content_type` values to include in the output |
| `outputFormat` | string | `normalized` | `normalized` / `nested` / `flat` / `edges` |
| `dedupeMode` | string | `canonical` | `canonical` (merge duplicate entities by canonical URL) or `none` |
| `onlyNewItems` | boolean | `false` | With `stateStoreId`, suppress rows unchanged since the last run |
| `includeUnchanged` | boolean | `true` | Keep unchanged rows when `onlyNewItems` is on |
| `stateStoreId` | string | `""` | Apify key-value store name for incremental re-scraping; required when `onlyNewItems` is on |
| `outputFields` | array | `[]` | Optional field allowlist for smaller rows; identity/status fields are always kept |
| `includeFieldEvidence` | boolean | `true` | Include `field_sources`/`fields_present` on each row |
| `includeUnresolvedEdges` | boolean | `true` | Keep relationship rows whose target couldn't be matched |
| `relationshipTypes` | array | `[]` | Allowlist of relationship collections to expand (follower, following, want-answers, upvoter, Space role, etc.); identity-revealing types are rejected unless `includeSensitiveRelationshipData` and the matching per-family opt-in are both on |
| `includeProfileEdges` / `includeQuestionFollowerEdges` / `includeAnswerUpvoterEdges` / `includeSpaceRoleEdges` | boolean | `false` | Per-family opt-ins for the relationship types above |
| `includeSensitiveRelationshipData` | boolean | `false` | Required alongside the identity-revealing relationship opt-ins (the run stops with an input error otherwise, e.g. for `includeAnswerUpvoterEdges`) |
| `includeTargetMetadata` | boolean | `false` | Keep the visible name/image of each relationship target |
| `includeRelationshipCounts` | boolean | `false` | Emit privacy-preserving member-count rows without identities; also add `relationship_collection` to `resultTypes`, which the default list doesn't include |
| `includeSpaceContentEdges` | boolean | `true` | Keep Space ↔ post/question membership edges |
| `maxRelationshipItemsPerCollection` | integer | `500` | Cap per relationship collection |
| `maxQuestions` | integer | `25` | How many question links discovered from search results, Topics, Spaces or profiles get queued, on top of your own seed URLs (max 1,000) |
| `maxAnswersPerQuestion` | integer | `10` | Maximum answers kept per question (max 500) |
| `maxAnswers` | integer | `0` | Global answer cap across the whole run (`0` = no cap) |
| `includeQuestion` | boolean | `true` | Keep question entities in the output |
| `includeAuthor` | boolean | `true` | Keep author/profile entities in the output |
| `includeTopics` | boolean | `true` | Keep topic entities in the output |
| `includeSpaces` | boolean | `false` | Keep Space and Space feed-item rows in the output; switched on automatically when `spaceUrls` is used |
| `includeComments` | boolean | `false` | Keep comment entities in the output (also needs `maxCommentsPerAnswer` above 0; turned on automatically by `includeReplyGraph`) |
| `includeAuthorSnapshot` | boolean | `false` | Fetch a bounded profile snapshot for each visible author link |
| `includeEngagementBreakdown` | boolean | `true` | Include per-reaction breakdowns alongside aggregate counts |
| `includeRelatedContent` / `maxRelatedContent` | boolean / integer | `false` / `20` | Collect an answer's "related" links, capped per answer |
| `topCommentsOnly` | boolean | `false` | Keep only comments explicitly labeled Top/Most helpful |
| `commentSortOrder` | string | `observed` | `observed` / `upvotes_desc` / `reactions_desc` / `replies_desc` / `newest` |
| `includeReplyGraph` / `maxCommentDepth` | boolean / integer | `false` / `20` | Keep nested comment replies, bounded by depth |
| `includeMedia` | boolean | `false` | Include image/video URL fields where available |
| `includeFeedText` | boolean | `false` | Include visible text on Space feed cards |
| `includeOutboundLinks` | boolean | `false` | Include non-Quora links found on a page |
| `includeEntityGraph` | boolean | `false` | Emit relationship rows even when `entity_edge` isn't in `resultTypes` |
| `maxCommentsPerAnswer` | integer | `0` | Comments kept per answer; at `0` no comments are collected even when `includeComments` is on |
| `maxItems` | integer | `0` | Cap on entity/status rows before graph/manifest rows (`0` = no cap, max 5,000) |
| `maxGraphEdges` | integer | `5000` | Cap on relationship rows |
| `maxScrollAttempts` | integer | `5` | Scroll attempts per page while loading more content |
| `maxLoadMoreAttempts` | integer | `0` | "Load more" button clicks per page |
| `includeRawEvidence` / `includeHtml` / `maxHtmlBytes` | boolean / boolean / integer | `false` / `false` / `100000` | Attach a document hash and optionally bounded raw HTML for auditing |
| `requestDelay` | number | `1` | Delay in seconds between page batches |
| `maxConcurrency` | integer | `1` | Pages processed in parallel (values above 3 are treated as 3) |
| `maxNavigationRetries` | integer | `2` | Retries after a failed page load (max 3) |
| `language` | string | `auto` | Browser language hint (`en`, `es`, `fr`, …) |
| `cookies` / `cookieString` | array / string | – | Optional session cookies for content you're authorized to view |
| `proxyConfiguration` | object | residential proxy | Proxy routing; residential is used by default, and leaving this empty or turning the proxy off still uses residential. Only an explicit proxy group or your own proxy URLs override it |
| `redactSensitiveQueryParams` | boolean | `true` | Strip credential-like query values from emitted URLs |
| `rawEvidenceRetentionDays` / `maxRawEvidenceBytes` | integer | `30` / `100000` | Retention label (at most 30 days) and size bound reported for raw HTML evidence, when enabled |
| `maxItemsPerSource` | integer | `0` | Cap on records from each individual source URL/query (`0` = no cap) |

## Example inputs

### Example: full detail for a question

```json
{
  "questionUrls": [{ "url": "https://www.quora.com/What-is-the-best-way-to-learn-Python" }],
  "maxAnswersPerQuestion": 20,
  "includeComments": true,
  "maxCommentsPerAnswer": 10
}
```

### Example: search seeds, compact nested output

```json
{
  "searchQueries": ["machine learning career advice"],
  "maxQuestions": 10,
  "outputFormat": "nested",
  "maxAnswersPerQuestion": 5
}
```

### Example: a Space's content and follower count

```json
{
  "spaceUrls": [{ "url": "https://www.quora.com/q/example-space" }],
  "resultTypes": ["space", "space_feed_item", "relationship_collection", "run_manifest"],
  "includeRelationshipCounts": true,
  "relationshipTypes": ["space_has_contributor"]
}
```

### Example: incremental re-scrape of the same question

```json
{
  "questionUrls": [{ "url": "https://www.quora.com/What-is-the-best-way-to-learn-Python" }],
  "onlyNewItems": true,
  "includeUnchanged": false,
  "stateStoreId": "python-question-watch"
}
```

## Use cases

- **Content research** — pull full question-answer-comment threads on a topic for analysis
- **Community monitoring** — re-scrape the same questions on a schedule and keep only rows flagged `new`/`changed`
- **Knowledge graph building** — use `outputFormat: "edges"` to load the question/answer/topic relationship graph into a graph database
- **Influencer and expert tracking** — follow a profile's answers and, with relationship counts enabled, its follower totals
- **Space analysis** — collect a Quora Space's feed and contributor structure

## FAQ

**Do I need a Quora account?**
No. Public Quora pages are read without login. Supplying `cookies`/`cookieString` loads pages as your own logged-in session, so only content your account can already see becomes available.

**Why did I get a `status` row instead of question/answer data?**
Quora showed a login wall, Cloudflare challenge, or a removed/redirected page for that URL. The actor reports this honestly as a `status` row instead of guessing at data that wasn't there.

**Why do I sometimes get fewer answers than `maxAnswersPerQuestion`?**
Quora's logged-out view can cap how many answers it renders per question, independent of your settings — especially on very high-traffic questions. This is a real ceiling on the source page, not a bug in the actor.

**What's the difference between the four `outputFormat` values?**
`normalized` keeps every entity as its own row (the default). `nested` groups each question's answers (and each answer's comments) underneath it; rows without a matching parent stay at the top level. `flat` is like `normalized`, except that answer rows also get `question_title` and comment rows get `answer_url`. `edges` returns the relationship rows between entities plus any status rows, so a blocked source still shows up.

**Can I get a Quora account's followers or who they follow?**
Only the Followers list currently returns identities (via `includeProfileEdges` + `includeSensitiveRelationshipData`); other relationship types (Following, Upvoters, Space roles) currently return accurate counts but not individual identities yet.

**What does the incremental re-scrape (`onlyNewItems`) actually compare?**
It hashes each entity's content and compares it to the previous run stored under `stateStoreId`, tagging each row `new`, `changed`, `unchanged`, or `scope_mismatch` (the previous run used different settings). Rows are only dropped when `onlyNewItems` is on and `includeUnchanged` is off. Status and manifest rows are never dropped by this setting. If any requested source didn't finish, the new state isn't saved and a `state_store_uncommitted` status row tells you so.

**Why are some text/media fields missing even with `includeMedia`/`includeHtml` on?**
Those fields are only populated when Quora's page actually renders that content for the entity in question — the toggles request the data, they don't guarantee every entity has it.

**Is this affiliated with Quora?**
No. This is an independent, third-party actor that reads Quora's public pages; it isn't affiliated with or endorsed by Quora, Inc.
