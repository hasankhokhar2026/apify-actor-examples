# NCAA Stats & Scores: Team & Player Leaderboards, Polls & Standings

Scrape official NCAA.com stats and scores for 14 college sports: team and individual statistical leaderboards, national ranking polls, conference standings, the NCAA school directory, schedules and scores, full team season schedules, championship / March Madness brackets, game details (venue, linescores, box score, play-by-play), and championship history. Every record comes from public NCAA.com pages and the official NCAA scoreboard/championship feeds — no account, cookies, or API key required.

## What this actor does

- **Eleven modes:** `teamStats`, `individualStats`, `rankings`, `standings`, `teams`, `schedules`, `teamSchedule`, `brackets`, `gameDetail`, `history`, `listOptions`
- **`listOptions`** returns the valid modes, sports, divisions, categories, polls, and conferences from the built-in catalog for a given `sport`/`division`; it makes no NCAA.com requests and uses no paid API
- **Fourteen sports** across Division I, II, and III, plus FBS/FCS football and National Collegiate men's volleyball and women's ice hockey
- **Every leaderboard column** NCAA.com publishes for the selected category, including games played, class year, height, and position where available
- **Every NCAA-hosted poll**, including AP, NET, RPI, committee rankings, NPI, WAB, and regional rankings
- **Conference standings** with conference and overall records, win percentage, streak, and sport-specific extra columns
- **School directory** with school name, short name, logo, and NCAA.com school URL
- **Schedules and scores** with home/away teams, scores, status, conferences, ranks, seeds, and championship context
- **Full team season schedules** (`teamSchedule`) from NCAA.com's season-wide schedule dates or football week calendar — not limited to the 31-day `schedules` window
- **Championship / March Madness brackets** (`brackets`) with rounds, regions, seeds, scores, and bracket position, from NCAA.com's official championship GraphQL route
- **Game detail** with venue, city/state, linescores, team records, box-score blocks, and play-by-play when NCAA.com publishes them
- **Optional schedule enrichment** adds venue, linescores, records, and box-score/play-by-play availability flags to schedule and team-schedule rows
- **Championship history** with year, champion, record, coach, score, runner-up, and site
- **Filters** for team, player, rank range, minimum games, conference, and final games only
- **Empty fields are omitted** — no `null`, no placeholders, no fabricated values

## Output per team leaderboard row (`mode: teamStats`)

- `sport`, `sportSlug`, `division`, `season`, `seasonLabel`, `seasonYear`
- `statCategory`, `statCategoryId` — category used and NCAA.com's category id
- `requestedStatCategory`, `fallbackUsed` — when the schema default was replaced by the curated per-sport default
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
- `pollSlug`, `pollName`, `usedPoll`, `requestedPoll`, `fallbackUsed` — the poll requested and the curated default actually used
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
- `sport`, `sportSlug`, `division`, `season`, `seasonLabel`, `seasonYear`, `week` (football)
- `date`, `startTime`, `startTimeEpoch` (UTC epoch)
- `status`, `statusDisplay`, `currentPeriod`, `contestClock`
- `homeTeam`, `homeTeamSlug`, `homeScore`, `homeConference`, `homeRank`, `homeSeed`
- `awayTeam`, `awayTeamSlug`, `awayScore`, `awayConference` (when published), `awayRank`, `awaySeed`
- `winner` — `home`, `away`, or `tie` when a final result is known
- `isChampionship`, `championshipId`, `bracketId`, `roundNumber`, `roundDescription`
- With `includeGameDetails`: `venue`, `city`, `state`, `linescores`, `homeRecord`, `awayRecord`, `homeTeamId`, `awayTeamId`, `homeTeamFullName`, `awayTeamFullName`, `winnerTeamId`, `hasBoxscore`, `hasPbp`, `hasTeamStats`, `hasScoringSummary`
- `sourceUrl`, `recordType`, `scrapedAt`

### Output per team-schedule game (`mode: teamSchedule`)

Same fields as a `schedules` row, returned for one team across the whole NCAA.com season. `team` is required (a school name or NCAA.com slug such as `duke`). The mode reads NCAA.com's season-wide game-date list (or football's week calendar) and does not apply the 31-day window; `scheduleDateFrom`, `scheduleDateTo`, and `week` are ignored. `includeGameDetails` works the same as in `schedules`.

## Output per bracket game (`mode: brackets`)

- `sport`, `sportSlug`, `division`
- `championshipYear`, `season`, `seasonYear` — the tournament year NCAA.com returned
- `championshipId`, `championshipTitle`, `bracketTemplate`
- `gameId`, `gameTitle`, `date`, `startTime`, `startTimeEpoch`
- `status`, `statusDisplay`, `currentPeriod`, `finalMessage`
- `roundNumber`, `roundTitle`, `isFinalRound`
- `bracketPositionId`, `bracketId`, `sectionId`, `region`, `regionCode`
- `homeTeam`, `homeTeamSlug`, `homeSeed`, `homeScore`, `homeTeamLogoUrl`
- `awayTeam`, `awayTeamSlug`, `awaySeed`, `awayScore`, `awayTeamLogoUrl`
- `winner` — `home`, `away`, or `tie` when a result is known; `winnerTeam` when published
- `bracketUrl` — official NCAA.com bracket page; `sourceUrl` — official game page
- `recordType` — `bracketGame`; `scrapedAt`

Unplayed bracket slots that NCAA.com publishes as TBA are returned with their bracket position and round; team and score fields are omitted until NCAA.com publishes them. No team or score is inferred.

## Output per game detail (`mode: gameDetail`)

- `gameId`, `sport`, `sportSlug`, `sportCode`, `division`, `season`, `seasonYear`, `week`
- `date`, `startTime`, `startTimeEpoch` (UTC epoch)
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

## Output per option (`mode: listOptions`)

- `recordType` — `option`
- `optionType` — `mode`, `sport`, `division`, `category`, `poll`, or `conference`
- `value` — the exact value to use in the matching input field
- `title` — human-readable label
- `sport`, `sportTitle`, `division`, `mode`, `statType`, `statCategoryId` — context when the option is scoped
- `isDefault` — `true` when this is the curated default
- `divisions` — for sport options
- `scrapedAt`

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
| `mode` | select | `teamStats` | `teamStats` / `individualStats` / `rankings` / `standings` / `teams` / `schedules` / `teamSchedule` / `brackets` / `gameDetail` / `history` / `listOptions` |
| `sport` | select | `basketball-men` | One of 14 NCAA sports (ignored by `mode=teams` and `mode=gameDetail`; optional scope for `mode=listOptions`) |
| `division` | select | `d1` | `d1` / `d2` / `d3` / `fbs` / `fcs` / `nc` (women's ice hockey `nc` schedules use NCAA.com's d1 scoreboard page; optional scope for `mode=listOptions`) |
| `statCategory` | select | `Scoring Offense` | Statistical category (`mode=teamStats` or `individualStats`); if the default is not valid for the sport/mode the actor uses a curated per-sport default and reports it in the run status |
| `season` | select | `current` | `Current season`, `2026-27` / `2025-26` / `2024-25` labels, `2026` … `2017` (`mode=teamStats`, `individualStats`, `teamSchedule`, or `brackets`). For `brackets`, `season` is the tournament year shown in NCAA.com's bracket URL; `YYYY-YY` tries the ending year first, then the starting year. |
| `pollSlug` | select | `di-mens-basketball-associated-press` | NCAA-hosted poll (`mode=rankings`); if the default is not valid for the sport/division the actor uses the curated default (AP for D1 basketball and FBS, AFCA Coaches for FCS, primary coaches/RPI/AVCA poll elsewhere) and reports it in the run status |
| `gameIds` | array | `[]` | Game IDs or URLs (`mode=gameDetail`), e.g. `6649632` |
| `team` | text | – | Case-insensitive team/school name or NCAA.com slug filter. Required for `mode=teamSchedule`; for example `duke` matches either side of each contest. |
| `playerName` | text | – | Case-insensitive player filter (`mode=individualStats`) |
| `conference` | select | `all` | Conference filter (`mode=standings` or `schedules`); records without a published conference are excluded when set |
| `rankFrom` | integer | – | Lowest rank to keep, 1–1000; records without a rank are excluded when set |
| `rankTo` | integer | – | Highest rank to keep, 1–1000; records without a rank are excluded when set |
| `minGames` | integer | – | Minimum games played, 0–500 (rows without games pass through) |
| `scheduleDateFrom` | text | – | First schedule date, `YYYY-MM-DD` (`mode=schedules`); ignored by `teamSchedule`, which scans the full season |
| `scheduleDateTo` | text | – | Last schedule date, `YYYY-MM-DD` (`mode=schedules`); ignored by `teamSchedule` |
| `week` | integer | – | Football week, 1–20 (`mode=schedules`, football); `teamSchedule` uses the full season calendar automatically |
| `finalOnly` | boolean | `false` | Keep only final games (`mode=schedules`, `teamSchedule`, or `brackets`); records without a final status are excluded |
| `includeGameDetails` | boolean | `false` | Enrich each schedule/team-schedule row with venue, linescores, records, and availability flags |
| `includeBoxscore` | boolean | `true` | Include team/player box-score blocks (`mode=gameDetail`) |
| `includePlayByPlay` | boolean | `false` | Include the play-by-play timeline (`mode=gameDetail`) |
| `maxItems` | integer | – (mode-aware) | Hard cap on records emitted, 1–5000. When omitted: 2,000 for leaderboards, 1,000 for polls/standings/history, 5,000 for the school directory and `listOptions`, 500 for schedules and brackets, 100 for `teamSchedule` and game detail. Leaderboards are also capped at 2,000 source rows (40 pages); the actor sets a status message whenever `maxItems` or the page cap actually truncates the output. |

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

### Example: full team season schedule

```json
{
  "mode": "teamSchedule",
  "sport": "basketball-men",
  "division": "d1",
  "season": "2025-26",
  "team": "duke",
  "maxItems": 100
}
```

### Example: March Madness bracket

```json
{
  "mode": "brackets",
  "sport": "basketball-men",
  "division": "d1",
  "season": "2026",
  "maxItems": 100
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

### Example: discover valid options for a sport/division

```json
{
  "mode": "listOptions",
  "sport": "basketball-women",
  "division": "d1",
  "maxItems": 5000
}
```

Each returned option record has `optionType`, `value`, `title`, and `isDefault` (when it is the curated default). Leave `sport` and `division` empty to list every sport, mode, and conference.

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

**Why did my schedule run return no games?** Check the date window and `finalOnly`. Football `schedules` runs are week-based: set `week` instead of a date range. Dates outside the current or archived season may have no games. For a whole team season, use `mode=teamSchedule` with `team`; it is not limited to the 31-day window.

**How do I get one team's full season schedule?** Use `mode=teamSchedule` with `team` (a school name or NCAA.com slug such as `duke`). The actor reads NCAA.com's season-wide game-date feed (or football's week calendar), then queries each date and keeps only that team's games. It is not limited to 31 days and ignores `scheduleDateFrom`/`scheduleDateTo`. Set `includeGameDetails` for venue, linescores, records, and availability flags.

**Are March Madness and other championship brackets included?** Yes, with `mode=brackets`. The actor calls NCAA.com's official `get_championship_ncaa` GraphQL route, which returns the same bracket data as the public bracket pages, including round, region, seeds, scores, and bracket position. Set `season` to the tournament year (for example `2026`); `YYYY-YY` labels try the ending year first and then the starting year. Brackets appear after the field is announced, and some sports/divisions publish only recent years. Unplayed TBA slots are returned without invented teams or scores. If NCAA.com rotates its persisted query, the run finishes with a clear status message instead of returning a partial or fabricated bracket.

**Do you include rosters, injuries, or betting odds?** No. These are out-of-scope external-source limitations, not hidden data limits. The public NCAA.com pages and GraphQL feeds this actor uses do not publish rosters, injury reports, or odds: rosters live on school athletics sites (and stats.ncaa.org is Akamai/robots-blocked), injuries are team/third-party announcements, and odds come from licensed sportsbooks or ESPN. Adding them would require a different non-NCAA source, so the actor does not fabricate or guess them.

**Are schedules and scores live?** They reflect the public NCAA scoreboard at the time of the run. Scheduled games show their start time; completed games show final scores and a winner.

**How do I get venue, box score, or play-by-play?** Use `mode: gameDetail` with one or more `gameIds`. Set `includeBoxscore` and/or `includePlayByPlay` to add those blocks. You can also set `includeGameDetails: true` on `schedules` to add venue, linescores, records, and availability flags to each schedule row without fetching full box scores or play-by-play.

**Why is a venue or box score missing for some games?** NCAA.com publishes those fields only for games it has complete data for. The actor adds `hasBoxscore`, `hasPbp`, `hasTeamStats`, and `hasScoringSummary` flags so you can tell what is available; it never fabricates a missing venue or stat.

**What happens if I leave the default category or poll selected for another sport?** The schema default is treated as "no explicit choice". If it is not valid for the selected sport/mode, the actor uses a curated default — for example AP for D1 basketball and FBS football, AFCA Coaches for FCS, and the primary coaches/RPI/AVCA poll elsewhere; Points Per Game for basketball players, Passing Yards Per Game for FBS players, and Batting Average for baseball/softball — and reports the substitution in the run status. It never picks the alphabetically first option.

**How do I find the valid categories, polls, or conferences?** Run `mode: listOptions` with the sport/division you care about. It returns the exact `value` strings to use in `statCategory`, `pollSlug`, `conference`, and the other select fields. You can also run it without a sport to list every mode, sport, division, and conference.

**What time zone is used for the default schedule date?** When both schedule dates are empty, the actor uses today's date in America/New_York (the zone NCAA.com's scoreboard uses) and keeps `startTimeEpoch` in UTC. Set `scheduleDateFrom`/`scheduleDateTo` explicitly for archival dates.

**Why does a category or poll return a "no data" message instead of an empty dataset?** NCAA.com sometimes publishes a category page that has no rows for a sport/division/season, or a poll that is not yet live. The actor detects that page state and returns the valid alternatives in the run status instead of reporting a generic "no rows" result. The catalog was also scrubbed of category IDs that NCAA.com returns 404.

**What do the filters do when a field is missing?** `team`, `playerName`, rank, conference, and `finalOnly` are strict when set: a record without the filtered field is excluded. `minGames` is the exception — rows without a games-played column pass through, as documented in the input description.

**Why is `nc` accepted for women's ice hockey schedules if NCAA.com's nc page is 404?** The actor maps that combination to NCAA.com's d1 scoreboard page, which is where NCAA.com serves the National Collegiate schedule. The output keeps the division you requested.

**Why did a large run stop before reaching `maxItems`?** Leaderboard modes are capped at 2,000 source rows (40 pages of 50). If the page cap is reached first, the run sets a status message; split by category or season to collect more. The same applies when `maxItems` truncates standings, teams, rankings, schedules, or history — the status message says which cap stopped the run and how many source rows were available.

**Why is `maxItems` optional now?** The old fixed default of 50 silently truncated large exports. `maxItems` now has a mode-aware default (for example 5,000 for the school directory, 2,000 for leaderboards, 100 for game detail) while the daily-test prefill stays at 3. The schema maximum is 5,000.

**Is this affiliated with the NCAA?** No. This is a third-party actor using publicly available NCAA.com statistics, rankings, standings, school, schedule, game-detail, and history pages.
