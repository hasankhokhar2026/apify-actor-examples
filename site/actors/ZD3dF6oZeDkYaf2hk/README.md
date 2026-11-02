# NCAA Team & Player Leaderboards, Polls & Standings

Pull official NCAA statistical leaderboards, ranking polls, and conference
standings for 14 college sports — men's and women's basketball, football,
baseball, softball, soccer, volleyball, lacrosse, ice hockey, and field hockey —
across Division I, II, and III (FBS/FCS for football; men's volleyball rankings
use the pooled "National Collegiate" division instead). No login, no cookies,
no paid proxy required.

## What this actor does

- **Team leaderboards** — every team-level statistical category NCAA.com tracks
  (Scoring Offense, Rebound Margin, Turnover Margin, Field Goal Percentage, and
  dozens more, sport-specific)
- **Individual (player) leaderboards** — the same categories at player level
  (Points Per Game, Passing Yards Per Game, Batting Average, etc.), including
  class year, height, and position where NCAA.com publishes them
- **National ranking polls** — AP Top 25, Coaches Polls, NET Rankings, RPI,
  committee rankings, and sport-specific polls (United Soccer Coaches, D1Baseball.com
  Top 25, AVCA Rankings, and more)
- **Conference standings** — conference and overall win-loss records, PCT, streak,
  and (for football) points for/against and home/away splits, grouped by
  conference. Currently published live by NCAA.com only for Division I men's
  and women's basketball and FBS/FCS football; other sport/division combinations
  return a clear status message instead of data
- **Historical seasons** — archive depth varies by sport (men's basketball back to
  2017; most other sports only have 1-4 prior seasons on NCAA.com). An unsupported
  season/sport combination returns a clear status message instead of data.
- **Automatic pagination** up to your requested `maxItems`
- Empty/unavailable fields are omitted from every record — no `null`, no placeholders

## Output fields

### Team statistics (`mode: teamStats`)

| Field | Description |
|---|---|
| `rank` | Position in the leaderboard |
| `tiedRank` | `true` only when this row shares its `rank` with the row above it (NCAA.com marks tied rows with `-` instead of repeating the number) |
| `team` | School name |
| `teamUrl` | Link to the school's NCAA.com page |
| `teamLogoUrl` | School logo image |
| `gamesPlayed` | Games played this season |
| `statCategory` / `statCategoryId` | The requested category and its NCAA.com id |
| `statValue` / `statLabel` | The category's headline value and its column label (e.g. `91.2` / `PPG`) |
| `stats` | Every other numeric column NCAA.com shows for this category (varies by category) |
| `sport` / `sportSlug` / `division` / `season` | Query context |
| `page` | Leaderboard page this row came from |
| `sourceUrl` | The exact NCAA.com page scraped |

### Individual statistics (`mode: individualStats`)

Same as team statistics, plus:

| Field | Description |
|---|---|
| `playerName` | Player's name |
| `class` | Class year (`Fr.`, `So.`, `Jr.`, `Sr.`) — when NCAA.com publishes it |
| `height` | Player height — when NCAA.com publishes it |
| `position` | Playing position — when NCAA.com publishes it |

### Rankings (`mode: rankings`)

| Field | Description |
|---|---|
| `rank` | Poll rank |
| `tiedRank` | `true` only when this row shares its `rank` with the row above it |
| `school` | School name |
| `firstPlaceVotes` | First-place votes received (media/coaches polls only) |
| `record` / `wins` / `losses` / `ties` | Season record, parsed into components |
| `points` | Poll points total (when the poll publishes one) |
| `previousRank` | Previous week's rank (when published) |
| `pollStats` | Every other column the poll table shows (conference, quadrant records, road/home/neutral splits, etc. — varies by poll) |
| `pollSlug` / `pollName` | The requested poll |
| `sport` / `sportSlug` / `division` | Query context |
| `sourceUrl` | The exact NCAA.com rankings page scraped |

### Conference standings (`mode: standings`)

| Field | Description |
|---|---|
| `conference` | Conference name (e.g. `ACC`, `Big Ten`) |
| `team` | School name |
| `teamLogoUrl` | School logo image |
| `conferenceWins` / `conferenceLosses` / `conferencePct` | Record within conference play |
| `overallWins` / `overallLosses` / `overallPct` | Season-wide record |
| `streak` | Current win/loss streak (e.g. `Won 3`) |
| `standingsStats` | Sport-specific extra columns NCAA.com publishes (e.g. football's points for/against and home/away splits) |
| `sport` / `sportSlug` / `division` | Query context |
| `sourceUrl` | The exact NCAA.com standings page scraped |

Every record also includes `recordType` and `scrapedAt` (UTC timestamp).

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `teamStats` | `teamStats` / `individualStats` / `rankings` / `standings` |
| `sport` | select | `basketball-men` | One of 14 supported NCAA sports |
| `division` | select | `d1` | `d1` / `d2` / `d3` / `fbs` / `fcs` / `nc` (football uses FBS/FCS; men's volleyball rankings use `nc` — National Collegiate) |
| `statCategory` | select | `Scoring Offense` | Statistical category (`mode=teamStats`/`individualStats`) — options depend on `sport` |
| `season` | select | `current` | Season/year; archive depth varies by sport (men's basketball back to 2017, most others fewer seasons) |
| `pollSlug` | select | `associated-press` | Which ranking poll to scrape (`mode=rankings`) — options depend on `sport` |
| `maxItems` | integer | `25` | Hard cap on records emitted (1–500) |

### Supported sports and divisions

| Sport | `sport` value | Divisions |
|---|---|---|
| Men's Basketball | `basketball-men` | d1, d2, d3 |
| Women's Basketball | `basketball-women` | d1, d2, d3 |
| Football | `football` | fbs, fcs, d2, d3 |
| Baseball | `baseball` | d1, d2, d3 |
| Softball | `softball` | d1, d2, d3 |
| Men's Soccer | `soccer-men` | d1, d2, d3 |
| Women's Soccer | `soccer-women` | d1, d2, d3 |
| Men's Volleyball | `volleyball-men` | d1, d3 |
| Women's Volleyball | `volleyball-women` | d1, d2, d3 |
| Men's Lacrosse | `lacrosse-men` | d1, d2, d3 |
| Women's Lacrosse | `lacrosse-women` | d1, d2, d3 |
| Men's Ice Hockey | `icehockey-men` | d1, d3 |
| Women's Ice Hockey | `icehockey-women` | d1, d3 |
| Field Hockey | `fieldhockey` | d1, d2, d3 |

If you request a `sport`/`division` combination NCAA.com doesn't publish (e.g.
Division II men's volleyball), or a `statCategory`/`pollSlug` that doesn't exist
for the chosen sport, the run finishes with a clear status message listing the
valid options for that sport instead of failing silently.

### Example: team scoring leaders

```json
{
  "mode": "teamStats",
  "sport": "basketball-men",
  "division": "d1",
  "statCategory": "Scoring Offense",
  "season": "current",
  "maxItems": 50
}
```

### Example: individual passing leaders (FBS football)

```json
{
  "mode": "individualStats",
  "sport": "football",
  "division": "fbs",
  "statCategory": "Passing Yards Per Game",
  "season": "current",
  "maxItems": 100
}
```

### Example: AP Top 25

```json
{
  "mode": "rankings",
  "sport": "basketball-men",
  "division": "d1",
  "pollSlug": "associated-press"
}
```

### Example: conference standings

```json
{
  "mode": "standings",
  "sport": "basketball-men",
  "division": "d1"
}
```

### Example: historical season archive

```json
{
  "mode": "teamStats",
  "sport": "baseball",
  "division": "d1",
  "statCategory": "Batting Average",
  "season": "2023",
  "maxItems": 200
}
```

## Use cases

- **Sports media & content sites** — auto-publish weekly leaderboard and poll roundups
- **Fantasy sports & betting research** — track team and player statistical trends
- **Recruiting & scouting** — surface individual leaderboards by position/category
- **Sports analytics** — build historical statistical datasets across seasons
- **Fan dashboards** — power a live conference/team stat tracker
- **Academic research** — study competitive trends across NCAA divisions

## FAQ

**Do I need an NCAA.com account, cookies, or API key?** No. This actor reads
publicly published pages only.

**Why does `stats` (or `pollStats`) vary between records?** NCAA.com shows a
different set of columns for every statistical category and every poll (e.g.
scoring stats show `PTS`/`PPG`; NET Rankings show conference and quadrant
records). The actor captures every column the source page publishes for the
requested category/poll — nothing is padded with placeholder values.

**What does `statValue`/`statLabel` mean?** NCAA.com's rightmost column is
the category's headline number (e.g. `91.2` under `PPG` for Scoring Offense).
`statValue`/`statLabel` surface that number directly; `stats` contains the
full column set for anyone who wants every number NCAA.com published.

**How far back does `season` go?** Most sports have archives back to 2017;
`current` always follows whichever season NCAA.com is actively displaying.
Archive coverage is set by NCAA.com itself and varies by sport/category/year —
a handful of older combinations for less-prominent sports aren't published in
the archive. When that happens the run finishes cleanly with 0 records and a
status message rather than an error; just try an adjacent season.

**Why do two rows share the same `rank`?** NCAA.com itself displays ties this
way — a tied row's rank cell shows `-` instead of repeating the number, so the
actor carries the previous row's rank forward and flags the row with
`tiedRank: true` rather than dropping it (an earlier version silently lost
these rows).

**Are `teamUrl` and `teamLogoUrl` reliable?** Yes — both are direct NCAA.com
URLs (the school's own page and its official logo asset) and are checked to
resolve without any cookies or referer header.

**Can I scrape multiple categories or polls in one run?** Run the actor once
per `statCategory`/`pollSlug` combination — this keeps each run's output
focused on one leaderboard or poll, matching how NCAA.com itself organizes
the data.

**Why is `mode: standings` only available for a few sports?** NCAA.com itself
only publishes a conference-standings widget for Division I men's/women's
basketball and FBS/FCS football — it doesn't build the page for other
sports/divisions at all (confirmed against the live site). Requesting any
other combination returns a clear status message instead of an empty result.

**Why did my run finish with 0 items and a status message?** Either the
`sport`/`division` pairing isn't offered by NCAA.com (e.g. Division II men's
volleyball), or the `statCategory`/`pollSlug` you chose doesn't exist for that
sport. The status message lists every valid option for the sport you selected.

**Is this affiliated with NCAA.com?** No, this is a third-party actor using
NCAA.com's public statistics, rankings, and standings pages. It is not
affiliated with, endorsed by, or sponsored by the NCAA.
