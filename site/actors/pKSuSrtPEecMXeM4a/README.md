# Yahoo Finance Market Data & Fundamentals Scraper

Give this actor a list of ticker symbols and it returns everything Yahoo Finance shows on a quote page in one structured record per ticker: live quote data, historical price candles, financial statements, dividends and splits, news, analyst ratings, and holder data. Works for stocks, ETFs, indices, currency pairs, and crypto.

## What this actor does

- Fetches a quote snapshot per ticker covering the company, intraday price, 52-week range, valuation ratios, and dividend yield
- Optionally pulls daily/weekly/monthly price history for a date range you choose
- Optionally pulls income statement, balance sheet, cash flow, dividends, splits, news, analyst recommendations, and institutional/mutual-fund holders
- Supports US equities, ETFs, foreign-suffix tickers, market indices, currency pairs, and crypto symbols
- Fields a ticker doesn't have data for are omitted; a ticker that fails entirely gets an `error` field instead of breaking the run

## Output per ticker

- `ticker` — uppercase ticker symbol
- `summaryUrl` — the ticker's Yahoo Finance page
- `companyName`, `shortName` — full and short company name
- `sector`, `industry`, `country` — classification fields
- `currency`, `exchange`, `quoteType` — quote currency, exchange code, and instrument type (`EQUITY`, `ETF`, `INDEX`, `CURRENCY`, `MUTUALFUND`, `CRYPTOCURRENCY`)
- `website`, `businessSummary` — company URL and description
- `marketCap`, `fullTimeEmployees` — company fundamentals
- `currentPrice`, `previousClose`, `open`, `dayHigh`, `dayLow` — intraday quote
- `fiftyTwoWeekHigh`, `fiftyTwoWeekLow` — 52-week range
- `volume`, `averageVolume` — share volume
- `beta`, `trailingPE`, `forwardPE`, `trailingEps` — valuation ratios
- `dividendYield`, `dividendRate` — current dividend stats
- `dayChange`, `dayChangePercent` — derived from current price vs. previous close
- `history` — OHLCV rows (`date, open, high, low, close, volume, dividends, stock_splits`), plus `historyCount`, when `includeHistory` is on
- `dividends`, `splits` — `{date, value}` rows, plus their counts, when their respective inputs are on
- `financials` — nested `{income, balance, cashflow, quarterly?}` blocks by period, when `includeFinancials` is on
- `news` — up to 25 `{title, url, publisher, publishedAt}` rows, plus `newsCount`, when `includeNews` is on
- `recommendations` — `{strongBuy, buy, hold, sell, strongSell}` analyst-rating summary, when `includeRecommendations` is on
- `earningsHistory` — up to 4 quarters of `{quarter, epsActual, epsEstimate, epsDifference, surprisePercent}`, when `includeEarningsHistory` is on
- `holders` — `{institutional, mutualFund}` arrays, when `includeHolders` is on
- `calendar` — upcoming earnings/dividend dates and analyst estimates, when `includeEarningsCalendar` is on
- `analystPriceTargets` — `{current, high, low, mean, median}`, when `includeAnalystPriceTargets` is on
- `insiderTransactions`, `insiderTransactionCount` — insider transactions (officers/directors/10%-owners) Yahoo currently lists for the ticker, when `includeInsiderTransactions` is on
- `options`, `optionExpirations` — next-expiration option chain and the next 20 expiry dates, when `includeOptions` is on
- `sustainability` — ESG scores, when `includeSustainability` is on and Yahoo publishes them for the ticker
- `error` — present instead of most other fields when the ticker couldn't be fetched (typo, delisted, regional restriction)
- `scrapedAt` — ISO 8601 UTC timestamp

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `tickers` | array | – | **Required.** Ticker symbols to fetch. |
| `startDate` | string | – | Earliest date for historical price data (`YYYY-MM-DD`); defaults to 30 days before today when left empty. |
| `endDate` | string | – | Latest date for historical price data (`YYYY-MM-DD`); defaults to today when left empty. |
| `interval` | string | `1d` | `1d`, `5d`, `1wk`, `1mo`, or `3mo`. |
| `includeHistory` | boolean | `true` | Include daily/weekly/monthly OHLCV candles. |
| `includeFinancials` | boolean | `false` | Include income statement, balance sheet, and cash flow. |
| `includeDividends` | boolean | `true` | Include dividend payment history. |
| `includeSplits` | boolean | `true` | Include stock split history. |
| `includeNews` | boolean | `true` | Include the latest news headlines (capped at 25). |
| `includeRecommendations` | boolean | `true` | Include the analyst recommendation breakdown. |
| `includeHolders` | boolean | `false` | Include institutional and mutual-fund holders (capped at 25 each). |
| `includeOptions` | boolean | `false` | Include the next-expiration option chain (capped at 50 strikes per side). |
| `includeEarningsCalendar` | boolean | `true` | Include upcoming earnings/dividend dates and analyst estimates. |
| `includeAnalystPriceTargets` | boolean | `true` | Include the analyst price-target summary. |
| `includeInsiderTransactions` | boolean | `false` | Include insider transactions (officers/directors/10%-owners) Yahoo currently lists. |
| `includeSustainability` | boolean | `false` | Include ESG scores, where Yahoo publishes them. |
| `includeQuarterlyFinancials` | boolean | `false` | Include quarterly statements under `financials.quarterly`. Only applies when `includeFinancials` is also on. |
| `includeEarningsHistory` | boolean | `true` | Include the last 4 quarters of EPS actual vs. estimate. |
| `concurrency` | integer | `4` | Number of tickers processed at once (1–16). |

### Example: quick quote and recent history for a watchlist

```json
{
  "tickers": ["AAPL", "MSFT", "GOOGL"],
  "startDate": "2026-01-01",
  "endDate": "2026-06-30",
  "interval": "1d",
  "includeHistory": true,
  "includeNews": true
}
```

### Example: full fundamentals for one company

```json
{
  "tickers": ["AAPL"],
  "includeFinancials": true,
  "includeQuarterlyFinancials": true,
  "includeHolders": true,
  "includeInsiderTransactions": true
}
```

### Example: options chain and analyst targets

```json
{
  "tickers": ["TSLA"],
  "includeOptions": true,
  "includeAnalystPriceTargets": true,
  "includeRecommendations": true
}
```

## Use cases

- **Watchlist monitoring** — pull live quote and fundamentals for every ticker on a schedule
- **Backtesting research** — bulk historical OHLCV data across an adjustable date range and interval
- **News tracking** — grab the latest headlines per ticker for keyword-based alerting
- **Income-portfolio modeling** — historical dividends and splits for yield calculations
- **Analyst-sentiment tracking** — sample recommendation and price-target data over time
- **Fundamental analysis** — structured income statement, balance sheet, and cash flow for spreadsheet work

## FAQ

**Does this need a proxy or API key?**
No. Quote and fundamental data is fetched without any account, signup, or API key.

**Can I get pre-market or after-hours prices?**
No. `currentPrice` and `volume` reflect the regular trading session only; extended-hours quotes aren't currently surfaced.

**What tickers are supported?**
Anything Yahoo Finance recognizes: US equities (`AAPL`, `MSFT`), ETFs (`SPY`, `QQQ`), foreign-suffix tickers (`BP.L` for London, `7203.T` for Tokyo), indices (`^GSPC`, `^DJI`), currency pairs (`EUR=X`), and crypto (`BTC-USD`).

**How fresh is the data?**
Quote fields are typically delayed about 15 minutes for US equities, matching Yahoo's free data terms. News is near real-time. Financials refresh within about a day of company filings. Historical candles update after market close.

**What happens if I enter a delisted or invalid ticker?**
That record comes back with an `error` field (`"no_data"` for a ticker Yahoo doesn't recognize, or the underlying exception name for a network/fetch failure) and the rest of its fields absent; the run continues normally for the other tickers.

**Why is the `financials` block sometimes missing?**
ETFs and indices don't report financial statements, some foreign tickers publish limited statements, and newly-listed companies may not have data yet. The field is simply omitted rather than returned empty.

**Why would `sustainability` be missing for a ticker I know has ESG data elsewhere?**
Yahoo's own ESG coverage is sparse — many tickers simply don't have a score published on Yahoo Finance, even if other sources track one.

**Is this affiliated with Yahoo?**
No. This is an independent, third-party actor that reads Yahoo Finance's publicly available data; it isn't affiliated with or endorsed by Yahoo.
