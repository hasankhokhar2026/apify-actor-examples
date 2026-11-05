# Google Fonts Library Metadata Extractor

Get structured metadata for Google's free, open-source font library instead of reading it off the fonts.google.com catalog by hand. Look a family up by name, pull every family in one of the five categories, or export the whole library at once, with weights, variable-font axes, language subsets, designer credits, and ready-to-paste specimen and CSS embed URLs.

## What this actor does

- **Three modes:** `byFamily`, `byCategory`, `listAll`
- **Every family:** weights, style variants, variable-font axes, language subsets, designers
- **Ranking signals:** popularity and trending positions across the whole library
- **Ready-to-use URLs:** a specimen page URL and a `css2` embed URL for each family
- **Empty fields are always omitted** — records only contain data that actually exists

## Output per font family

| Field | Description |
|---|---|
| `family` | Font family name (e.g. `Roboto`, `Open Sans`) |
| `displayName` | A display-friendly variant of the family name, when Google Fonts publishes one separate from `family` |
| `category` | `Sans Serif` / `Serif` / `Display` / `Handwriting` / `Monospace` |
| `stroke` | Stroke classification when present (e.g. `Sans Serif`, `Slab Serif`) |
| `classifications` | Secondary tags (e.g. `Display`, `Monospace`, `Symbols`) |
| `subsets` | Language / script subsets (e.g. `latin`, `cyrillic`, `greek`, `vietnamese`) |
| `weights` | Distinct numeric weights (e.g. `["100","400","700","900"]`) |
| `variants` | All style variants incl. italics (e.g. `["400","400i","700"]`) |
| `axes` | Variable-font axes: `[{tag, min, max, defaultValue}]` |
| `isVariable` | `true` when the family ships a variable font |
| `designers` | List of designer / foundry names |
| `popularity` | Popularity rank across the library (lower = more popular) |
| `trending` | Trending rank across the library |
| `dateAdded` | Date the family was first added to Google Fonts |
| `lastModified` | Date the family was last updated |
| `primaryScript` / `primaryLanguage` | Primary script / language when set |
| `colorCapabilities` | Color-font tech when present (e.g. `COLRV1`, `OTSVG`) |
| `isOpenSource` | `true` when Google Fonts marks the family open source in its metadata (true on virtually every family, since the whole library is open source) |
| `isBrandFont` | `true` when Google Fonts flags this family as a brand font |
| `isNoto` | `true` when the family is part of the Noto font collection |
| `googleFontsUrl` | Specimen page, e.g. `https://fonts.google.com/specimen/Open+Sans` |
| `cssUrl` | Embed stylesheet, e.g. `https://fonts.googleapis.com/css2?family=Open+Sans` |
| `recordType` | `font` |
| `scrapedAt` | ISO-8601 timestamp of the scrape |

## Output per failed lookup (recordType = `error`)

When a requested family name in `families` doesn't match any family in the library (mode=`byFamily`), the actor emits a typed error record instead of silently skipping it:

| Field | Description |
|---|---|
| `error` | Short error type, e.g. `not_found` |
| `message` | Human-readable explanation |
| `input` | The family name that didn't match |
| `sourceUrl` | The Google Fonts metadata endpoint queried |
| `scrapedAt` | ISO-8601 timestamp |

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `mode` | string | `byFamily` | `byFamily` / `byCategory` / `listAll` |
| `families` | array | `["Roboto"]` | Exact family names (mode=byFamily), case-insensitive |
| `category` | string | `Sans Serif` | One category (mode=byCategory) |
| `maxItems` | integer | `50` | Hard cap on emitted records (1–2000) |

### Example: look up specific families

```json
{
  "mode": "byFamily",
  "families": ["Roboto", "Open Sans", "Playfair Display", "JetBrains Mono"]
}
```

### Example: browse every monospace font

```json
{
  "mode": "byCategory",
  "category": "Monospace",
  "maxItems": 100
}
```

### Example: export the whole library

```json
{
  "mode": "listAll",
  "maxItems": 2000
}
```

## Use cases

- **Design systems** — build a searchable, filterable font picker from live Google Fonts data
- **Web performance** — pull the exact `css2` URLs and weights you need before self-hosting
- **Typography research** — analyse the library by category, popularity, or variable-font support
- **App onboarding** — offer users a curated font list without hand-maintaining metadata
- **SEO / content tooling** — enrich articles and galleries with accurate font specifications
- **Localization** — filter families by language subset (Cyrillic, Greek, Vietnamese, and more)

## FAQ

**Where does the data come from?**  The official public Google Fonts metadata catalog that powers [fonts.google.com](https://fonts.google.com). No login or API key is required.

**How many fonts are covered?**  The entire library — over 1,900 families and growing. `listAll` returns all of them (up to `maxItems`).

**What are the categories?**  `Sans Serif`, `Serif`, `Display`, `Handwriting`, and `Monospace`.

**What's the difference between `weights` and `variants`?**  `weights` lists the distinct numeric weights (e.g. `400`, `700`). `variants` lists every shipped style, including italics (e.g. `400`, `400i`, `700`, `700i`).

**What are `axes`?**  For variable fonts, the adjustable axes — such as `wght` (weight), `wdth` (width), `slnt` (slant), or `opsz` (optical size) — each with its `min`, `max`, and `defaultValue`.

**How do I embed a font?**  Use the `cssUrl` in a `<link>` tag, then reference the `family` in your CSS `font-family`. You can add `:wght@...` to the URL to request specific weights.

**Are these fonts free to use?**  Yes. Every Google Font is open source (licensed under the SIL Open Font License or Apache License 2.0) and free for commercial and personal use.

**How fresh is the data?**  Live — the actor fetches the current metadata document on every run, so new families and updates appear as soon as Google publishes them.

**Is this affiliated with Google?**  No. This is an independent, third-party actor that reads Google Fonts' publicly available library metadata and is not affiliated with or endorsed by Google.
