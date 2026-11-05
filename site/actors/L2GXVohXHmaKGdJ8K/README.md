# TikTok Top Ads Leaderboard - 122 Markets & Metrics

See what is actually winning on TikTok. This actor reads TikTok's public Creative
Center Top Ads boards and returns one structured row per ad: the creative, brand,
CTR, likes, budget tier, industry, campaign objective, downloadable video renditions,
and the landing page when TikTok publishes it. It also reads TikTok's handpicked Top
Ads Spotlight and can refresh a list of known ad IDs.

No TikTok account, cookies, API key, or browser is required. The actor signs its own
anonymous Creative Center session with plain HTTP.

## What this actor does

- Reads the Top Ads leaderboard for any of **122 markets**, 7 / 30 / 180-day windows,
  258 industries, 8 campaign objectives, 17 ad languages, Spark/Non-Spark formats,
  and 5 like-percentile tiers.
- Ranks by TikTok's For You mix, Reach, CTR, 2-second view rate, 6-second view rate,
  conversion rate, or Likes. CTR and Likes are returned highest-first.
- Goes beyond TikTok's 20-ad board by reading more filter combinations and deduplicating
  by ad ID. It stops at your `maxItems` or when the source has no more unique ads.
- Optionally adds the ad detail record: landing page, target countries, comments,
  shares, ad source, and the full objective list.
- Optionally adds the per-second retention curve from TikTok's keyframe data.
- Reads the Top Ads Spotlight: five handpicked ads with TikTok's expert commentary.
- Refreshes specific ad IDs or Creative Center URLs without re-running a whole board.
- Preserves the original output fields and adds new fields beside them.

## How many ads can I get?

TikTok shows an anonymous visitor **20 ads per filter board** (one market + period +
industry + objective + ranking + format + like tier). The second page is empty. The
ranked index behind a query can hold up to **500** ads, but only 20 are visible per
board.

This actor reads board after board - other rankings, objectives, industries, formats,
like tiers, languages, and markets - and deduplicates by ad ID. `maxItems` is a cap on
unique ads, not a promise that one board contains that many. If the source runs out,
the run succeeds with an honest status message instead of pretending it filled the
request.

## Modes

| Mode | What it reads |
|---|---|
| **Top Ads leaderboard** (default) | The main Top Ads boards, with all filters and the sweep. |
| **Top Ads Spotlight** | TikTok's handpicked Spotlight list, five ads with expert commentary. `industry` is the only board filter used; `includeDetails` adds title, brand, landing page, and target countries. |
| **Specific ad IDs** | A detail lookup for each ID or Creative Center URL you provide. |

## Inputs

| Field | Default | What it controls |
|---|---|---|
| `mode` | `leaderboard` | Leaderboard, Spotlight, or Specific ad IDs. |
| `country` | `US` | 122 markets, or **All countries** to read multiple market boards and merge the results. |
| `period` | `30` | Last 7, 30, or 180 days. |
| `industry` | All industries | TikTok's 258-entry industry taxonomy; child categories are shown under their parent. |
| `objective` | All objectives | Traffic, App Installs, Conversions, Video Views, Reach, Lead Generation, Product Sales, or App Promotion. |
| `language` | All languages | The language of the ad copy (17 options). |
| `adFormat` | All formats | All formats, Spark ads, or Non-Spark ads. |
| `likeTier` | All like tiers | All like tiers, Top 1-20%, Top 21-40%, Top 41-60%, Top 61-80%, or Top 81-100%. |
| `orderBy` | `for_you` | For You, Reach, CTR, 2-second view rate, 6-second view rate, conversion rate, or Likes. |
| `maxItems` | `30` | Maximum unique ads to deliver, 0-500. |
| `sweep` | `true` | Read more filter combinations to get past the 20-ad board. Turn off to get exactly one board. |
| `includeDetails` | `true` | Add landing page, target countries, comments, shares, source, and objectives. |
| `includeKeyframes` | `false` | Add the per-second retention curve. |
| `adIds` | Any | Ad IDs or Creative Center URLs for Specific ad IDs mode. |

### Examples

Top US ads from the last 30 days:

```json
{
  "mode": "leaderboard",
  "country": "US",
  "period": "30",
  "maxItems": 50,
  "sweep": true
}
```

Spark conversion ads in Germany over 180 days, with landing pages:

```json
{
  "mode": "leaderboard",
  "country": "DE",
  "period": "180",
  "objective": "campaign_objective_conversion",
  "adFormat": "1",
  "maxItems": 100,
  "includeDetails": true
}
```

All countries, Beauty & Personal Care, highest CTR, top 20:

```json
{
  "mode": "leaderboard",
  "country": "",
  "period": "30",
  "industry": "label_14000000000",
  "orderBy": "ctr",
  "maxItems": 20
}
```

Top Ads Spotlight:

```json
{
  "mode": "spotlight",
  "industry": "label_15000000000",
  "maxItems": 5
}
```

Refresh two known ads:

```json
{
  "mode": "byAdIds",
  "adIds": [
    "7694650748144042002",
    "https://ads.tiktok.com/business/creativecenter/topads/7694538970823606279/pc/en"
  ]
}
```

## Output

Every row keeps the original fields: `adId`, `adUrl`, `adTitle`, `brandName`, `cost`,
`ctr`, `like`, `industryKey`, `objectiveKey`, `isSearch`, `observedCountry`,
`observedPeriod`, `scrapedAt`, `videoCoverUrl`, `videoDuration`, `videoHeight`,
`videoWidth`, `videoId`, and `videoUrls`.

New fields are additive:

- `source`, `creativeCenterUrl`, `rank`, `foundInCountry`
- `costTier`, `industryName`, `parentIndustryName`, `objectiveName`, `adFormat`
- `landingPageUrl`, `targetCountries`, `commentCount`, `shareCount`, `adSource`,
  `objectives`, `voiceOver`
- `spotlightHighlight`, `retentionCurve`
- `videoUrlBest`, `videoUrlsExpireAt`
- `detailsFetched`, `detailUnavailable`, `availableTotal`

Empty fields are omitted. `0` and `false` are kept because they are real values.
`brandName="Not Mention"` and similar placeholders are omitted.

### Notes on the metrics

- `ctr` is TikTok's CTR score in percent units: `0.62` means `0.62%`.
- `cost` is a budget tier, not money: 0 = Low, 1 = Medium, 2 = High.
- `like` is an absolute count.
- `commentCount` and `shareCount` are detail fields; 0 is common and real.
- `videoUrls` are signed CDN URLs with a limited lifetime. `videoUrlsExpireAt` tells you
  when the earliest one expires. Download what you want to keep.
- `availableTotal` is TikTok's ranked-index size for the base query, not the number of
  rows the actor delivered.

## Use cases

- **Creative research** - build a swipe file of winning hooks, formats, and CTAs by
  market, industry, objective, and language.
- **Competitor monitoring** - see which brands and landing pages are appearing in the
  Top Ads boards for your vertical.
- **Benchmarking** - compare your CTR and likes with the top percentile bands TikTok
  publishes.
- **Trend tracking** - run weekly with `period=7` and watch new ads enter the board.
- **Creative briefs** - pull the retention curve to show where viewers drop off.

## FAQ

**Do I need a TikTok account or cookies?**
No. The actor signs an anonymous Creative Center session itself. It never asks for a
TikTok login, cookie, or API key.

**Why did I get fewer rows than `maxItems`?**
TikTok exposes 20 ads per board and up to 500 per query. The actor reads extra boards
when `sweep` is on, but some filter combinations have fewer unique ads. The run status
message reports how many boards were read and why it stopped.

**Can I search by keyword?**
TikTok's keyword search on Top Ads is login-only; an anonymous request returns zero
ads. This actor does not ship a keyword field. Use industry, objective, language, or a
specific ad ID instead.

**Why is `brandName` missing on some rows?**
TikTok often does not publish a brand name. It is present on roughly a quarter of rows
in our sample. The actor omits the field rather than guessing.

**Why does `adUrl` open the Top Ads dashboard?**
TikTok has no stable public per-ad deep link; its own ad detail links redirect to the
dashboard. `adId` is the stable key. `creativeCenterUrl` uses TikTok's canonical ad
route for reference.

**Are the video URLs permanent?**
No. They are signed CDN URLs that expire within hours. Download them promptly or use
`videoUrlsExpireAt`.

**Why do some industries return no ads?**
The 258-entry taxonomy includes niche child categories that TikTok may not have a board
for in a given market and period. Try the parent industry or a longer period.

**Is this affiliated with TikTok?**
No. This is an independent actor that reads publicly available Creative Center data. It
is not endorsed by or affiliated with TikTok or ByteDance.

## Limitations

- 20 ads per board, 500 per query.
- Keyword search is login-only and is not supported.
- Brand name and landing page are published for only some ads.
- Exact spend, impressions, reach, dates, and audience targeting are not in the public
  Creative Center payload.
- Media URLs expire.
- TikTok may change its internal signing scheme; the actor re-mints and can recover the
  signer from the live page bundle, but a future change can still require an update.

## Data source

TikTok Creative Center Top Ads at
`https://ads.tiktok.com/business/creativecenter/inspiration/topads/pc/en` and Top Ads
Spotlight at
`https://ads.tiktok.com/business/creativecenter/tiktok-topads-spotlight/pc/en`.
The actor calls the same public JSON endpoints the pages use and reads only publicly
available data.
