# Facebook Timeline Posts & Reel Transcript Extractor

Turn any public Facebook Page or Profile into a clean, spreadsheet-ready feed of its posts, or look up individual posts, reels and videos straight from their links. Every record carries the post text, the author, reaction counts split by type, comment and share totals, play counts for videos and reels, photo and video files, link-card details, and, when you ask for them, the full comment threads and Facebook's own reel and video captions. You don't need a Facebook account, cookies or any proxy setup.

## What this actor does

- **Reads whole timelines, not only the first screen.** Collect a few posts or thousands from each Page or Profile, newest first. Narrow them down with a date window, content types (reels, albums, links, shared posts and more), or minimum reactions and comments.
- **Opens almost any Facebook link.** Post, reel, video, watch, photo, `permalink.php`, `story.php`, mobile, public group post and share links (`facebook.com/share/…`, `fb.watch/…`) each return that one post, so a list of links you collected elsewhere can be enriched in one run.
- **Counts and conversations, included.** Video and reel records include the play count Facebook displays plus its two other view metrics; reactions come per type (Like, Love, Care, Haha, Wow, Sad, Angry and seasonal ones) next to the total. Pick the comment order (most relevant, newest or unfiltered) and optionally include each comment's reply thread, with its author, profile picture, time, reaction count and direct link.
- **Keeps the media usable.** Every photo of an album, link-preview cards, the shared post behind a re-share, and permanent copies of images (videos optional), because Facebook's own media links expire after a few days.
- **Empty fields are omitted.** Fields Facebook doesn't show for a post are left out instead of filled with blanks.

## Output per post

| Field | Description |
|---|---|
| `postId` | Facebook's numeric post ID |
| `permalinkUrl` | Direct link to the post, reel or video |
| `postType` | `photo`, `video`, `reel` or `text` (from the first photo/video; link shares and re-shares are `text`) |
| `contentType` | Finer type: `text`, `photo`, `album`, `video`, `reel`, `link`, `share` or `live` |
| `text` | Full post text |
| `hashtags` | Hashtags in the text |
| `mentions` | Tagged people and Pages: `{id, name, url}` |
| `externalLinks` | Links in the text, as their real destination (not a tracking redirect) |
| `creationTime` / `creationTimeIso` | Publication time as a Unix timestamp and as ISO 8601 (UTC) |
| `backdatedTime` / `backdatedTimeIso` / `backdatedTimeGranularity` | The date the author set for a backdated post (for example a life event in 1985) and how precise it is (`DAY`, `MONTH`, `YEAR`) |
| `author` | `{id, name, url, profilePictureUrl, profileUrlIsFallback}`; the flag is `true` only when Facebook gave no profile link and one was built from the numeric ID |
| `collaborators` | Co-authors of a joint post: `{id, name, url}` |
| `attachments` | Photos (`id`, `url`, `width`, `height`, `accessibilityCaption`) and videos (`videoUrlHd`, `videoUrlSd`, `thumbnailUrl`, `durationMs`, `width`, `height`, `isReel`, `isLive`, `captionsAvailable`, plus `videoTranscript`, `videoTranscriptText`, `videoTranscriptLocale` and `videoTranscriptFormat` when transcripts are requested) |
| `albumPhotoCount` | Total photos in an album post |
| `linkPreview` | Link card: `{url, title, description, source, domain, imageUrl}` |
| `sharedPost` | The original post behind a re-share: `{postId, url, author, creationTime, creationTimeIso, text}`, plus `contentType`, `reactionsTotal`, `commentsCount`, `sharesCount` and `viewsCount` with "Original text of shared posts" |
| `reelAudio` / `remix` | Reels with "Reel audio and remix details": `{title, type, id, albumArtUrl, isOriginalAudio}` and `{isRemixable, status}` |
| `musicTitle` | Song used in a reel or video |
| `location` | Place the post was checked in at: `{id, name, url}` |
| `taggedProfiles` | People or Pages tagged with "is with": `{id, name, url}` |
| `reactionsTotal` / `reactionBreakdown` | Total reactions and `[{type, count}]` per reaction type |
| `commentsCount` / `sharesCount` | Totals as shown by Facebook |
| `viewsCount` | Plays shown on the video or reel (the "views" number on Facebook) |
| `videoViewCount` / `videoPostViewCount` | Facebook's two other view metrics for videos and reels |
| `feedbackId` | Facebook's engagement ID for the post, handy for joining with other comment datasets |
| `isAd` | `true` when Facebook marks the post as sponsored |
| `topComments` | Comments shown under the post |
| `allComments` | Full comment list when "Fetch all comments" is on |
| `inputUrl` | The link from your input, normalized |
| `scrapedAt` | When the record was collected (ISO 8601) |
| `recordType` | Always `post` |

**Comment fields** (in `topComments`, `allComments` and `replies`): `commentId`, `commentUrl`, `text`, `author {id, name, url, profilePictureUrl}`, `createdTime`, `createdTimeIso`, `reactionsTotal` (or `reactionsCountText` such as "1.2K" when Facebook only shows a rounded figure), `reactionBreakdown` (per type, exact, with "Reactions by type on comments"), `replyCount`, `depth`, `parentCommentId`, `imageUrl` and `replies`.

**Media copies:** when a file is copied into the run's storage, the field holds the permanent copy and `<field>Original` keeps Facebook's link (for example `url` and `urlOriginal`). Links left on Facebook's servers get `<field>ExpiresAt`, the moment they stop working.

Fields with no value for a given post are left out rather than filled with empty values.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `startUrls` | array | – | **Required.** Page, Profile, post, reel, video, photo, watch or share links, in any mix |
| `maxItems` | integer | `20` | Posts per Page or Profile (1-10,000) |
| `onlyPostsNewerThan` | string | – | Keep timeline posts after a date (`2026-01-01`), ISO timestamp, or period (`7 days`, `3 months`) |
| `onlyPostsOlderThan` | string | – | Keep timeline posts before a date; combine both for a window |
| `contentTypes` | array | all | Keep only `text`, `photo`, `album`, `video`, `reel`, `link`, `share` and/or `live` posts |
| `minReactions` / `minComments` | integer | – | Skip timeline posts below these engagement levels |
| `includeTopComments` | boolean | `true` | Comments shown under each post |
| `fetchAllComments` | boolean | `false` | Full comment lists into `allComments` |
| `maxCommentsPerPost` | integer | `100` | Limit for `allComments` (1-5,000); replies count toward it |
| `commentsSortOrder` | select | `mostRelevant` | `mostRelevant`, `newest` or `all` (unfiltered), in Facebook's own ordering |
| `onlyCommentsNewerThan` | string | – | Keep only comments after a date or period (`1 day`); read newest first |
| `includeCommentReplies` | boolean | `false` | Reply threads inside each comment |
| `includeCommentReactions` | boolean | `false` | Each comment's reactions by type with exact totals |
| `fetchVideoCaptions` | boolean | `false` | Facebook's caption files as transcripts |
| `fetchReelDetails` | boolean | `false` | Reel audio track and remix setting |
| `fetchSharedPostDetails` | boolean | `false` | Text and counters of the original behind each re-share |
| `fetchAllAlbumPhotos` | boolean | `false` | Every photo of album posts (the timeline shows up to five) |
| `rehostMedia` | select | `images` | `images`, `imagesAndVideos` or `none` |

Date, content-type and engagement filters apply to Page and Profile links. A direct post link always returns its post.

### Example: last 30 days of a brand's reels, with transcripts

```json
{
  "startUrls": [{ "url": "https://www.facebook.com/nike" }],
  "maxItems": 100,
  "onlyPostsNewerThan": "30 days",
  "contentTypes": ["reel"],
  "fetchVideoCaptions": true
}
```

### Example: a news Page's most discussed posts in a fixed window

```json
{
  "startUrls": [{ "url": "https://www.facebook.com/nytimes" }],
  "maxItems": 50,
  "onlyPostsNewerThan": "2026-09-01",
  "onlyPostsOlderThan": "2026-10-01",
  "minComments": 500
}
```

### Example: enrich a list of post and reel links with full, newest-first comment threads

```json
{
  "startUrls": [
    { "url": "https://www.facebook.com/pepsi/posts/1054998311204476" },
    { "url": "https://www.facebook.com/reel/2995026330636892/" },
    { "url": "https://fb.watch/72TEK5emY-/" }
  ],
  "fetchAllComments": true,
  "commentsSortOrder": "newest",
  "includeCommentReplies": true,
  "maxCommentsPerPost": 500
}
```

### Example: archive a club's photo albums with permanent image copies

```json
{
  "startUrls": [{ "url": "https://www.facebook.com/fcbarcelona" }],
  "maxItems": 40,
  "contentTypes": ["album", "photo"],
  "fetchAllAlbumPhotos": true,
  "rehostMedia": "images"
}
```

## Use cases

- **Competitor and brand tracking:** chart posting cadence, formats and reactions by type for any set of Pages.
- **Reel and video performance reports:** compare play counts across creators, and read what was said through the caption transcripts.
- **Audience research:** collect entire comment threads, replies included, for sentiment or topic analysis.
- **Newsroom and fact-check work:** freeze a viral post's text, media, counters and discussion at a known moment.
- **Content archiving:** keep album photos and media copies that still open after Facebook's links expire.
- **Lead and partner discovery:** find who comments on, collaborates with, or is re-shared by a Page.

## FAQ

**Do I need a Facebook login, cookies or a proxy?**
No. The actor reads only what Facebook shows to logged-out visitors and picks its connection method automatically. There is nothing to configure.

**How many posts can I get from one Page?**
As many as Facebook publicly lists, up to 10,000 per link per run. Some Pages and personal profiles show only a handful of posts to everyone, logged in or not. In that case the run stops when the timeline ends and the status message says so.

**Why did a link return no post?**
The status message names every link that produced nothing and why: removed or private content (including videos Facebook hides from logged-out visitors), links that aren't posts or Pages (group feeds, events, Marketplace), or a page that Facebook restricts in some countries. Region-restricted pages show "not available in <country>" and are reported as such instead of being retried.

**Are video view counts exact?**
Yes. `viewsCount` is the full integer behind the rounded number Facebook displays (for example 422,708 behind "422K"). Photo, text and link posts have no public view count, so the field is left out for them.

**Is the transcript AI-generated?**
No. It is the caption file Facebook created or the uploader added. Roughly a third of videos have one, in many languages, and English is preferred when available. Videos without captions simply have no transcript.

**Why do some comment reactions read "1.2K"?**
Next to each comment, Facebook only shows a rounded figure for busy comments, and that is what `reactionsCountText` keeps. Turn on "Reactions by type on comments" to get the exact total and the split by reaction type for every comment.

**Do the photo and video links keep working?**
Facebook's media links expire after one to five days. By default every post image (photos, video thumbnails, link pictures and the author's picture) is copied into the run's storage and the copy is what you receive, with Facebook's original kept beside it. Choose `imagesAndVideos` to copy videos too, or `none` to keep only Facebook's links, each with its expiry time. Profile pictures inside comments always stay on Facebook's servers, so download them soon after the run if you need them.

**Can I monitor a Page on a schedule?**
Yes. Schedule the actor with "Only posts newer than" set to the schedule interval (for example `1 day`) to receive only the new posts each time.

**What can't this actor collect?**
These limits come from what Facebook shows to logged-out visitors:
- Some Pages and personal profiles show only a few posts to everyone, logged in or not. The run stops when that public timeline ends.
- Pages restricted in the country of the connection are reported as "not available in <country>".
- Videos hidden from logged-out visitors are reported as unavailable.
- Live viewer counts and a post's edit history aren't shown to logged-out visitors.
- Authors of group posts and some commenters appear with a masked ID and no profile link, because Facebook hides them from the public.
- Some link previews carry no description, because the linked site doesn't provide one.
- Album videos beyond the first five are listed with their ID and thumbnail. Open the video's own link for the playable file.
- Reels come from the Page's timeline, which includes the reels a Page posts; filter them with "Content types: Reel".
- A post that Facebook adds to a timeline after your run, with an earlier timestamp, appears only in the next run. When scheduling, let "Only posts newer than" overlap the previous run a little (for example `2 days` for a daily schedule).
- Facebook shows slightly different posts to different visitors and connections. A run can occasionally omit a post that another visitor sees at the same moment, most often near the top of a timeline; a later run usually returns it. The run stays newest-first and reports exactly what its connection was shown.

**Is this affiliated with Facebook or Meta?**
No. It is an independent tool that reads publicly available Facebook pages. It is not endorsed by or connected to Meta Platforms, Inc.
