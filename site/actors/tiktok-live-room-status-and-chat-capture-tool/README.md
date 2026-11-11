# TikTok LIVE Room Status & Event Capture

Check whether TikTok creators are live right now and export the room's title, viewer counters, playback URLs, host profile and audience stats — or attach to a live room and capture its chat, gifts, likes, follows, joins and viewer-count updates as they happen.

Everything works **cookielessly**. There is no login step, no cookie to paste, no API key and no proxy setup.

## What this actor does

- **Room status mode (default):** one row per creator. Live creators get the full room snapshot; offline creators get a clearly labelled status row when "Include offline creators" is on.
- **Live events mode:** attaches to a live room's public event stream and pushes one row per chat message, gift, like, follow, join or viewer-count update.
- **Trustworthy live detection:** TikTok keeps serving an ended room's title, playback URLs and viewer numbers, sometimes for months. This actor checks the room's live status code and the real-time `check_alive` endpoint, so an ended stream is not reported as live.
- **Signed playback URLs:** HLS and FLV links at every quality TikTok exposes (both standard and HEVC stream data are merged), plus the earliest signature expiry when it can be parsed.
- **No credentials, no paid proxy:** a direct connection is tried first, then the free Apify datacenter pool. No residential proxy, no third-party proxy, no user-supplied cookie.

## Modes

### Room status (default)

One row per supplied creator:

- **Live:** `isLive: true`, `status: "live"`, room id, title, start time, live duration, current/total viewers, likes, shares, comments, follows, gift viewers, stream URLs and their expiry, cover images, host profile and follower stats.
- **Offline:** `isLive: false`, `status: "offline"`, the public profile (bio, avatar, follower/following/heart/video counts, bio link) and the most recent stream's title/start time when TikTok still exposes it. Viewer counters are deliberately omitted for offline creators.
- **Not found:** `status: "notFound"` when TikTok has no such account. `isLive` is omitted because the actor has no live evidence either way.
- **Unavailable:** `status: "unavailable"` with a short `error` when TikTok returns a bot check or an unreadable answer. This is never reported as offline, and `isLive` is omitted.

### Live events

Attaches to one live room at a time and emits events until `connectionDuration` seconds or `eventCap` events. Event types: `chat`, `gift`, `like`, `follow`, `share`, `join`, `stats`, and `other` for TikTok message types that do not map to a named category. Replayed messages are deduplicated by message id.

Live events are ephemeral: TikTok exposes no chat history, so you only receive what arrives while the actor is attached.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `roomStatus` | `roomStatus` (one row per creator) or `liveEvents` (real-time events) |
| `usernames` | array | prefill `["natgeo"]` | Bare handles, `@handles`, profile URLs or LIVE URLs |
| `liveUrls` | array | – | Direct TikTok URLs; merged with `usernames` |
| `includeOffline` | boolean | `false` (prefill `true`) | Emit a status row for offline/not-found/unavailable creators. Ignored in live-events mode |
| `includeStreamUrls` | boolean | `true` | Add HLS/FLV playback URLs and their expiry for live creators (room-status mode) |
| `connectionDuration` | integer | `60` (prefill `10`) | Seconds to stay attached per live room, in live-events mode |
| `eventCap` | integer | `500` (prefill `100`) | Stop after this many events per stream, in live-events mode |
| `eventTypes` | multi-select | `["all"]` | Which event categories to keep |

### Example: check a watchlist

```json
{
  "mode": "roomStatus",
  "usernames": ["natgeo", "bbcnews", "cnn"],
  "includeOffline": true,
  "includeStreamUrls": true
}
```

### Example: capture a stream's chat and gifts

```json
{
  "mode": "liveEvents",
  "usernames": ["creator_handle"],
  "connectionDuration": 120,
  "eventCap": 1000,
  "eventTypes": ["chat", "gift", "stats"]
}
```

### Example: mix handles and URLs

```json
{
  "mode": "roomStatus",
  "usernames": ["@natgeo"],
  "liveUrls": ["https://www.tiktok.com/@tiktok/live"]
}
```

## Output per room-status row

- `recordType`, `isLive`, `status`
- `roomId`, `liveUrl`, `sourceUrl`
- `liveTitle`, `liveStatus`, `liveRoomMode`
- `startTime`, `startedAt`, `liveDurationSeconds`
- `totalViewers`, `currentViewers`
- `likeCount`, `diggCount`, `shareCount`, `commentCount`, `followCount`, `giftUvCount`, `watchUserCount`, `roomFollowCount`, `totalUser`
- `coverUrl`, `squareCoverUrl`, `hashtagId`, `gameTagId`, `isPaidEvent`, `isSubscriberOnly`, `streamId`
- `streamUrls`, `streamUrlExpiresAt`
- `hostUsername`, `hostUserId`, `hostSecUid`, `hostDisplayName`, `hostVerified`, `hostBio`, `hostBioLink`, `hostAvatarUrl`, `hostFollowerCount`, `hostFollowingCount`, `hostHeartCount`, `hostVideoCount`, `hostPrivateAccount`, `hostIsOrganization`, `hostLanguage`
- Offline-only: `lastLiveTitle`, `lastLiveStartTime`, `lastLiveStartedAt`, `lastLiveStatus`
- `checkAlive` when TikTok answered the real-time check
- `scrapedAt`

Missing values are omitted, never filled with `null`, empty strings or placeholders.

## Output per live-event row

- `recordType`, `isLive`, `status`, `roomId`, `hostUsername`, `liveUrl`, `sourceUrl`
- `eventType`, `receivedAt`, `eventTimestamp`, `msgId`
- `user`: `id`, `secUid`, `username`, `displayName`, `avatarUrl`, `verified`
- `payload`:
  - chat: `text`, `emotes`, `contentLanguage`
  - gift: `giftName`, `giftId`, `giftCount`, `giftDiamondCount`, `giftTotalDiamonds`, `repeatEnd`
  - like: `likeCount`, `totalLikes`
  - stats: `viewerCount`
  - join: `actionId`
  - follow/share: `action`, `shareType`, `shareTarget`, `shareCount`, `followCount` (the last two are cumulative room/host counters reported with the event)
  - other: `rawMethod`, `payloadSize`
- `scrapedAt`

## Use cases

- **Go-live alerts:** poll a creator roster and diff `isLive` between runs.
- **Audience snapshots:** compare viewer counts, likes, shares, follows and gift activity across streams.
- **Creator research:** keep a current record of who is live, under what title, and with how many viewers.
- **Community management:** capture your own stream's chat and gifts for moderation or a highlight reel.
- **Live-commerce research:** follow a set of sellers and record their stream metadata over time.

## FAQ

**Do I need a TikTok account or cookie?**
No. Room status and live events are read from the same public surfaces any logged-out viewer sees. Authentication is only required to *post* messages, which this actor never does.

**Why did a creator come back as offline even though their page shows a room title?**
TikTok keeps the previous room's metadata after a stream ends. The actor checks the room's live status and the real-time `check_alive` endpoint; if neither confirms a broadcast, the creator is reported as offline with `lastLive*` fields for the ended room.

**What happens when a creator isn't live?**
With "Include offline creators" on, you get one status row with their public profile. With it off, the creator is skipped — the old behaviour. In live-events mode an offline creator produces no event rows and a clear log line.

**Do the stream URLs keep working?**
They are signed by TikTok and expire. The actor emits `streamUrlExpiresAt` when it can parse the signature's expiry. Re-run for fresh links.

**Can I capture chat history?**
No. TikTok exposes no endpoint for past chat messages. Live-events mode captures what arrives while it is attached.

**Are events region-dependent?**
Yes. TikTok's live rooms and viewer counts are relative to the connection's region. If a room is region-restricted, the actor reports it as `unavailable` rather than guessing.

**Can I monitor many creators in one run?**
Yes. In room-status mode each creator is checked in turn and gets one row. In live-events mode each live creator is captured for `connectionDuration` seconds, so total runtime grows with the list.

**Does this actor discover live streams by keyword or record video?**
No. It is a creator-status and event-capture actor. Keyword/category discovery, rankings, top-gifter leaderboards and recording are separate jobs and are not part of this actor.

**Is this affiliated with TikTok?**
No. It is an independent third-party tool that reads public LIVE data. Use it only for public data and in line with TikTok's terms and applicable law.

## Limitations

- Chat history does not exist upstream; live events are only what arrives while attached.
- Playback, cover and avatar URLs are signed and expire. Some CDNs reject HTTP `HEAD` probes; playback itself works with a normal media request.
- Engagement counters (likes, shares, comments, follows, gift viewers) come from TikTok's room-enter response. A region-restricted room can withhold that response; the counters are then omitted rather than fabricated.
- Some rooms are region-restricted; the actor labels them `unavailable` instead of inventing data.
- Private accounts, private analytics, sending messages, recording and keyword discovery are out of scope.
- TikTok can change its internal page state or Webcast protocol without notice. The actor fails soft (status rows/log lines) rather than fabricating fields.

## Data source

Public TikTok LIVE pages (`/@creator/live`), public profile pages, the real-time room `check_alive` endpoint, and the public Webcast event stream. No account, cookie, API key or proxy input is used.
