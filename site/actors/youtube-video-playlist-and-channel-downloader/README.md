# YouTube Video, Playlist & Channel Downloader with Metadata

Inspect or download YouTube videos from a direct link, a playlist, a channel, or a search phrase in one run. Every row carries the video's metadata, and download rows add a readable file link, the real container and codec, the requested and delivered quality, captions, and an optional transcript.

Use this actor only for content you own or are authorized to download. YouTube's Terms of Service may prohibit downloading content without permission, and you are responsible for complying with them. This actor is not affiliated with YouTube or Google, and it does not bypass DRM, private-video access, or geographic restrictions.

## What this actor does

- **Four input paths:** direct video URLs, playlists, channels, and keyword search
- **Metadata, download, or subtitles:** choose what each run returns
- **Compatible video:** SDR 360p-1080p H.264/AAC MP4 when YouTube provides it
- **Opt-in 4K:** 1440p/2160p SDR with a 10-minute and 1000 MB cap
- **Audio passthrough:** M4A (AAC) or Opus, without a fake bitrate uplift
- **Captions and transcript:** WebVTT, SubRip, or plain text
- **Honest failures:** rows explain private, live, DRM, geo-blocked, oversized, and unavailable videos
- **Empty fields are omitted** — records only contain values that are actually populated

## Output per video

- `record_type` — `video`, `failure`, or `input_error`
- `video_url`, `video_id`, `title`, `description`
- `uploader`, `uploader_id`, `uploader_url`, `channel_id`
- `upload_date`, `duration_seconds`
- `view_count`, `like_count`, `comment_count`
- `thumbnail`, `tags[]`, `categories[]`, `is_live`
- `playlist_index` — position inside a playlist, channel listing, or search result
- `source_label` — `direct`, `playlist:...`, `channel:...`, or `search:...`
- `download_status` — `success`, `metadata_only`, `subtitles_only`, `failed`, `skipped_unsupported`, or `upload_failed`
- `failure_code` — e.g. `private`, `removed`, `live_unsupported`, `drm_unsupported`, `geo_blocked`, `bot_check`, `too_long`, `too_large`, `no_formats`, `upload_failed`, `no_captions`, `captions_unavailable`
- `error`, `retryable`
- `requested_quality`, `delivered_quality`, `quality_match`
- `container`, `vcodec`, `acodec`, `dynamic_range`, `is_hdr`
- `width`, `height`, `resolution`, `fps`, `aspect_ratio`, `audio_only`
- `filesize_bytes`, `total_bitrate_kbps`, `checksum_sha256`
- `download_url`, `storage_key`, `storage_mode`, `expires_at`
- `four_k_cap_applied` — present when the 4K duration/size cap governed the row
- `subtitle_files[]`, `subtitle_urls[]`, `subtitle_languages[]`, `caption_kind`
- `caption_status` — `no_captions`, `captions_unavailable`, or `upload_failed` when no caption file was produced
- `transcript` — when transcript output is requested
- `video_meta` — nested technical details for the downloaded file
- `downloaded_at`
- `search_query` — on an input-error row for an empty search result

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `metadata` | `metadata`, `download`, or `subtitles` |
| `videoUrls` | array | — | Direct video, Shorts, replay, `youtu.be` URLs, or 11-character IDs |
| `playlistUrls` | array | — | Playlist URLs |
| `channelUrls` | array | — | Channel URLs, `@handles`, or `UC...` IDs |
| `searchQueries` | array | — | Search phrases |
| `videoQuality` | string | `720p` | `360p`, `480p`, `720p`, `1080p`, `1440p`, `2160p`, or `best` |
| `container` | string | `auto` | `auto`, `mp4`, `webm`, or `mkv` |
| `audioOnly` | boolean | `false` | Download source audio only |
| `audioFormat` | string | `m4a` | `m4a` (AAC) or `opus` |
| `downloadSubtitles` | boolean | `false` | Fetch existing caption tracks |
| `subtitleLanguages` | array | `["en"]` | Language codes to request |
| `subtitleFormat` | string | `vtt` | `vtt` or `srt` |
| `includeTranscript` | boolean | `false` | Add a plain-text transcript |
| `maxVideos` | integer | `10` | Total videos per run (1–50) |
| `maxMinutes` | integer | `30` | Per-video duration cap (1–30) |
| `maxMB` | integer | `500` | Per-video size cap; 4K opt-in allows up to 1000 |
| `allow4K` | boolean | `false` | Enable 1440p/2160p SDR |
| `storage` | string | `ephemeral_kvs` | `ephemeral_kvs`, `named_kvs`, or `s3` |
| `kvsName` | string | — | Named KVS name |
| `storageRetentionDays` | integer | `7` | Presigned S3/R2 link lifetime (1–7 days) |
| `s3Bucket`, `s3Prefix`, `s3Endpoint`, `s3Region` | string | — | S3 or R2 destination |
| `s3AccessKeyId`, `s3SecretAccessKey` | secret | — | Optional S3/R2 credentials |
| `s3PublicBaseUrl` | string | — | Use public bucket URLs instead of presigned links |
| `cookies` | secret | — | Optional Netscape cookies for authorized age-restricted or members-only access |
| `proxyConfiguration` | object | automatic | Optional connection override |

## Examples

### Metadata for one video

```json
{
  "mode": "metadata",
  "videoUrls": ["https://www.youtube.com/watch?v=jNQXAC9IVRw"]
}
```

### Download a 720p MP4

```json
{
  "mode": "download",
  "videoUrls": ["https://www.youtube.com/watch?v=dQw4w9WgXcQ"],
  "videoQuality": "720p",
  "container": "mp4",
  "maxVideos": 1
}
```

### Playlist with captions and transcript

```json
{
  "mode": "download",
  "playlistUrls": ["https://www.youtube.com/playlist?list=PLFgquLnL59alCl_2TQvOiD5Vgm1hCaGSI"],
  "videoQuality": "480p",
  "maxVideos": 5,
  "downloadSubtitles": true,
  "subtitleLanguages": ["en"],
  "subtitleFormat": "srt",
  "includeTranscript": true
}
```

### Search to audio

```json
{
  "mode": "download",
  "searchQueries": ["public domain jazz"],
  "audioOnly": true,
  "audioFormat": "m4a",
  "maxVideos": 3
}
```

### Opt-in 4K SDR

```json
{
  "mode": "download",
  "videoUrls": ["https://www.youtube.com/watch?v=LXb3EKWsInQ"],
  "videoQuality": "2160p",
  "container": "auto",
  "allow4K": true,
  "maxMinutes": 10,
  "maxMB": 1000
}
```

## Use cases

- **Own-channel archiving** — export metadata, captions, and small compatible files for channels you manage
- **Authorized media research** — collect titles, descriptions, dates, and public statistics for analysis
- **Caption workflows** — pull existing VTT or SRT tracks and transcript text for translation or accessibility
- **Audio libraries** — save authorized M4A or Opus audio without re-encoding
- **Content audits** — compare requested and delivered quality, codecs, and file sizes
- **Pipeline integrations** — one row per video with stable status and failure fields

## FAQ

### What can I download with this actor?

Content you own or are authorized to download. The actor does not grant rights to third-party media and does not bypass DRM, private access, or geographic restrictions.

### Does it support live streams?

No. Live and upcoming broadcasts have no finite file and are returned as `live_unsupported` failure rows.

### Can I download age-restricted or members-only videos?

Sometimes, when you have authorized access and supply your own cookies. Public videos work without cookies.

### Does it bypass geo-blocks or DRM?

No. Geo-restricted and DRM-protected videos are reported as failure rows. Changing proxy settings is not a guaranteed workaround.

### Where is the MP3 option?

There is no MP3 option because YouTube does not serve 320 kbps MP3. The actor passes through the source M4A (AAC) or Opus audio track and reports the real codec. Claiming a higher bitrate would only mean re-encoding and inflating the file.

### Why did I get 480p when I asked for 720p?

Not every video has every resolution. The actor delivers the closest available quality at or below your request and sets `quality_match` to `false` when it had to step down.

### Why is my 4K file MKV or WebM instead of MP4?

YouTube usually serves 1440p and 2160p as VP9 or AV1 video, often with Opus audio. Those streams are not H.264/AAC MP4. The actor keeps the real codec and container instead of mislabelling a file. Choose `container: "auto"` or `mkv` for 4K.

### What are the download caps?

Each video is capped at 30 minutes and 500 MB by default, with at most 50 videos per run. Opt-in 4K is capped at 10 minutes and 1000 MB. A video outside the caps gets a `too_long` or `too_large` failure row instead of a partial file.

### How long do download links last?

Ephemeral KVS links follow your Apify account's key-value store retention. Named KVS persists while the store exists. S3/R2 links are presigned for the configured retention period, or permanent when a public bucket URL is configured. KVS file URLs do not support HTTP Range requests, so use S3/R2 when a downstream system needs resumable or partial downloads.

### Do I need to set up a proxy?

No. The actor chooses a working connection automatically for metadata and player access. Media bytes are fetched directly whenever possible.

### What happens when a video fails?

The run continues and writes a failure row with `failure_code`, `error`, and `retryable`. A failed row never claims a download link.

### Is this affiliated with YouTube?

No. This is an independent third-party tool and is not affiliated with, endorsed by, or sponsored by YouTube or Google.
