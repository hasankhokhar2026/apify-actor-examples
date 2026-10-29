# X (Twitter) Profile & Post Engagement Extractor

Collect public X profiles and posts without login, cookies, developer keys or API tokens. The actor returns a profile row, post rows with engagement and media, and explicit status rows when X limits or hides something.

## What it collects

- **Profile header** from the public profile page: handle, display name, bio, bio links and emails, location, website, join date, follower/following/post/media/like counters, verification type, avatar, banner, public birth date, pinned post and professional label.
- **Latest posts** from the profile's server-rendered originals timeline, strictly newest first, topped up through the cursor-paged timeline when the target is higher than the 5-9 server-rendered rows. A pinned post is marked `isPinned` but stays in its chronological position (and may exceed the cap by one).
- **Top posts** ranked by total engagement. X exposes no public Top tab to logged-out callers, so the actor combines the guest search Top product with the profile timeline candidate pool and ranks the merged set locally; a pinned post is not promoted above its earned rank.
- **Media posts** by filtering the collected timelines to photos, videos and GIFs. X does not serve a full media tab to logged-out callers. Filter-heavy runs page the timeline until the requested number of matching rows is found or the source ceiling is reached, so rare GIF matches are not missed by a fixed buffer.
- **Replies and Highlights** as best-effort groups. Highlights are cursor-paged through the legacy guest query, so large curated sets return their full observed depth; replies remain limited. X sometimes refuses those guest timelines; the actor reports `repliesLimited` or `highlightsLimited` instead of pretending the account has none.
- **Specific post URLs** through `postUrls`: the focal post plus up to three server-rendered replies per URL.
- **Derived activity metrics** on profile rows: account age, followers/following ratio, posts per day, last post date, days since the last post, recent average likes/replies/reposts/views and a recent engagement percentage.
- **Provenance and timestamps** on every row: `type`, `recordType`, `sourceUrl`, `collectedAt` and `scrapedAt`.

The actor never signs in, never asks for cookies and never uses a user-supplied token.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `usernames` | array | – | Optional; supply this, `postUrls`, or both. Handles (`NASA`, `@NASA`), profile links (`https://x.com/NASA`), numeric ids (`11348282`, `id:11348282`) or `https://x.com/i/user/11348282`. |
| `include` | multi-select | `["profileInfo", "latestPosts"]` | `profileInfo`, `latestPosts`, `topPosts`, `media`, `replies`, `highlights`; legacy `about` is accepted but reported as unavailable. Groups are additive. |
| `postUrls` | array | `[]` | Exact post URLs or ids; can run alone or alongside profiles. Each returns the focal post and up to 3 replies. |
| `maxPostsPerProfile` | integer 1-1000 | `50` | Post target per account. The actor follows X's guest timeline bottom cursor (X's own ceiling is about 3,200 posts). When a target is still unmet, older posts are filled from search windows only when X serves them. |
| `includeReplies` | boolean | `false` | Keep replies the account sent (best effort). |
| `includeRetweets` | boolean | `false` | Keep reposts. |
| `includeHighlights` | boolean | `false` | Also collect the Highlights tab. Cursor-paged up to `maxPostsPerProfile`; observed depths include 113, 287 and 1,097 rows on different accounts. |
| `dateFrom`, `dateTo` | date picker | – | Client-side post date window. `dateTo` includes the whole day. |
| `language` | text | – | Post language, e.g. `en`, `es`, `ja`. Locale forms such as `en-US` and `pt-BR` are normalized to `en`/`pt` in code, so old tasks keep working. |
| `minimumLikes`, `minimumRetweets`, `minimumReplies`, `minimumViews`, `minimumQuotes` | integer ≥ 0 | – | Client-side engagement minimums. Posts missing the requested count are dropped when the minimum is set. |
| `onlyWithMedia` | boolean | `false` | Keep only posts with photos, videos or GIFs. |
| `mediaType` | select | `any` | `any`, `photos`, `videos`, `gifs`. |
| `onlyVerified` | boolean | `false` | Skip accounts without a verification badge. |
| `verifiedType` | select | `any` | `any`, `blue`, `business`, `government`. X and mirror labels are normalized in code. |
| `minFollowers`, `maxFollowers` | integer ≥ 0 | `0` | Account-level follower range. `0` means any. |
| `minAccountAgeDays` | integer ≥ 0 | `0` | Skip accounts younger than this. Accounts without a public join date are skipped when set. |
| `withWebsiteOnly` | boolean | `false` | Skip accounts with no website in the profile or bio. |
| `bioKeywords` | array | `[]` | Keep accounts whose name or bio contains every keyword (case-insensitive). |
| `activeWithinDays` | integer ≥ 0 | `0` | Skip accounts whose newest public post is older than this. |
| `enrichEngagement` | boolean | `true` | Refresh each collected post through its public status page for views, bookmarks and complete media. One request per post; turn off for the cheapest profile-only runs. |
| `proxyConfiguration` | proxy | – | Optional override. The actor works without a proxy and tries the direct connection first. |

### Examples

Profile only (the daily prefill shape):

```json
{
  "usernames": ["NASA"],
  "include": ["profileInfo"],
  "maxPostsPerProfile": 3,
  "enrichEngagement": false
}
```

Profile plus latest and top posts:

```json
{
  "usernames": ["NASA", "https://x.com/apify"],
  "include": ["profileInfo", "latestPosts", "topPosts"],
  "maxPostsPerProfile": 100
}
```

High-engagement photo posts from a date range:

```json
{
  "usernames": ["NASA"],
  "include": ["latestPosts"],
  "mediaType": "photos",
  "minimumLikes": 5000,
  "minimumViews": 1000000,
  "dateFrom": "2026-01-01",
  "dateTo": "2026-10-27"
}
```

Lead-gen profile filter:

```json
{
  "usernames": ["apify", "NASA"],
  "include": ["profileInfo"],
  "minFollowers": 10000,
  "minAccountAgeDays": 365,
  "withWebsiteOnly": true,
  "bioKeywords": ["space"]
}
```

Specific posts:

```json
{
  "usernames": ["NASA"],
  "include": ["profileInfo"],
  "postUrls": ["https://x.com/NASA/status/2114801524358406570"]
}
```

## Output

Every row has `type` (`profile`, `post` or `status`), `recordType`, `collectedAt` and `scrapedAt`. Profile and post rows, and status rows with a known account or post URL, also carry `sourceUrl`. Empty fields are omitted recursively: the dataset never contains `null`, `""`, `[]` or `{}`.

### Profile row

Keeps the original fields: `id`, `username`, `name`, `bio`, `bioLinks`, `bioEmails`, `location`, `website`, `joinedAt`, `birthDate`, `followers`, `following`, `postCount`, `mediaCount`, `likesGiven`, `listedCount`, `isBlueVerified`, `verified`, `verifiedType`, `label`, `isProtected`, `avatarUrl`, `bannerUrl`, `pinnedPostId`, `pinnedTweetId`, `pinnedTweet`, `mediaTweets`, `withReplies`, `profileStatus`, `collectedAt`.

Adds: `profileUrl`, `websiteDisplayUrl`, `bioMentions`, `accountAgeDays`, `followersToFollowingRatio`, `postsPerDay`, `lastPostAt`, `daysSinceLastPost`, `recentAvgLikes`, `recentAvgReplies`, `recentAvgReposts`, `recentAvgViews`, `recentEngagementRatePct`, `professionalType`, `professionalCategory`, `affiliateLabel`, `highlightCount`, `recordType`, `sourceUrl`, `scrapedAt`.

`websiteDisplayUrl` is the label X shows for the profile's website entity (for example `nasa.gov`). Bio links stay in `bioLinks` and are never reused as the website label.

Conditional fields are omitted when X does not expose them. `listedCount` is not guaranteed by current cookieless payloads.

### Post row

Keeps the original fields: `id`, `url`, `text`, `createdAt`, `language`, `replyCount`, `retweetCount`, `likeCount`, `quoteCount`, `bookmarkCount`, `viewCount`, `engagementRate`, `isReply`, `isRetweet`, `isQuote`, `isNoteTweet`, `isPinned`, `conversationId`, `threadRootId`, `threadPosition`, `inReplyToTweetId`, `inReplyToUserId`, `inReplyToUsername`, `hashtags`, `mentions`, `urls`, `cashtags`, `media`, `quotedTweet`, `quotedTweetId`, `poll`, `card`, `possiblySensitive`, `place`, `postedFrom`, `withheldInCountries`, `isEdited`, `editControl`, `newsActionType`, `parentTweet`, `author`, `username`, `collectedAt`.

Adds: `totalEngagement`, `engagementPerView`, `mediaTypes`, `source`, `isHighlight`, `authorId`, `authorUsername`, `authorName`, `recordType`, `sourceUrl`, `scrapedAt`.

`source` is provenance: `profileLatest`, `profileTop`, `profileHighlight`, `profileReplies`, `syndication`, `search` or `status`.

`conversationId` and `threadRootId` are set on `postUrls` replies from the focal post when the status page omits them, so every reply can be grouped by conversation.

`totalEngagement` is emitted only when likes, reposts, replies and quotes are all real numbers. `engagementPerView` additionally needs a positive view count. No count is invented.

**Media item:** `type` (`photo` / `video` / `gif`), `url`, `previewImageUrl`, `width`, `height`, `durationSeconds`, `viewCount`, `altText`, `variants`, and where X provides them `mediaKey`, `allowDownload`, `mediaAvailability`, `focusRects`. Video `url` prefers the best MP4 at or below 1080p; the full variant list (including 4K) remains in `variants`.

### Status row

Status rows explain a skipped, protected, missing, empty or limited account:

| Status | Meaning |
|---|---|
| `noInput` | No usable usernames or post URLs were supplied. |
| `invalidUsername` | A username/link/id could not be parsed. |
| `notFound` | The account does not exist, was removed or is suspended. |
| `rateLimited` | X temporarily limited the profile request. |
| `skipped` | An account-level filter excluded the account. The message names the filter. |
| `protected` | The account is protected; only its public header is returned. |
| `repliesLimited` | Replies were requested but X served none or fewer than the target this run; `achieved` and `target` are included. |
| `highlightsLimited` | Highlights were requested but X returned no rows or refused the request this run. |
| `noMediaPosts` | Media mode found no matching photos, videos or GIFs. |
| `noPosts` | Posts were collected but every one was filtered out. |
| `noVisiblePosts` | The account exists but X shows no public posts. |
| `timelineUnavailable` | The profile loaded but its posts could not be collected. |
| `searchLimited` | Fewer posts than requested were available; `achieved` and `target` are included. |
| `aboutUnavailable` | A legacy task requested X's login-only About panel. |
| `error` | An unexpected per-profile failure. |

## Data source and limits

- **Primary:** the public profile HTML, including X's server-rendered `GraphQLRequestStream.Completed` payload. This is the same page any logged-out visitor sees.
- **Fallbacks:** guest GraphQL (`UserByScreenName` header, cursor-paged `UserTweets` ranked timeline, Highlights), the syndication timeline, and the public FxTwitter mirror. Guest `UserByScreenName` is merged before FxTwitter; FxTwitter is a third-party mirror and remains the last resort for post views or a missing header field.
- **No credentials:** no cookies, login, API key or user proxy is required.
- **Proxy:** the actor tries a direct connection first, then the Apify AUTO datacenter tier after a real block. A paid residential tier is hardcoded as a last resort and is never a schema default. A user-supplied `proxyConfiguration` overrides the built-in ladder.

### Honest limits

- **About panel:** login-only. The legacy `about` value remains in the `include` enum for saved-task compatibility and is labeled as unavailable; requesting it emits an `aboutUnavailable` status instead of failing the task.
- **Full replies:** X does not serve the full reply tab to logged-out callers, and the guest reply timeline/search refuses most attempts. Replies remain best effort and report `repliesLimited` when empty; use `postUrls` for a focal post plus up to three server-rendered replies.
- **Full media tab:** X's `/media` route is a login wall for guests and the guest `UserMedia` operation returns 404. Media mode filters the collected timelines instead; cursor pagination can now collect far more media posts than the old one-page path.
- **Deep history:** the guest `UserTweets` bottom cursor pages a profile timeline back to X's ceiling of about 3,200 posts, and `maxPostsPerProfile` supports 1-1000. Guest search is not reliable, so older-row top-ups beyond the cursor are best effort.
- **Highlights:** the old `userId` Highlights query pages the curated set through its bottom cursor, not a fixed 20-row page. Observed depths include 113 (second-opinion sample), 287 (NASA) and 1,097 (elonmusk), bounded by the account's Highlights set and `maxPostsPerProfile`. The live `screenName` query remains a one-page fallback.
- **Syndication quota:** about 30 profile timeline lookups per IP per 15 minutes. The actor falls back to guest GraphQL and FxTwitter instead of retrying forever.
- **`listedCount`:** best effort only. Syndication returns a placeholder `0` and that value is never published; only a search author snapshot carries the real count, and guest search itself is limited.
- **`postedFrom`, `place`:** conditional. `postedFrom` is filled when the timeline row carries a top-level `source`; `place` is not exposed by current cookieless payloads and is omitted.
- **Views:** recent posts get views from the status page; tweets from before X introduced view counts have no view count anywhere.
- **4K video:** the 4K MP4 can be hundreds of megabytes. `media.url` prefers 1080p or lower; the 4K URL stays in `variants`.

## FAQ

**Do I need an X account or developer key?** No. The actor only reads public pages and needs no credential input.

**Why are there fewer posts than `maxPostsPerProfile`?** The account may have fewer public posts in the reachable timeline, the filters may remove rows, or X may refuse the guest search top-up. The actor merges and cursor-pages every public source, then reports `searchLimited` with the achieved count only when a real source cap leaves the target unmet.

**Why is a count missing instead of `0`?** A missing field means X did not expose it. The actor never substitutes a sentinel or an invented zero. A real zero (for example `quoteCount: 0`) is preserved.

**Why did my account get a `skipped` row?** An account-level filter (`onlyVerified`, `verifiedType`, follower range, account age, website, bio keywords or `activeWithinDays`) excluded it. The message says which one.

**Can I collect protected accounts?** Only their public header. Posts require approval from the account owner, which the actor does not attempt.

**Is the data live?** Yes. Every run reads X at request time; schedule the actor for hourly, daily or weekly refreshes.

**How do I use the dataset?** Use the run page, the Apify API, webhooks, or a no-code connector such as Zapier, Make or Google Sheets.

**Is this affiliated with X?** No. It is an independent third-party actor that reads publicly available pages.

## Development

Run the offline tests from the actor folder:

```bash
python -m pytest tests/ -q
```

Run locally with the Apify CLI:

```bash
apify run --purge --input-file input.json
```
