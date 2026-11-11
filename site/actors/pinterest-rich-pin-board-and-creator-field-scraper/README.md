# Pinterest Rich Pin, Board & Creator Field Scraper

Pinterest's own pages carry far more structured data than a basic Pin scrape surfaces — media variants, full creator and board objects, product and SEO metadata, Story Pin pages, and reaction breakdowns. This actor pulls that deeper field set for Pins, profiles, boards, search results, and public comments, without requiring login cookies; anything Pinterest doesn't publish for a given record is simply left out of the newer camelCase fields.

## What this actor does

- **Ten collection modes plus auto-detect:** Pin detail, Pin comments, Pin search, video search, profile detail, a creator's Pins, a creator's boards, board detail, and board Pins, plus `auto` for pasted links.
- **Rich Pin context:** media variants, creator and original-creator objects, board objects, destination links, product and SEO metadata, Story Pin pages and reaction counts when Pinterest supplies them.
- **Pin filters:** saves, creator followers, verified creator, destination link, image-only, promoted Pins and shoppable Pins. They apply to Pin rows only, never to profile, board or comment rows.
- **Cursor paging:** follows Pinterest's own next-page cursors for searches, creator feeds and boards, and skips Pins already returned earlier in the run.
- **Encrypted feed IDs:** search and board feeds can return an opaque `e1_...` Pin ID instead of a numeric one. Those rows are kept as list records with `idIsEncrypted: true`, `detailAvailable: false` and no Pin URL, so a run is never silently empty.
- **Numeric-ID recovery:** for a creator feed that returns encrypted IDs, the actor reads the creator's public RSS feed (or the numeric user-pins feed) and emits openable numeric Pin rows when `resolveNumericIds` is on.
- **Run provenance:** every row carries `sourceType`, `sourceValue`, `position`, `seed`, and `query` on search rows, plus `numericIdSource` when a numeric ID was recovered.
- **Run summary:** the default key-value store gets a `RUN_SUMMARY` with raw rows, accepted rows, rejected rows and the reason a run returned nothing.
- **Omitted fields:** the camelCase fields are dropped when Pinterest doesn't supply them. A few older snake_case fields fall back to `0`, `false` or `"public"` instead (see the note under the output section).

## Output per record

Every row includes `record_type`/`recordType` (`pin`, `profile`, `board` or `comment`), `source_url` (the search, profile, board or Pin page it came from), `scraped_at`, `sourceType`, `sourceValue` and `position`. Search rows also carry `query`; every row carries `seed`. Rows produced from a recovered numeric ID carry `numericIdSource` (`userPins` or `profileRss`).

### Pin fields

Many Pin values appear twice: once under an older snake_case name and once under a newer camelCase name. Any field below may be absent when Pinterest doesn't expose it for that Pin.

- **Identity & text:** `id`/`pinId`, `idIsEncrypted`, `detailAvailable`, `commentsAvailable`, `url`/`pinUrl` (numeric Pins only), `title`, `description`, `altText`, `created_at`/`createdAt`, `dominant_color`, `link`/`linkUrl`, `linkDomain`, `domain`, `contentCategory`, `canonicalUrl`, `canonicalPinId`, `canonicalPinUrl`
- **Media:** `images` (size → URL map), `imageUrl`, `imageVariants`, `videoVariants`, `video_url`/`videoUrl`, `is_video`/`isVideo`, `mediaType` (`image`, `animatedImage` or `video`), `pinFormat` (`story` for Story Pins), `mediaMethod`, `storyPinId`, `storyPages`
- **SEO & link tracking:** `seoTitle`, `seoDescription`, `seoUrl`, `mobileLinkUrl`, `trackedLinkUrl`, `utmLinkUrl`
- **Creator:** `creator`, `creatorId`, `creatorUsername`, `creatorName`, `creatorFollowerCount`, `originalCreator` (only when it differs from `creator`), `pinner_id`, `pinner_username`, `pinner_name`, `pinner_followers`
- **Board:** `board`, `boardId`/`board_id`, `boardName`/`board_name`, `boardDescription`, `boardUrl`/`board_url`, `boardCoverImageUrl`, `boardPinCount`, `boardFollowerCount`, `boardSectionCount`, `boardCollaboratorCount`, `boardPrivacy`, `boardCreatedAt`, `boardIsCollaborative`, `boardFollowedByMe`
- **Engagement:** `saves`/`save_count`, `commentCount`/`comment_count`, `repinCount`, `shareCount`, `likeCount`/`like_count`, `reactionCount`/`reaction_count`, `reactionCounts`/`reaction_counts`
- **Status flags:** `isPromoted`, `commentsDisabled`, `commentsEligible`, `isEligibleForImageDownload`, `isEligibleForProduct`, `isOutOfStock`, `isStaleProduct`, `isUnsafeForComments`, `isDownstreamPromotion`, `shouldMute`
- **Shopping:** `product`, `productPrice`, `productCurrency`, `productMerchant`, `productAvailability`, `isShoppable`, `shoppingFlags`, `richMetadata`

`creator` and `originalCreator` can carry `id`, `username`, `fullName`, `firstName`, `followerCount`, `avatarSmallUrl`, `avatarMediumUrl`, `avatarLargeUrl`, `isVerified`, `isAdsOnly`, `isPrivate` and `followedByMe`. Each `imageVariants`/`videoVariants` entry is keyed by Pinterest's own size name and can carry `url`, `width`, `height`, `duration` and `thumbnailUrl`. Story Pin pages can carry `pageId`, `layout` and a block list with `type`, `text`, `images` and `videos`.

### Profile fields

- **Identity:** `type` (always `user`), `id`/`profileId`, `username`, `full_name`/`fullName`, `bio`, `location`, `createdAt`
- **Counts:** `follower_count`/`followerCount`, `following_count`/`followingCount`, `pin_count`/`pinCount`, `board_count`/`boardCount`, `monthlyViews`
- **Media & links:** `avatarUrls`, `avatarUrl`, `image_url`, `website_url`/`websiteUrl`, `domainUrl`, `profile_url`/`profileUrl`
- **Account flags:** `is_verified`, `isVerified`, `isPrivate`, `isPartner`, `isVerifiedMerchant`, `isDomainVerified`, `isTastemaker`

### Board fields

- **Identity:** `type` and `recordType` (both `board`), `id`/`boardId`, `name`, `description`, `url`, `owner_username`/`ownerUsername`, `owner_name`, `createdAt`
- **Counts:** `pin_count`/`pinCount`, `follower_count`/`followerCount`, `sectionCount`, `collaboratorCount`
- **Media & flags:** `coverImageUrl`, `privacy`, `isCollaborative`, `followedByMe`

### Comment fields

- **Content & identity:** `id`, `text`, `created_at`, `type`, `node_id`, `tags`, `tagged_users`, `media`, `pin_id`, `pin_url`
- **Author:** `author_name`, `author_username`, `author_id`, `author_first_name`, `author_image`, `author_image_medium`, `author_node_id`, `author_is_private_profile`
- **Engagement & state:** `like_count`, `reaction_counts`, `reaction_by_me`, `helpful_count`, `marked_helpful_by_me`, `reply_count`, `is_edited`, `is_highlighted_by_pin_owner`, `is_translatable`

**Note on absent values:** every field is written only when Pinterest supplied it for that record. An explicit `0` or `false` from Pinterest is kept; an unknown engagement count, follower count or video flag is omitted instead of being replaced with a made-up zero. `idIsEncrypted`, `detailAvailable` and `commentsAvailable` are always present because the actor can determine them from the ID shape.

### Encrypted Pin IDs

Pinterest increasingly returns an opaque ID such as `e1_AfqPShx7dj...` from search and board feeds. That ID is real, but `pinterest.com/pin/<id>/`, the Pin detail endpoint and oEmbed do not open it. The actor keeps the row:

- `id` and `pinId` contain the opaque ID exactly as Pinterest returned it.
- `idIsEncrypted` is `true` and `detailAvailable` is `false`.
- `aggregatePinId` is emitted when Pinterest supplies the aggregate comments ID. In that case `commentsAvailable` is `true` and `includeComments` can fetch the public comment thread without a Pin URL.
- `url` and `pinUrl` are omitted because no public Pin page exists.
- All list fields Pinterest did return remain: title, description, images, creator, board, reaction counts, saves (when the feed carries them), `created_at`, `domain`, `link`, video/story data and so on.

The actor never invents detail-only fields for these rows. If the same Pin is later found through a creator feed with a numeric ID, that row is openable and can be enriched.

### Numeric-ID recovery

`UserPinsResource` normally returns numeric IDs. When it returns only opaque IDs or no rows, `resolveNumericIds` (default on) makes the actor read the creator's public `/<username>/feed.rss`. RSS items carry a numeric Pin link, title, description, image and publication date; they are emitted with `sourceType: "profileRss"` and `numericIdSource: "profileRss"`. RSS contains only the creator's most recent Pins (about 21-25). The user-pins cursor is always preferred when it returns numeric rows.

### Commerce fields

When Pinterest supplies a real product payload (`product_pin_data`, `product_metadata` or `rich_summary.products[].offers`), the actor normalizes:

- `productPrice` in major currency units (Pinterest's `price_value` is in cents: `1364` -> `13.64`).
- `productCurrency` (upper-case ISO code), `productMerchant`, `productAvailability` (`in_stock`, `out_of_stock`, `preorder`, `backorder` or `stale`).
- `isShoppable` only when Pinterest published real product/shopping evidence. A `{type, id}` metadata stub alone is not treated as shoppable.

The original `product` object is kept for traceability.

### Run summary and zero-row behavior

Every run writes `RUN_SUMMARY` to the default key-value store:

```json
{
  "rawRows": 20,
  "accepted": 5,
  "rejected": 0,
  "recordsByType": { "pin": 5 },
  "sources": [
    { "sourceType": "search", "sourceValue": "cats", "rawRows": 20, "accepted": 5, "rejected": 0, "rejectReasons": {} }
  ]
}
```

When a valid source returns rows but none can be emitted, the run fails with a reason such as `opaque_id_not_openable` or `source_returned_no_rows`. When filters deliberately remove every row, the run warns with `all_rows_filtered_out`. The status message always shows raw / accepted / rejected / reason, so a zero-row run is never reported as a plain success.

## Input

At least one source is required: `keywords`, `startUrls`, `pinUrls`, `usernames`, `boardUrls`, or an explicit mode with its matching source. The auto prefill is `search=cats`; Apify's validator cannot express "one of", so the actor documents the fallback.

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `auto` | `auto`, `pinDetail`, `comments`, `searchPins`, `searchVideos`, `searchUsers`, `searchBoards`, `userProfile`, `userPins`, `userBoards`, `boardDetail`, `boardPins`, `ideas`, or `search` (same as `searchPins`). |
| `keywords` | array | `[]` | Search phrases. Used by the search modes and by `auto`; merged together with `search`. Legacy `searchTerms` is mapped in code. |
| `search` | string | – | One extra search phrase, added to `keywords`. |
| `pinUrls` | array | `[]` | Pin URLs or numeric Pin IDs for `pinDetail` and `comments`. Legacy `pinterestUrls` is mapped in code. |
| `usernames` | array | `[]` | Usernames, `@usernames` or profile URLs for `userProfile`, `userPins` and `userBoards`. Legacy `profiles` is mapped in code. |
| `boardUrls` | array | `[]` | Board URLs or `username/board-name` paths for `boardDetail` and `boardPins`. Legacy `boards` is mapped in code. |
| `startUrls` | array | – | Mixed Pin, profile, board and search URLs for `auto` mode. A profile URL returns the profile row plus that person's Pins. |
| `maxItems` | integer | `50` | Maximum records for the run (`0` = no limit, up to 20,000). Counts Pin rows in Pin-producing modes, and profile or board rows in `userProfile`, `userBoards` and `boardDetail`. Comment rows and the profile row added by profile URLs are not counted. |
| `maxPages` | integer | `0` | Pages per search, creator feed or board. `0` follows Pinterest's cursor until it ends. Legacy `endPage` is mapped in code. |
| `minSaves` | integer | – | Keep Pins with at least this many saves. Pins without a save count are dropped. |
| `minCreatorFollowers` | integer | – | Keep Pins whose creator has at least this many followers. |
| `verifiedOnly` | boolean | `false` | Keep only Pins whose creator object is marked verified. Profiles and boards are not filtered. |
| `requireOutboundLink` | boolean | `false` | Keep only Pins with a destination link. |
| `imageOnly` | boolean | `false` | Drop Pins Pinterest marks as video. |
| `excludeAds` | boolean | `false` | Drop Pins marked as promoted. |
| `commerceOnly` | boolean | `false` | Keep only Pins with product or shopping data. |
| `includeComments` | boolean | `false` | Add comment rows after each collected Pin. |
| `maxComments` | integer | `10` | Maximum comment rows per Pin (1-20,000). |
| `includeCommentReplies` | boolean | `false` | Fetch depth-one replies for comments that report replies. |
| `maxCommentReplies` | integer | `10` | Maximum replies fetched per top-level comment (1-200). |
| `enrichDetails` | boolean | `false` | Re-open each feed Pin (search, creator, board) to refresh its comment, reaction and save counts, creator name/username/followers and video fields. |
| `resolveNumericIds` | boolean | `true` | When a creator feed returns only encrypted Pin IDs, read the creator's public RSS feed (or numeric user-pins feed) to emit openable numeric Pin rows. Turn off to keep only the IDs the creator feed itself returns. |

### Example: detailed Pin

```json
{
  "mode": "pinDetail",
  "pinUrls": ["https://www.pinterest.com/pin/142567144448888376/"]
}
```

### Example: creator feed with refreshed counts

```json
{
  "mode": "userPins",
  "usernames": ["crazylaurablog"],
  "maxItems": 2000,
  "endPage": 0,
  "enrichDetails": true
}
```

### Example: board Pins with comments

```json
{
  "mode": "boardPins",
  "boardUrls": ["https://www.pinterest.com/nasa/hubble-images/"],
  "maxItems": 500,
  "includeComments": true,
  "maxComments": 20
}
```

### Example: filtered video search

```json
{
  "mode": "searchVideos",
  "keywords": ["easy dinner", "travel guide"],
  "excludeAds": true,
  "maxItems": 500
}
```

## Use cases

- Audit the destination links, SEO titles and alt text on a brand's Pins.
- Compare creators by follower counts, monthly views and verification flags.
- Inventory a board's Pins together with their section and collaborator counts.
- Collect Story Pins and video Pins with every published media size for a creative library.
- Read the comment threads under high-save Pins in a niche.
- Track which Pins in a search are shoppable, out of stock or promoted.

## FAQ

### Do I need to log in?

No. Every mode works signed-out. The cookie inputs are optional and no mode depends on them.

### What happens if I run it with no input?

When no search phrase, URL, username or board is given, the actor collects the single example Pin from the input form so the run still produces a record.

### Why were my usernames or boards ignored?

In `auto` mode the actor only reads `keywords`/`search`, `startUrls` and (when `startUrls` is empty) `pinUrls`. Pick `userProfile`, `userPins`, `userBoards`, `boardDetail` or `boardPins` to use `usernames` or `boardUrls`, or paste the profile and board links into `startUrls`.

### What is the difference between `searchPins` and `searchVideos`?

Both run the same Pinterest Pin search. `searchVideos` then keeps only the results Pinterest marks as video, so it can page through more results to fill `maxItems`. `search` is an older name for `searchPins`.

### Can a run return more than 10,000 rows?

Yes. `maxItems` goes up to 20,000 (or `0` for no limit), and the actor keeps following Pinterest's cursor as long as Pinterest returns more Pins.

### Why can a feed contain fewer rows than the account's visible Pin count?

Signed-out feeds, cursor limits, privacy settings, duplicate Pins and your filters all shrink the result. For boards, the actor loads up to `maxItems` Pins first and then applies the filters, so a filtered board run can return fewer rows than `maxItems`.

### Why do some rows have no `url` or detail counts?

Search and board feeds can return an encrypted `e1_...` Pin ID. Pinterest does not open that ID as a Pin page and does not return its detail. Those rows are still real list records: `idIsEncrypted` is `true`, `detailAvailable` is `false`, and `url`/`pinUrl` are left out. The list fields Pinterest did publish remain. When Pinterest supplies an aggregate comments ID (`aggregatePinId`), the actor can still fetch the public top-level comments for that row. Set `includeCommentReplies` to fetch depth-one replies for comments that report replies; each reply carries `parentCommentId` and `depth: 1`. Deeper nesting is not exposed by the public resource.

### What does `resolveNumericIds` do?

For a creator feed, it enables the numeric-ID recovery path. If the creator's Pin list is empty or contains only encrypted IDs, the actor reads the creator's public RSS feed and emits numeric Pin rows there. RSS is recent-only; set the option to `false` if you want only the IDs the creator feed itself returns.

### Why is a run marked failed with zero rows?

The actor now treats a zero-row run as a bug when the source returned rows it could not emit. The status message and `RUN_SUMMARY` show `rawRows`, `accepted`, `rejected` and a reason such as `opaque_id_not_openable` or `source_returned_no_rows`. A run that is empty because your filters removed every row warns with `all_rows_filtered_out` instead of failing.

### Why is `productPrice` missing on most Pins?

Pinterest publishes product payloads only for a small subset of Pins. The actor fills `productPrice`, `productCurrency`, `productMerchant`, `productAvailability` and `isShoppable` only when Pinterest supplies real product data or shopping flags. A metadata stub with just a type and ID is not treated as a product.

### What does `enrichDetails` change?

For Pins found through search, creator or board feeds, it opens each Pin's own page and overwrites the comment, reaction and save counts, the creator id, name, username and follower count, and the video flag and URL with the Pin page's values. It does not add new media, product or SEO fields, and it slows the run down. `pinDetail`, `comments` and Pin URLs in `auto` already read the Pin's own page.

`maxItems` counts Pins/source records. Comment rows, including opt-in replies, are additional and are capped by `maxComments` and `maxCommentReplies`; a comments run can therefore produce more dataset rows than `maxItems`.

### Are filters based on guessed engagement?

No. `minSaves`, `verifiedOnly`, `commerceOnly` and the other filters only pass a Pin when Pinterest supplied the value they test. A Pin with no published save count is dropped by `minSaves`.

### Which Pinterest links are recognised?

Pin, profile, board, board-section, Ideas, `/search/pins/?q=`, `/search/users/?q=` and `/search/boards/?q=` links on pinterest.com and its regional domains (such as pinterest.co.uk, .de, .fr, .ca, .com.au and .jp). Short `pin.it` links are not recognised.

### What do the newer modes return?

- `searchUsers` and `searchBoards` return public people/board search results with cursor pagination.
- `ideas` returns the Pins in an Ideas feed (list-only; the public feed has no detail/comments).
- A three-segment board-section URL reads `BoardSectionsResource` + `BoardSectionPinsResource`, which is the best cookieless source of numeric Pin IDs.
- Profile tabs are routed honestly: `pins`/`_created` read created Pins, `boards` reads the person's boards, and unsupported tabs (`_saved`, followers, following, likes, activity) warn instead of returning unrelated Pins.
- Related-Pins mode is not exposed because the public resource worked locally but returned no rows from the cloud exit. The `e1_...` to numeric mapping remains a hard limit; use board sections, user Pins and creator RSS for numeric recovery.

### Why do some outbound `linkUrl` values return 403?

The outbound link is exactly what Pinterest supplied. Etsy short links (`etsy.me`) can reject clean non-browser clients with 403; the destination is still valid in a browser. Pin media, profile and board URLs were verified HTTP 200.

### Is this affiliated with Pinterest?

No. It's an independent tool that reads publicly visible Pinterest data.
