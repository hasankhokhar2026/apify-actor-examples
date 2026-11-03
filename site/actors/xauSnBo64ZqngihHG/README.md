# SoundCloud Charts, Search & Artist Catalog Scraper

Pull structured data straight from [SoundCloud](https://soundcloud.com): genre charts, keyword search across tracks/users/playlists/albums, a full artist catalog, or any track/playlist/profile URL you already have. No SoundCloud account or API key needed.

## What this actor does

- Browses genre charts — most-played of all time or currently trending, across 30+ genres
- Searches by keyword for tracks, users, playlists, or albums
- Pulls every track from one artist's public profile
- Resolves a list of SoundCloud track/playlist/user URLs directly to structured records
- Empty fields are omitted from records rather than returned as blanks

## Output per record

Each record is a track, a user/artist profile, or a playlist, distinguished by `recordType`.

- `title` — track title, artist/username, or playlist title
- `url` — the canonical SoundCloud page URL
- `trackId` — SoundCloud's internal numeric ID
- `artist`, `artistUrl` — uploader's name and profile URL (tracks and playlists)
- `duration` — length as `MM:SS` or `HH:MM:SS` (tracks and playlists)
- `playCount` — total plays (tracks and users)
- `likeCount` — likes/favorites (tracks, users, playlists)
- `repostCount` — reposts (tracks, users, playlists)
- `commentCount` — comments (tracks only)
- `genre` — genre label (tracks and playlists)
- `tags` — array of tags attached by the uploader (tracks only)
- `uploadDate` — ISO 8601 date the item was created
- `lastModified` — ISO 8601 date the track was last edited, when SoundCloud reports one (tracks only)
- `streamUrl` — SoundCloud's own transcoding/stream endpoint for the track (tracks only) — see FAQ
- `artworkUrl` — artwork/avatar image URL at 500×500
- `waveformUrl` — waveform image URL (tracks only)
- `description` — track or profile description, when the uploader wrote one
- `recordType` — `track`, `user`, or `playlist`
- `scrapedAt` — ISO 8601 timestamp of the request

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `charts` | `charts` / `search` / `artistTracks` / `byUrl` |
| `chartKind` | string | `top` | `top` (most-played of all time) or `trending` (mode=charts) |
| `genre` | string | `soundcloud:genres:all-music` | Genre filter for charts and search |
| `searchQuery` | string | `chill lofi` | Search keyword (mode=search) |
| `searchKind` | string | `tracks` | What to search: tracks, users, playlists, or albums (mode=search) |
| `artistUrl` | string | – | SoundCloud artist profile URL (mode=artistTracks) |
| `startUrls` | array | `[]` | SoundCloud track/playlist/user URLs to resolve directly (mode=byUrl) |
| `maxItems` | integer | `20` | Maximum records to return (1–500) |

Genres available for `genre`: All Music, Alternative Rock, Ambient, Classical, Country, Dance & EDM, Dancehall, Deep House, Disco, Drum & Bass, Dubstep, Electronic, Folk & Singer-Songwriter, Hip-hop & Rap, House, Indie, Jazz & Blues, Latin, Metal, Piano, Pop, R&B & Soul, Reggae, Reggaeton, Rock, Soundtrack, Techno, Trance, Trap, Trip Hop, World.

### Example: trending electronic chart

```json
{
  "mode": "charts",
  "chartKind": "trending",
  "genre": "electronic",
  "maxItems": 50
}
```

### Example: search for playlists by keyword

```json
{
  "mode": "search",
  "searchQuery": "lofi study beats",
  "searchKind": "playlists",
  "maxItems": 30
}
```

### Example: an artist's full catalog

```json
{
  "mode": "artistTracks",
  "artistUrl": "https://soundcloud.com/lofi_producer",
  "maxItems": 200
}
```

### Example: resolve specific URLs

```json
{
  "mode": "byUrl",
  "startUrls": [
    "https://soundcloud.com/artist/chill-lofi-beat",
    "https://soundcloud.com/lofi_producer"
  ]
}
```

## Use cases

- **Music discovery** — pull genre charts to see what's rising without opening SoundCloud
- **Artist research** — build a complete, current discography for any public profile
- **Playlist curation** — source track metadata (genre, tags, duration) for building new playlists
- **Catalog monitoring** — re-run `artistTracks` on a schedule to catch new uploads
- **Analytics dashboards** — track play/like/repost counts for a set of tracks over time

## FAQ

**Do I need a SoundCloud account to use this?**  No — every mode reads SoundCloud's public pages and public API; no login or API key is required.

**What's the difference between `top` and `trending` charts?**  `top` ranks the most-played tracks of all time in a genre; `trending` ranks tracks currently gaining traction, which changes day to day.

**Can I get the actual audio file?**  The `streamUrl` field points at SoundCloud's own stream endpoint for the track. Whether a given track can actually be played/downloaded from it still depends on the streaming permissions the artist set on SoundCloud.

**Why is `playCount` or `commentCount` missing from some tracks?**  Those fields are only included when SoundCloud's own data for the track includes a value; very new or low-visibility tracks sometimes don't carry one.

**Why do playlist records have `genre` but not `commentCount` or `tags`?**  SoundCloud's playlist objects simply don't carry per-track stats like comment counts or a track's own tags, so this actor doesn't invent values for fields SoundCloud never returns there.

**How many records can one run return?**  Up to `maxItems`, capped at 500. For a bigger pull, split the work across multiple runs with different genres, search terms, or artists.

**Can this reach private or unlisted tracks?**  No — only tracks, playlists, and profiles that are publicly visible on soundcloud.com without logging in are accessible.

**Is this affiliated with SoundCloud?**  No. This is an independent actor that reads SoundCloud's publicly available pages and is not affiliated with or endorsed by SoundCloud.
