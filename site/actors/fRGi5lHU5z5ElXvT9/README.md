# Username Lookup Across 400+ Social Platforms

People reuse the same handle everywhere — this actor checks a username or nickname against 400+ sites at once and reports back which ones actually have a live, public profile under that name. Feed it one username or a batch, narrow it to a handful of platforms or let it check everything, and get a flat list of real, working profile links.

## What this actor does

- Checks each username against your choice of 400+ sites: social networks, video, music, gaming, developer, professional, and messaging platforms
- Confirms every "Found" result with a live request to the platform at run time, using that platform's own sign of a real profile (status code, error text or redirect), rather than guessing from the URL pattern alone
- Supports a wildcard separator (`{?}`) so one query like `john{?}doe` checks `john_doe`, `john-doe`, and `john.doe` in one go
- Runs multiple usernames in the same batch (duplicates are checked once) and caps the total number of rows returned
- When you filter to specific platforms, also lists those platforms where no profile was confirmed; without a filter, only `Found` rows are returned

## Output per check

- `username` — the username or nickname that was searched
- `platform` — the name of the platform checked (e.g. `GitHub`, `Instagram`)
- `url` — the profile URL when `status` is `Found`; an empty string when `Not Found`
- `status` — `Found`, or `Not Found` (only when `platforms` is set; means no profile was confirmed, which also covers checks the platform blocked or that timed out)

If no row at all is produced (for example, no profile found anywhere and no `platforms` filter), the run ends with a failed status and an empty dataset.

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `queries` | array | – | **Required.** Usernames or nicknames to search. Supports `{?}` wildcard expansion (e.g. `john{?}doe`). |
| `platforms` | array | – (all 400+) | Limit the search to specific platforms (pick from the list). Leave empty to check every supported platform. |
| `maxResults` | integer | – (no limit) | Maximum total rows (Found and Not Found) to return across all usernames, in input order. Leave empty for no limit. |

### Example: check one username everywhere

```json
{
  "queries": ["johndoe"],
  "maxResults": 200
}
```

### Example: check several usernames on specific platforms

```json
{
  "queries": ["johndoe", "jane_smith"],
  "platforms": ["Instagram", "GitHub", "LinkedIn", "YouTube"]
}
```

### Example: wildcard separator expansion

```json
{
  "queries": ["john{?}doe"],
  "platforms": ["Instagram", "TikTok", "Twitter"]
}
```

## Use cases

- **Lead enrichment** — attach every public social account to a prospect's known handle
- **Brand protection** — see where your brand name is already claimed across platforms
- **OSINT research** — build a systematic picture of a username's online footprint
- **Background checks** — verify someone's public digital presence before engaging with them
- **Username availability** — shortlist platforms where a desired handle shows no existing profile, then confirm on the site itself
- **Competitive mapping** — chart a competitor's presence across video, social, and developer platforms

## FAQ

**Do I need an account or API key for any platform?**
No. Every check is a direct request to the platform's own public profile URL.

**How long does a run take?**
It depends on how many usernames and platforms you check, and on how quickly each site answers; usernames are checked one after another. Narrowing `platforms` to a shortlist finishes much faster since fewer sites are checked.

**What does the `{?}` wildcard do?**
It expands to the three most common separators — underscore, hyphen, and period — so `john{?}doe` checks `john_doe`, `john-doe`, and `john.doe` as three separate usernames.

**Why doesn't `johndoe` also match `john.doe`?**
Matching is exact per username string. Use the `{?}` wildcard if you want the common separator variants checked together.

**Why are some big platforms, like Facebook, missing from the list?**
Only platforms whose public profile pages can be checked reliably without logging in are included. Pick from the `platforms` list to see exactly what is supported.

**Can I search by email or phone number instead of a username?**
No — this actor only matches against usernames and nicknames.

**Why is `url` empty on a "Not Found" row?**
A `Not Found` row means the platform was checked but no profile could be confirmed, so there's no URL to report. That usually means the username isn't registered there, but a platform that blocks or times out the check is reported the same way.

**How reliable is a "Found" result?**
Each "Found" row is backed by a live check against the platform at run time, not just a guessed URL. False positives can still occur on platforms with unusual redirect or error-page behavior, so open the link before relying on it.

**Is this affiliated with any of the listed platforms?**
No. This is an independent, third-party actor that checks publicly accessible profile pages; it isn't affiliated with Instagram, GitHub, TikTok, or any other platform it checks.
