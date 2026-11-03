# NCAA Team & Player Leaderboards, Polls & Standings

Scrape official NCAA.com data for 14 college sports: team and individual statistical leaderboards, national ranking polls, conference standings, the NCAA school directory, schedules and scores, game details (venue, linescores, box score, play-by-play), and championship history. Every record comes from public NCAA.com pages and the official NCAA scoreboard feed — no account, cookies, or API key required.

## What this actor does

- **Eight modes:** `teamStats`, `individualStats`, `rankings`, `standings`, `teams`, `schedules`, `gameDetail`, `history`
- **Fourteen sports** across Division I, II, and III, plus FBS/FCS football and National Collegiate men's volleyball and women's ice hockey
- **Every leaderboard column** NCAA.com publishes for the selected category, including games played, class year, height, and position where available
- **Every NCAA-hosted poll**, including AP, NET, RPI, committee rankings, NPI, WAB, and regional rankings
- **Conference standings** with conference and overall records, win percentage, streak, and sport-specific extra columns
- **School directory** with school name, short name, logo, and NCAA.com school URL
- **Schedules and scores** with home/away teams, scores, status, conferences, ranks, seeds, and championship context
- **Game detail** with venue, city/state, linescores, team records, box-score blocks, and play-by-play when NCAA.com publishes them
- **Optional schedule enrichment** adds venue, linescores, records, and box-score/play-by-play availability flags to schedule rows
- **Championship history** with year, champion, record, coach, score, runner-up, and site
- **Filters** for team, player, rank range, minimum games, conference, and final games only
- **Empty fields are omitted** — no `null`, no placeholders, no fabricated values

## Output per team leaderboard row (`mode: teamStats`)

- `sport`, `sportSlug`, `division`, `season`
- `statCategory`, `statCategoryId` — requested category and NCAA.com's category id
- `rank` — leaderboard position
- `tiedRank` — `true` only when the row shares the rank above it
- `team` — school name
- `teamUrl` — NCAA.com school page
- `teamLogoUrl` — official school logo
- `gamesPlayed`
- `stats` — every other numeric or text column NCAA.com shows for the category
- `statLabel`, `statValue` — the category's headline column label and value
- `lastUpdated` — NCAA.com's "through games" or last-updated note, when published
- `page` — source leaderboard page
- `sourceUrl`, `recordType`, `scrapedAt`

## Output per player leaderboard row (`mode: individualStats`)

Same fields as a team leaderboard row, plus:

- `playerName`
- `class` — class year when NCAA.com publishes it
- `height` — when NCAA.com publishes it
- `position` — when NCAA.com publishes it

## Output per poll row (`mode: rankings`)

- `sport`, `sportSlug`, `division`
- `pollSlug`, `pollName`
- `rank`, `tiedRank`
- `school` — school or college name
- `firstPlaceVotes` — when the poll publishes first-place votes
- `record`, `wins`, `losses`, `ties` — when the poll publishes a record
- `points` — poll points when published
- `previousRank` — previous poll position when published
- `conference` — when the poll table includes a conference column
- `pollStats` — every other column the poll publishes (road/home/neutral splits, quadrant records, etc.)
- `lastUpdated` (when published), `sourceUrl`, `recordType`, `scrapedAt`

## Output per standings row (`mode: standings`)

- `sport`, `sportSlug`, `division`
- `conference`, `conferenceSlug` (`conferenceSlug` when a specific conference was requested)
- `team`, `teamLogoUrl`
- `conferenceWins`, `conferenceLosses`, `conferencePct`
- `overallWins`, `overallLosses`, `overallPct`
- `streak`
- `standingsStats` — sport-specific extra columns (for football: points for/against, home/away records)
- `lastUpdated` (when published), `sourceUrl`, `recordType`, `scrapedAt`

## Output per school (`mode: teams`)

- `team` — short school name
- `schoolName` — full institution name
- `teamSlug` — NCAA.com school slug
- `teamUrl`, `teamLogoUrl`
- `page` — directory page
- `sourceUrl`, `recordType`, `scrapedAt`

## Output per game (`mode: schedules`)

- `gameId`
- `sport`, `sportSlug`, `division`, `season`, `week` (football)
- `date`, `startTime`, `startTimeEpoch`
- `status`, `statusDisplay`, `currentPeriod`, `contestClock`
- `homeTeam`, `homeTeamSlug`, `homeScore`, `homeConference`, `homeRank`, `homeSeed`
- `awayTeam`, `awayTeamSlug`, `awayScore`, `awayConference` (when published), `awayRank`, `awaySeed`
- `winner` — `home`, `away`, or `tie` when a final result is known
- `isChampionship`, `championshipId`, `bracketId`, `roundNumber`, `roundDescription`
- With `includeGameDetails`: `venue`, `city`, `state`, `linescores`, `homeRecord`, `awayRecord`, `homeTeamId`, `awayTeamId`, `homeTeamFullName`, `awayTeamFullName`, `winnerTeamId`, `hasBoxscore`, `hasPbp`, `hasTeamStats`, `hasScoringSummary`
- `sourceUrl`, `recordType`, `scrapedAt`

## Output per game detail (`mode: gameDetail`)

- `gameId`, `sport`, `sportSlug`, `sportCode`, `division`, `season`, `week`
- `date`, `startTime`, `startTimeEpoch`
- `status`, `statusDisplay`, `currentPeriod`, `clock`, `finalMessage`
- `venue`, `city`, `state` — when NCAA.com publishes a location
- `homeTeam`, `homeTeamId`, `homeTeamSlug`, `homeTeamFullName`, `homeCollegeName`, `homeColor`, `homeScore`, `homeRecord`, `homeRank`, `homeGameRank`, `homeSeed`
- `awayTeam`, `awayTeamId`, `awayTeamSlug`, `awayTeamFullName`, `awayCollegeName`, `awayColor`, `awayScore`, `awayRecord`, `awayRank`, `awayGameRank`, `awaySeed`
- `winner`, `winnerTeamId`
- `linescores` — per-period home/visit scores
- `hasBoxscore`, `hasPbp`, `hasTeamStats`, `hasScoringSummary`
- `isChampionship`, `isConferenceTournament`, `network`
- With `includeBoxscore`: `homeTeamStats`, `awayTeamStats`, `homePlayerStats`, `awayPlayerStats`, `boxscoreTitle`, `boxscoreStatus`, `boxscorePeriod`
- With `includePlayByPlay`: `playByPlay` (periods and events), `playCount`, `pbpTitle`, `pbpStatus`
- `sourceUrl`, `recordType`, `scrapedAt`

## Output per champion (`mode: history`)

- `sport`, `sportSlug`, `division`
- `year`
- `champion`, `championRecord`, `wins`, `losses`, `ties` — when a record is published
- `coach` — when published
- `score` — final score when published
- `runnerUp` — when published
- `site` — host city/site when published
- `selectingOrganization` — for football champions selected by different organizations
- `sourceUrl`, `recordType`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | select | `teamStats` | `teamStats` / `individualStats` / `rankings` / `standings` / `teams` / `schedules` / `gameDetail` / `history` |
| `sport` | select | `basketball-men` | One of 14 NCAA sports (ignored by `mode=teams` and `mode=gameDetail`) |
| `division` | select | `d1` | `d1` / `d2` / `d3` / `fbs` / `fcs` / `nc` (women's ice hockey `nc` schedules use NCAA.com's d1 scoreboard page) |
| `statCategory` | select | `Scoring Offense` | Statistical category (`mode=teamStats` or `individualStats`); falls back to the first valid category when the default is not available for the selected sport/mode |
| `season` | select | `current` | `Current season`, `2026` … `2017` (`mode=teamStats`, `individualStats`, or `schedules`) |
| `pollSlug` | select | `di-mens-basketball-associated-press` | NCAA-hosted poll (`mode=rankings`); falls back to the first valid poll when the default is not available for the selected sport/division |
| `gameIds` | array | `[]` | Game IDs or URLs (`mode=gameDetail`), e.g. `6649632` |
| `team` | text | – | Case-insensitive team/school filter |
| `playerName` | text | – | Case-insensitive player filter (`mode=individualStats`) |
| `conference` | select | `all` | Conference filter (`mode=standings` or `schedules`); records without a published conference are excluded when set |
| `rankFrom` | integer | – | Lowest rank to keep, 1–1000; records without a rank are excluded when set |
| `rankTo` | integer | – | Highest rank to keep, 1–1000; records without a rank are excluded when set |
| `minGames` | integer | – | Minimum games played, 0–500 (rows without games pass through) |
| `scheduleDateFrom` | text | – | First schedule date, `YYYY-MM-DD` (`mode=schedules`) |
| `scheduleDateTo` | text | – | Last schedule date, `YYYY-MM-DD` (`mode=schedules`) |
| `week` | integer | – | Football week, 1–20 (`mode=schedules`, football) |
| `finalOnly` | boolean | `false` | Keep only final games (`mode=schedules`); records without a final status are excluded |
| `includeGameDetails` | boolean | `false` | Enrich each schedule row with venue, linescores, records, and availability flags |
| `includeBoxscore` | boolean | `true` | Include team/player box-score blocks (`mode=gameDetail`) |
| `includePlayByPlay` | boolean | `false` | Include the play-by-play timeline (`mode=gameDetail`) |
| `maxItems` | integer | `50` | Hard cap on records emitted, 1–2000. Leaderboards are also capped at 2,000 source rows (40 pages); the actor sets a status message if that cap is reached before `maxItems`. |

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
| Men's Volleyball | `volleyball-men` | d1, d3, nc |
| Women's Volleyball | `volleyball-women` | d1, d2, d3 |
| Men's Lacrosse | `lacrosse-men` | d1, d2, d3 |
| Women's Lacrosse | `lacrosse-women` | d1, d2, d3 |
| Men's Ice Hockey | `icehockey-men` | d1, d3 |
| Women's Ice Hockey | `icehockey-women` | d1, d3, nc |
| Field Hockey | `fieldhockey` | d1, d2, d3 |

If you request a sport/division combination NCAA.com does not publish, or a category/poll/conference that does not exist for that combination, the run finishes with a status message listing the valid options instead of failing silently.

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

### Example: player passing leaders with a team filter

```json
{
  "mode": "individualStats",
  "sport": "football",
  "division": "fbs",
  "statCategory": "Passing Yards Per Game",
  "team": "Oregon",
  "minGames": 8,
  "maxItems": 100
}
```

### Example: AP Top 25, ranks 1-10

```json
{
  "mode": "rankings",
  "sport": "basketball-men",
  "division": "d1",
  "pollSlug": "di-mens-basketball-associated-press",
  "rankFrom": 1,
  "rankTo": 10
}
```

### Example: ACC standings

```json
{
  "mode": "standings",
  "sport": "basketball-men",
  "division": "d1",
  "conference": "acc",
  "maxItems": 50
}
```

### Example: final games on a date

```json
{
  "mode": "schedules",
  "sport": "basketball-men",
  "division": "d1",
  "scheduleDateFrom": "2026-11-02",
  "scheduleDateTo": "2026-11-02",
  "finalOnly": true,
  "maxItems": 100
}
```

### Example: enrich schedules with game details

```json
{
  "mode": "schedules",
  "sport": "basketball-men",
  "division": "d1",
  "scheduleDateFrom": "2026-11-02",
  "scheduleDateTo": "2026-11-02",
  "includeGameDetails": true,
  "maxItems": 25
}
```

### Example: full game detail with box score and play-by-play

```json
{
  "mode": "gameDetail",
  "gameIds": ["6649632"],
  "includeBoxscore": true,
  "includePlayByPlay": true
}
```

### Example: championship history

```json
{
  "mode": "history",
  "sport": "basketball-men",
  "division": "d1",
  "maxItems": 200
}
```

## Use cases

- **Sports media and content sites** — auto-publish weekly leaderboard, poll, and standings roundups
- **Fantasy sports and betting research** — track team and player statistical trends over time
- **Recruiting and scouting** — search player leaderboards by name, team, class year, or position
- **Sports analytics** — build historical datasets from leaderboards, polls, and championship results
- **Fan dashboards** — power live score, schedule, and conference-standings widgets
- **Academic research** — compare competitive trends across NCAA divisions and sports

## FAQ

**Do I need an NCAA.com account, cookies, or an API key?** No. The actor reads public NCAA.com pages and the public NCAA scoreboard feed.

**Why does `stats` or `pollStats` vary between records?** NCAA.com publishes a different set of columns for every statistical category and every poll. The actor captures every column the source page shows for the requested category or poll, with numeric values parsed as numbers.

**What do `statValue` and `statLabel` mean?** NCAA.com's rightmost column is the category's headline number. `statLabel` is that column's label (for example `PPG`) and `statValue` is the number.

**How far back does `season` go?** Archive depth is set by NCAA.com and varies by sport. Men's basketball has the deepest archive; several other sports have only recent seasons. When a season is not published, the run finishes with a clear status message.

**Why do two rows share the same `rank`?** NCAA.com renders a tied row's rank as `-` instead of repeating the number. The actor carries the previous rank forward and adds `tiedRank: true` rather than dropping the row.

**Why are some polls missing for my sport?** The actor exposes only polls hosted on NCAA.com. Some polls (for example USA Today coaches polls) live on third-party sites and are not scraped.

**Can I scrape multiple categories or polls in one run?** Run the actor once per category or poll. Each run is focused on one leaderboard or poll, matching how NCAA.com organizes the data.

**Why is `standings` only available for a few sports?** NCAA.com publishes its conference-standings widget only for Division I men's and women's basketball and FBS/FCS football. Other sport/division combinations return a status message.

**Why did my schedule run return no games?** Check the date window and `finalOnly`. Football schedules are week-based: set `week` instead of a date range. Dates outside the current or archived season may have no games.

**Are schedules and scores live?** They reflect the public NCAA scoreboard at the time of the run. Scheduled games show their start time; completed games show final scores and a winner.

**How do I get venue, box score, or play-by-play?** Use `mode: gameDetail` with one or more `gameIds`. Set `includeBoxscore` and/or `includePlayByPlay` to add those blocks. You can also set `includeGameDetails: true` on `schedules` to add venue, linescores, records, and availability flags to each schedule row without fetching full box scores or play-by-play.

**Why is a venue or box score missing for some games?** NCAA.com publishes those fields only for games it has complete data for. The actor adds `hasBoxscore`, `hasPbp`, `hasTeamStats`, and `hasScoringSummary` flags so you can tell what is available; it never fabricates a missing venue or stat.

**What happens if I leave the default category or poll selected for another sport?** The schema default is treated as "no explicit choice". If it is not valid for the selected sport/mode, the actor falls back to the first category or poll NCAA.com publishes for that combination instead of returning an error.

**What do the filters do when a field is missing?** `team`, `playerName`, rank, conference, and `finalOnly` are strict when set: a record without the filtered field is excluded. `minGames` is the exception — rows without a games-played column pass through, as documented in the input description.

**Why is `nc` accepted for women's ice hockey schedules if NCAA.com's nc page is 404?** The actor maps that combination to NCAA.com's d1 scoreboard page, which is where NCAA.com serves the National Collegiate schedule. The output keeps the division you requested.

**Why did a large leaderboard run stop before reaching `maxItems`?** Leaderboard modes are capped at 2,000 source rows (40 pages of 50). If the cap is reached first, the run sets a status message; split by category or season to collect more.

**Is this affiliated with the NCAA?** No. This is a third-party actor using publicly available NCAA.com statistics, rankings, standings, school, schedule, game-detail, and history pages.
