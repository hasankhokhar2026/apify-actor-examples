# Username Search & Cross-Platform Identity Resolution

Search for usernames across **400+ social networks**, narrow results down to just the platforms you care about, and — uniquely — figure out **which account on a target platform actually belongs to a known profile**, even when squatters and lookalike accounts are in the way.

## What this actor does

- **Search 400+ social networks** in a single run, or filter down to just the ones you need via a dropdown of every supported network
- **Batch processing** — search multiple usernames at once, with `{?}` wildcard expansion for username variations (e.g. `john{?}doe` → `john_doe`, `john-doe`, `john.doe`)
- **Identity resolution** — give it a known account on one platform and a target network, and it either auto-discovers or verifies candidate accounts there, ranking each by a transparent, multi-signal confidence score (bio backlink, display-name/avatar similarity, verified badge, follower count, username similarity) — never a black-box match
- **Honest "no match" reporting** — if no candidate clears the confidence bar, the actor says so instead of guessing
- **Empty fields are omitted** — no `null`, no placeholders; every field present is real data
- **No login required** — works entirely with publicly available information

## Output

### Broad Search (mode = `broadSearch`)

- `username` — the username that was searched
- `links[]` — URLs of profiles where the username was found (omitted entirely if none found)

### Identity Resolution (mode = `identityResolution`)

One record per target network:

- `sourceProfile` — the known account being resolved against, with any enrichment found: `platform`, `handle`, `profileUrl`, `displayName`, `verified`
- `targetNetwork` — the network this record's candidates were evaluated on
- `candidateMode` — `discover` or `verify`
- `candidatesEvaluated` — how many candidates were scored
- `bestMatch` — the highest-confidence candidate (handle, profileUrl, confidenceScore, confidenceLabel, signals) — omitted entirely if none clears the confidence bar
- `candidates[]` — every scored candidate, ranked by confidence, each with its own `signals` breakdown
- `warnings[]` — non-fatal notes (e.g. a signal couldn't be computed, or auto-discovery isn't supported for this network) — omitted if empty

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `broadSearch` | `broadSearch` or `identityResolution` |
| `usernames` | array | – | Usernames to search (mode=broadSearch). Supports `{?}` wildcard. |
| `targetNetworks` | array | – | Networks to limit the search/resolution to — dropdown of every supported network. Optional filter in broadSearch (omit to search all 400+); required (1+) in identityResolution; exactly one required when `candidateMode` is `verify`. |
| `sourceProfile` | object | – | The known account to resolve against — `{platform, handle}` (mode=identityResolution) |
| `sourceOverrides` | object | – | Manual `displayName`/`bio`/`avatarUrl` for the source, used when the source platform can't be auto-read or to supplement missing data (mode=identityResolution) |
| `candidateMode` | string | `discover` | `discover` — auto-find candidates via search + username-variation heuristics; `verify` — score only the handles you supply (mode=identityResolution) |
| `candidateHandles` | array | – | Candidate handles to score (required when `candidateMode` is `verify`) |
| `maxCandidatesToDiscover` | integer | `20` | Caps how many candidates `discover` mode generates/searches (1–60) |

### Example: filter Broad Search to specific networks

```json
{
  "mode": "broadSearch",
  "usernames": ["johndoe"],
  "targetNetworks": ["GitHub", "YouTube"]
}
```

### Example: discover the real account on a target network

```json
{
  "mode": "identityResolution",
  "sourceProfile": { "platform": "instagram", "handle": "xyz" },
  "targetNetworks": ["GitHub"],
  "candidateMode": "discover",
  "maxCandidatesToDiscover": 20
}
```

### Example: verify a shortlist of suspects

```json
{
  "mode": "identityResolution",
  "sourceProfile": { "platform": "github", "handle": "torvalds" },
  "targetNetworks": ["TikTok"],
  "candidateMode": "verify",
  "candidateHandles": ["torvalds", "torvalds_official", "real_torvalds"]
}
```

### Example: batch username search with wildcard expansion

```json
{
  "mode": "broadSearch",
  "usernames": ["john{?}doe", "janedoe"],
  "targetNetworks": ["GitHub", "Reddit", "Twitter"]
}
```

## Use Cases

- **Influencer verification** — confirm which TikTok/Instagram/Twitter account genuinely belongs to a known creator before running a partnership or ad spend
- **Brand protection** — find squatter and impersonator accounts across networks and see exactly why they were flagged as low-confidence
- **OSINT investigations** — discover all online accounts associated with a username, filtered to the networks that matter for the case
- **Digital forensics** — cross-reference identity signals across platforms with a transparent, auditable trail
- **Recruiting / vendor vetting** — cross-check a candidate's or vendor's professional and social presence before engaging

## FAQ

### Can I limit results to just the networks I care about?

Yes. Set `targetNetworks` in `broadSearch` mode (e.g. `["TikTok", "Instagram"]`) — pick from the dropdown of every supported network — and only those sites are checked, so you don't pay for or wait on the other 400+. `identityResolution` mode additionally accepts `Reddit` as a target since it resolves candidates through Reddit's own public search API rather than Sherlock's site list.

### How does it tell the real account apart from fake/lookalike accounts?

This is what `identityResolution` mode is for. Given a known source profile, it finds candidate accounts on the target network (either by searching the platform directly or by generating and existence-checking common username variants like numeric suffixes and "official"/"real" patterns), then scores every candidate on independent signals: whether the candidate's bio links back to the source account, how similar the display names are, how similar the profile pictures are, verified-badge status, relative follower count, and username similarity (case-insensitive). The scores are weighted so that bio backlinks and display-name/avatar similarity — signals fakes rarely have — count far more than raw username similarity, which is exactly what squatter accounts (`xyz0`, `xyz1`, `xyz2`) try to exploit. A bio backlink only ever *helps* a candidate when found — a real profile whose bio simply doesn't mention the source platform (common; most people don't cross-link everywhere) is never penalized for it. The full signal breakdown is always included so you can see exactly why a candidate was or wasn't picked. If no candidate is confidently the real account, the actor reports that honestly instead of guessing.

### What if I already know the suspect accounts and just want them ranked?

Use `candidateMode: "verify"` with `candidateHandles` set to your list of suspects and a single `targetNetworks` entry. The actor skips discovery and scores exactly those candidates.

### Why is auto-discovery unavailable for some networks?

TikTok's public existence-check reports every handle — including random strings — as "existing," so auto-generated candidates there would be fabricated rather than real. Auto-discovery (`candidateMode: "discover"`) is disabled specifically for TikTok for this reason; `candidateMode: "verify"` still works fully, with the same transparent scoring, once you supply your own candidate list.

### How many social networks does it search?

Broad Search covers the same 400+ platforms as the original Sherlock — GitHub, Twitter/X, Instagram, Reddit, TikTok, LinkedIn, YouTube, and hundreds more.

### Does it find private or deleted accounts?

No. Only publicly accessible profiles are checked — private, deleted, or restricted-visibility accounts won't appear.

### What does the `{?}` wildcard do?

Expands a username into three variations using common separators: `_`, `-`, and `.`. For example, `john{?}doe` searches `john_doe`, `john-doe`, and `john.doe`.

### Does this require a login or API key?

No. Everything works with publicly accessible information — no authentication, cookies, or API keys required.

### Can false positives occur?

Yes, occasionally — on both Broad Search (a site may report a username as existing when the page is actually an error page) and Identity Resolution (signals can be sparse for platforms that block scraping, e.g. Twitter/X, lowering confidence). Always review the `signals` breakdown before treating a match as certain.

### Is this affiliated with any of the platforms it searches?

No. This is an independent, third-party actor using only publicly accessible information; it is not affiliated with GitHub, Reddit, TikTok, Instagram, Twitter/X, LinkedIn, YouTube, or any other platform it searches.

### What output formats are available?

Results can be exported as JSON, CSV, Excel (XLSX), HTML, RSS, or XML directly from the Apify platform.
