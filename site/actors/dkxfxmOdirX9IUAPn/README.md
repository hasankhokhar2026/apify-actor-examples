# Amazon Creator Storefront & Idea List Scraper

Amazon-approved influencers run affiliate storefronts at `amazon.com/shop/{handle}` to recommend products to their audience. This actor pulls the creator's profile and affiliate disclosure, every curated "Idea List" with its products and prices, and the creator's shoppable videos. No login required — these are public pages.

## What this actor does

- **Profile info** — display name, bio, profile image, affiliate disclosure text
  ("Earns revenue"), and which tabs (Profile / Idea Lists / Videos) the shop exposes
- **Idea Lists** — every curated product collection the creator has published, with
  both the *declared* item count (from the list header) and the *actual* number of
  unique products we could extract — these can legitimately differ
- **Idea List products** — ASIN, title, brand, price, discount, delivery text, badge,
  and creator comments where shown
- **Creator videos** — title, duration, thumbnail, tagged product ASIN, and like count
- **Inactive-shop detection** — inactive storefronts return an explicit
  `INACTIVE_STOREFRONT` status record instead of fabricated or unrelated content
- **Empty fields are omitted** — the dataset never contains `null`, `""`, or `[]`

## Output

This actor emits four record types (`recordType` field), distinguished in one dataset.

### Shop profile (`recordType: "shopProfile"`)

- `handle`, `shopUrl`
- `status` — `ACTIVE`, `INACTIVE_STOREFRONT`, `NOT_FOUND`, or `BLOCKED`
- `displayName`, `bio`, `profileImage`, `coverImage`
- `affiliateDisclosure` — verbatim disclosure text Amazon requires creators to show
- `availableTabs[]` — which of `profile` / `ideaLists` / `videos` the shop exposes
- `associateTag` — the creator's Amazon Associates tracking ID (e.g. `amandacerny07-20`),
  parsed from the `tag=` query param shared by every outgoing product/Idea-List link on
  the page; only emitted when every link on the page agrees on a single tag value
- `listCount`, `videoCount` — totals found on the profile page
- `marketplace` — `{countryCode, domain, marketplaceId, currency, language}`
- `requestContext` — `{sourceUrl, canonicalUrl}`
- `scrapedAt`

### Idea List summary (`recordType: "ideaListSummary"`)

- `handle`, `listId`, `title`, `url`, `image`, `position`
- `declaredItemCount` — item count shown on the list card/header
- `extractedItemCount` — unique ASINs actually extracted (only present when
  `crawlIdeaLists=true`) — **may legitimately differ from `declaredItemCount`**
  (some items in a list can be unavailable-in-this-variant placeholders, or the DOM
  virtualizes lazily-loaded items)
- `marketplace`, `requestContext`, `scrapedAt`

### Idea List item (`recordType: "ideaListItem"`)

- `handle`, `listId`, `listTitle`, `position`
- `asin`, `title`, `brand`, `url`, `image`
- `price`, `listPrice` — `{value, currency, display}`, omitted when unparseable
- `deliveryText` — delivery/shipping estimate text
- `availabilityText`, `isAvailable` — only set when Amazon shows explicit
  unavailable-in-this-variant text; never fabricated from a missing price
- `badge` — e.g. `Best Seller`, `Amazon's Choice`
- `creatorComment` — the creator's own note on the item, when shown
- `marketplace`, `requestContext` (includes `selectedAsin`), `scrapedAt`

### Creator video (`recordType: "creatorVideo"`)

- `handle`, `contentId`, `title`, `durationText`, `position`
- `videoStreamUrl` — HLS manifest URL, `thumbnailImage`
- `productAsin`, `relatedAsins[]` — tagged/related products
- `heartCount` — likes shown on the video
- `marketplace`, `requestContext`, `scrapedAt`

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `handles` | array | `[]` | Creator handles, e.g. `gearvlogz` |
| `shopUrls` | array | – | Full shop URLs, e.g. `https://www.amazon.com/shop/gearvlogz` |
| `marketplaceDomain` | string | `amazon.com` | Amazon domain used to build URLs from `handles` |
| `tabs` | string | `all` | `all` / `profile` / `ideaLists` / `videos` |
| `crawlIdeaLists` | boolean | `true` | Open each Idea List and extract its products |
| `maxLists` | int | `10` | Max Idea Lists per shop (1–50) |
| `maxItemsPerList` | int | `30` | Max products per Idea List (1–100) |
| `maxVideos` | int | `20` | Max videos per shop (1–100) |
| `useResidentialProxy` | boolean | `false` | Force residential proxy from the start |
| `proxyConfiguration` | object | AUTO | Apify proxy config (defaults to the free datacenter group) |

### Example: default — profile, Idea Lists, and videos

```json
{
  "handles": ["gearvlogz"],
  "tabs": "all",
  "maxLists": 5,
  "maxItemsPerList": 20
}
```

### Example: Idea List summaries only, no item drill-down

```json
{
  "handles": ["gearvlogz"],
  "tabs": "ideaLists",
  "crawlIdeaLists": false
}
```

### Example: multiple shops via full URLs on a non-US marketplace

```json
{
  "shopUrls": [
    "https://www.amazon.co.uk/shop/somecreator"
  ],
  "tabs": "profile"
}
```

## Use cases

- **Affiliate/influencer research** — see which products a creator recommends and at
  what price point
- **Competitive monitoring** — track a competitor brand's influencer partnerships
- **Product discovery** — mine curated Idea Lists for trending or niche products
- **Content strategy** — see which creators are active, which have the largest Idea
  List catalogs, and which videos get the most engagement

## FAQ

**What is a creator/influencer storefront?**
It's a public Amazon page (`amazon.com/shop/{handle}`) where an approved Amazon
Influencer curates products into an affiliate-linked profile. It's distinct from a
Brand Store (run by a manufacturer) and a third-party Seller's storefront.

**Why do `declaredItemCount` and `extractedItemCount` sometimes differ?**
Amazon's Idea Lists can include items that have gone out of stock in a variant/style
and show as "may be unavailable" placeholders, and the product grid can be
lazily/virtually rendered. We report both numbers honestly rather than forcing them
to match.

**What happens for an inactive creator shop?**
Amazon shows the explicit text "This Influencer Storefront is not active." for
creators who registered but never published a shop, or later deactivated it. The
actor emits a single `shopProfile` record with `status: "INACTIVE_STOREFRONT"` and
stops for that handle — it never substitutes an unrelated recommendation carousel.

**Do I need a proxy or login?**
No login is required. A proxy is optional — leave `useResidentialProxy` off to use the default configuration, or enable it for higher reliability on larger runs.

**Is this affiliated with Amazon?**
No — this is an independent third-party actor that reads Amazon's public storefront
pages.

**Does this work on non-US Amazon marketplaces (`amazon.co.uk`, `amazon.de`, etc.)?**
`marketplaceDomain`/`shopUrls` accept any of Amazon's 23 marketplace domains, and the
actor will correctly report a real, honest `NOT_FOUND` status for one if it doesn't
exist — but in practice, across extensive live testing, Amazon's Influencer/Creator
Storefront program (`/shop/{handle}`) has only ever been found live on `amazon.com`.
The non-US options are kept for forward compatibility (in case Amazon expands the
program, or you have a specific non-US `shopUrl` we haven't tested), not because a
working non-US storefront is currently known to exist.

**Why does the product URL (`url` on `ideaListItem`) return a 503 when I curl it directly?**
Amazon's `/dp/{asin}` pages reject requests with no `User-Agent` header (or a
non-browser one) with a 503, regardless of this actor. The link is valid and opens
normally in any browser or with a realistic `User-Agent` header set — it's an
Amazon-side anti-bot check on the request, not a broken link.
