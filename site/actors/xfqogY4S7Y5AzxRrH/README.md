# Pinterest Rich Pin, Board & Creator Field Scraper

Pinterest's own pages carry far more structured data than a basic Pin scrape surfaces — media variants, full creator and board objects, product and SEO metadata, Story Pin pages, and reaction breakdowns. This actor pulls that deeper field set for Pins, profiles, boards, search results, and public comments, without requiring login cookies; anything Pinterest doesn't publish for a given record is simply left out of the newer camelCase fields.

## What this actor does

- **Ten collection modes plus auto-detect:** Pin detail, Pin comments, Pin search, video search, profile detail, a creator's Pins, a creator's boards, board detail, and board Pins, plus `auto` for pasted links.
- **Rich Pin context:** media variants, creator and original-creator objects, board objects, destination links, product and SEO metadata, Story Pin pages and reaction counts when Pinterest supplies them.
- **Pin filters:** saves, creator followers, verified creator, destination link, image-only, promoted Pins and shoppable Pins. They apply to Pin rows only, never to profile, board or comment rows.
- **Cursor paging:** follows Pinterest's own next-page cursors for searches, creator feeds and boards, and skips Pins already returned earlier in the run.
- **Omitted fields:** the camelCase fields are dropped when Pinterest doesn't supply them. A few older snake_case fields fall back to `0`, `false` or `"public"` instead (see the note under the output section).

## Output per record

Every row includes `record_type` (`pin`, `profile`, `board` or `comment`), `source_url` (the search, profile, board or Pin page it came from) and `scraped_at`.

### Pin fields

Many Pin values appear twice: once under an older snake_case name and once under a newer camelCase name. Any field below may be absent when Pinterest doesn't expose it for that Pin.

- **Identity & text:** `id`/`pinId`, `url`/`pinUrl`, `title`, `description`, `altText`, `created_at`/`createdAt`, `dominant_color`, `link`/`linkUrl`, `linkDomain`, `domain`, `contentCategory`, `canonicalUrl`, `canonicalPinId`, `canonicalPinUrl`
- **Media:** `images` (size → URL map), `imageUrl`, `imageVariants`, `videoVariants`, `video_url`/`videoUrl`, `is_video`/`isVideo`, `mediaType` (`image`, `animatedImage` or `video`), `pinFormat` (`story` for Story Pins), `mediaMethod`, `storyPinId`, `storyPages`
- **SEO & link tracking:** `seoTitle`, `seoDescription`, `seoUrl`, `mobileLinkUrl`, `trackedLinkUrl`, `utmLinkUrl`
- **Creator:** `creator`, `creatorId`, `creatorUsername`, `creatorName`, `creatorFollowerCount`, `originalCreator` (only when it differs from `creator`), `pinner_id`, `pinner_username`, `pinner_name`, `pinner_followers`
- **Board:** `board`, `boardId`/`board_id`, `boardName`/`board_name`, `boardDescription`, `boardUrl`/`board_url`, `boardCoverImageUrl`, `boardPinCount`, `boardFollowerCount`, `boardSectionCount`, `boardCollaboratorCount`, `boardPrivacy`, `boardCreatedAt`, `boardIsCollaborative`, `boardFollowedByMe`
- **Engagement:** `saves`/`save_count`, `commentCount`/`comment_count`, `repinCount`, `shareCount`, `likeCount`/`like_count`, `reactionCount`/`reaction_count`, `reactionCounts`/`reaction_counts`
- **Status flags:** `isPromoted`, `commentsDisabled`, `commentsEligible`, `isEligibleForImageDownload`, `isEligibleForProduct`, `isOutOfStock`, `isStaleProduct`, `isUnsafeForComments`, `isDownstreamPromotion`, `shouldMute`
- **Shopping:** `product`, `isShoppable`, `shoppingFlags`, `richMetadata`

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

**Note on fallback values:** the camelCase fields are only written when Pinterest supplies a value. A few older snake_case fields are filled with a fallback instead when Pinterest omits them: `pinner_followers` and `reaction_count` on Pins, `follower_count`, `following_count`, `pin_count`, `board_count` and `is_verified` on profiles, and `pin_count`, `follower_count` and `privacy` (`"public"`) on boards. Use the camelCase equivalent when you need to tell "zero" apart from "not published".

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `auto` | `auto`, `pinDetail`, `comments`, `searchPins`, `searchVideos`, `userProfile`, `userPins`, `userBoards`, `boardDetail`, `boardPins`, or `search` (same as `searchPins`). |
| `keywords` / `searchTerms` | array | `[]` | Search phrases. Used by the search modes and by `auto`; merged together with `search`. |
| `search` | string | – | One extra search phrase, added to `keywords`. |
| `pinUrls` / `pinterestUrls` | array | `[]` | Pin URLs or numeric Pin IDs for `pinDetail` and `comments`. In `auto` they are used only when `startUrls` is empty, and only full Pin URLs are recognised there. |
| `usernames` / `profiles` | array | `[]` | Usernames, `@usernames` or profile URLs for `userProfile`, `userPins` and `userBoards`. Not read in `auto` mode. |
| `boardUrls` / `boards` | array | `[]` | Board URLs or `username/board-name` paths for `boardDetail` and `boardPins`. Not read in `auto` mode. |
| `startUrls` | array | – | Mixed Pin, profile, board and search URLs for `auto` mode. A profile URL returns the profile row plus that person's Pins. |
| `maxItems` | integer | `50` | Maximum records for the run (`0` = no limit, up to 20,000). Counts Pin rows in Pin-producing modes, and profile or board rows in `userProfile`, `userBoards` and `boardDetail`. Comment rows and the profile row added by profile URLs are not counted. |
| `maxPages` | integer | `0` | Pages per search, creator feed or board. Only read when `endPage` is absent from the input; because `endPage` has its own default, set `endPage` instead. |
| `endPage` | integer | `0` | Pages per search, creator feed or board; `0` follows Pinterest's cursor until it ends. |
| `minSaves` | integer | – | Keep Pins with at least this many saves. Pins without a save count are dropped. |
| `minCreatorFollowers` | integer | – | Keep Pins whose creator has at least this many followers. |
| `verifiedOnly` | boolean | `false` | Keep only Pins whose creator object is marked verified. Profiles and boards are not filtered. |
| `requireOutboundLink` | boolean | `false` | Keep only Pins with a destination link. |
| `imageOnly` | boolean | `false` | Drop Pins Pinterest marks as video. |
| `excludeAds` | boolean | `false` | Drop Pins marked as promoted. |
| `commerceOnly` | boolean | `false` | Keep only Pins with product or shopping data. |
| `includeComments` | boolean | `false` | Add comment rows after each collected Pin. |
| `maxComments` | integer | `10` | Maximum comment rows per Pin (1–20,000). |
| `enrichDetails` | boolean | `false` | Re-open each feed Pin (search, creator, board) to refresh its comment, reaction and save counts, creator name/username/followers and video fields. |
| `cookies` / `cookiesJson` | array/string | – | Optional Cookie-Editor export. Not needed for any mode. |
| `proxy` / `proxyConfiguration` | object | – | Optional proxy configuration. |

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

### What does `enrichDetails` change?

For Pins found through search, creator or board feeds, it opens each Pin's own page and overwrites the comment, reaction and save counts, the creator id, name, username and follower count, and the video flag and URL with the Pin page's values. It does not add new media, product or SEO fields, and it slows the run down. `pinDetail`, `comments` and Pin URLs in `auto` already read the Pin's own page.

### Are filters based on guessed engagement?

No. `minSaves`, `verifiedOnly`, `commerceOnly` and the other filters only pass a Pin when Pinterest supplied the value they test. A Pin with no published save count is dropped by `minSaves`.

### Which Pinterest links are recognised?

Pin, profile, board and `/search/pins/?q=` links on pinterest.com and its regional domains (such as pinterest.co.uk, .de, .fr, .ca, .com.au and .jp). Short `pin.it` links are not recognised.

### Is this affiliated with Pinterest?

No. It's an independent tool that reads publicly visible Pinterest data.
