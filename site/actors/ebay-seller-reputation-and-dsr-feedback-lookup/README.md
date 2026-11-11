# eBay Seller Reputation & DSR Feedback Lookup

Look up **eBay** seller feedback and reputation from a seller's public feedback profile. Get individual
feedback entries (rating, comment, item, price, buyer context, verified-purchase status and public seller
replies), plus a seller profile summary with feedback score, positive percentage, member-since date,
1/6/12-month rating counts, all four Detailed Seller Ratings and store metadata such as items sold and
followers.

Use seller usernames, profile URLs or store URLs, choose one of 14 eBay marketplaces, filter by feedback
role, rating, period or item title/ID, and collect only feedback with buyer photos or only buyer-written
feedback when you need a cleaner dataset.

## What this actor does

- **Feedback rows** — one row per feedback entry: rating, comment, item title/URL/ID, price with currency,
  buyer context, verified-purchase flag, buyer photos, automated-feedback flag and public seller replies
- **Seller profile summaries** — one summary row per seller: feedback score, total feedback received,
  12-month positive percentage, member-since date, location, Top Rated / business / ID-verified / store
  badges, 1/6/12-month positive/neutral/negative counts and all four Detailed Seller Ratings
- **Store metadata** — store name, description, positive percentage, items sold, followers, store image and
  store URL when the seller runs an eBay Store
- **Marketplace selection** — United States, United Kingdom, Germany, Australia, Canada, France, Italy,
  Spain, Ireland, Netherlands, Poland, Switzerland, Austria and Belgium
- **Filters** — feedback role (seller/buyer/left for others), positive/neutral/negative rating, 1/6/12-month
  period, newest/relevance sort, item title or ID search, photos-only and automated-feedback toggle
- **Incremental collection** — stop each seller at feedback IDs you already have from a previous run
- **Clean records** — omit-empty output: fields eBay does not show for a record are left out, never sent as
  null or a placeholder

## Input

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `mode` | Select | `feedback` | `feedback` rows, `sellerProfile` summaries, or `both` |
| `sellerUsernames` | List | – | eBay usernames, member profile URLs or feedback profile URLs |
| `storeUrls` | List | – | eBay store URLs (`https://www.ebay.com/str/<seller>`); the URL's eBay site is used |
| `marketplace` | Select | `US` | eBay site for plain usernames and the default for store URLs |
| `feedbackType` | Select | `All` | All received feedback, received as seller, received as buyer, or left for others |
| `ratingType` | Select | `All` | All, Positive, Neutral or Negative |
| `period` | Select | `All` | All time, past month, past 6 months or past 12 months |
| `sortBy` | Select | `Newest` | Newest first or most relevant |
| `itemSearch` | Text | – | Only feedback for a matching item title or item ID |
| `imagesOnly` | Boolean | `false` | Only feedback entries with a buyer photo |
| `includePhotos` | Boolean | `false` | Fetch every buyer photo for entries with more than one |
| `includeAutomated` | Boolean | `true` | Include eBay's automated positive feedback entries |
| `maxItems` | Integer | `25` | Maximum feedback rows across all sellers |
| `maxFeedbackPerSeller` | Integer | `500` | Per-seller feedback cap |
| `maxPages` | Integer | `20` | Safety cap on feedback pages followed per seller |
| `stopAtFeedbackIds` | List | `[]` | Stop each seller at the first known feedback ID (the known row is excluded) |

At least one of `sellerUsernames` or `storeUrls` must be provided. If neither is given, the actor falls
back to a known-good seller so a run always produces real output.

The prefill is the cheapest run with output: one seller, all ratings and 3 rows.

## Output per feedback row (`recordType: "feedback"`)

| Field | Type | Description |
|-------|------|-------------|
| `feedbackId` | String | eBay's own identifier for the feedback entry |
| `sellerUsername` | String | The seller this feedback was left for |
| `marketplace` | String | The eBay site used (`US`, `UK`, `DE`, ...) |
| `feedbackRole` | String | `receivedAsSeller`, `receivedAsBuyer`, `leftForOthers` or `all` |
| `rating` | String | `positive`, `neutral` or `negative` |
| `comment` | String | The feedback comment |
| `itemTitle` | String | Title of the item the feedback refers to |
| `itemUrl` | String | Link to the item |
| `itemId` | String | eBay item ID |
| `priceFormatted` | String | Price as eBay displays it, e.g. "GBP 4.82" or "US $409.36" |
| `itemPriceValue` | Number | Numeric price |
| `itemPriceCurrency` | String | ISO currency code |
| `itemImageUrl` | String | Buyer-attached photo preview, when present |
| `itemImageUrls` | List | Buyer-attached photo URLs; one preview by default, every photo with `includePhotos` |
| `itemImageCount` | Integer | Number of buyer-attached photos |
| `buyerUsername` | String | Buyer name as eBay masks it (e.g. "r***c") |
| `buyerFeedbackCount` | Integer | Legacy name for the buyer's feedback score |
| `buyerFeedbackScore` | Integer | The buyer's feedback score |
| `buyerFeedbackStar` | String | Buyer's star level code, e.g. `RED_STAR` |
| `buyerFeedbackStarLabel` | String | Human-readable buyer star level |
| `buyerPrivateFeedback` | Boolean | True when eBay marks the buyer's profile private |
| `automatedFeedback` | Boolean | True for eBay's automated feedback entries |
| `verifiedPurchase` | Boolean | True when eBay marks a verified purchase |
| `dateRange` | String | eBay's relative time label, e.g. "Past month" |
| `replies` | List | Public seller replies: `{author, dateRange, comment}` |
| `sellerFeedbackScore` | Integer | Seller's overall feedback score |
| `sellerTotalFeedbackCount` | Integer | Total feedback entries eBay says the seller received |
| `sellerPositiveFeedbackPercent` | Number | 12-month positive percentage |
| `sellerPositiveFeedbackCount12Months` | Integer | Positive count behind the percentage |
| `sellerNegativeFeedbackCount12Months` | Integer | Negative count behind the percentage |
| `sellerPositiveRatingCount1Month` | Integer | Positive ratings, last month |
| `sellerPositiveRatingCount6Months` | Integer | Positive ratings, last 6 months |
| `sellerPositiveRatingCount12Months` | Integer | Positive ratings, last 12 months |
| `sellerNeutralRatingCount1Month` | Integer | Neutral ratings, last month |
| `sellerNeutralRatingCount6Months` | Integer | Neutral ratings, last 6 months |
| `sellerNeutralRatingCount12Months` | Integer | Neutral ratings, last 12 months |
| `sellerNegativeRatingCount1Month` | Integer | Negative ratings, last month |
| `sellerNegativeRatingCount6Months` | Integer | Negative ratings, last 6 months |
| `sellerNegativeRatingCount12Months` | Integer | Negative ratings, last 12 months |
| `sellerDsrAccurateDescription` | Number | "Accurate description" DSR average, out of 5 |
| `sellerDsrAccurateDescriptionRatingsCount` | Integer | Ratings behind that average |
| `sellerDsrReasonableShippingCost` | Number | "Reasonable shipping cost" DSR average |
| `sellerDsrReasonableShippingCostRatingsCount` | Integer | Ratings behind that average |
| `sellerDsrShippingSpeed` | Number | "Shipping speed" DSR average |
| `sellerDsrShippingSpeedRatingsCount` | Integer | Ratings behind that average |
| `sellerDsrCommunication` | Number | "Communication" DSR average |
| `sellerDsrCommunicationRatingsCount` | Integer | Ratings behind that average |
| `sellerMemberSince` | String | ISO member-since date |
| `sellerMemberSinceRaw` | String | eBay's original member-since wording |
| `sellerLocation` | String | Member location as eBay shows it |
| `sellerIsBusinessSeller` | Boolean | Registered as a business seller |
| `sellerIsIdVerified` | Boolean | ID-verified badge |
| `sellerIsStoreOwner` | Boolean | eBay Store badge |
| `sellerIsTopRated` | Boolean | Top Rated Seller badge |
| `sellerAvatarUrl` | String | Seller avatar URL |
| `sellerStoreUrl` | String | Seller's eBay Store URL |
| `sellerAutomatedFeedbackCount` | Integer | eBay automated-feedback count |
| `sellerRevisedFeedbackCount` | Integer | Revised feedback count |
| `sourceUrl` | String | Feedback profile URL |
| `scrapedAt` | String | ISO 8601 extraction timestamp |

## Output per seller profile (`recordType: "sellerProfile"`)

Seller profile rows carry the same `seller*` fields as feedback rows, plus:

| Field | Type | Description |
|-------|------|-------------|
| `sellerStoreName` | String | Store display name |
| `sellerStoreUrl` | String | Store URL |
| `sellerStoreDescription` | String | Store description |
| `sellerStorePositiveFeedbackPercent` | Number | Store positive-feedback percentage |
| `sellerStoreItemsSoldText` | String | Items sold as displayed, e.g. "51.7M" |
| `sellerStoreItemsSoldCount` | Integer | Items sold expanded to a number |
| `sellerStoreFollowersText` | String | Followers as displayed, e.g. "498K" |
| `sellerStoreFollowersCount` | Integer | Followers expanded to a number |
| `sellerStoreImageUrl` | String | Store image URL |

## Output per error row (`recordType: "error"`)

When a seller cannot be reached, does not exist or has no public feedback, the actor emits one error row
for that seller with `sellerUsername`, `marketplace`, `sourceUrl`, `error` and `scrapedAt`, then continues
with any other requested sellers.

## Examples

### Check one seller's recent feedback

```json
{
  "sellerUsernames": ["musicmagpie"],
  "maxItems": 50
}
```

### Audit negative feedback in the last 12 months

```json
{
  "sellerUsernames": ["discountcomputerdepot"],
  "ratingType": "Negative",
  "period": "Past12Months",
  "maxItems": 100
}
```

### Get seller profile summaries

```json
{
  "sellerUsernames": ["musicmagpie", "discountcomputerdepot"],
  "mode": "sellerProfile"
}
```

### Look up a seller by store URL on the UK site

```json
{
  "storeUrls": ["https://www.ebay.co.uk/str/musicmagpie"],
  "maxItems": 50
}
```

### Read feedback as a seller on the German site

```json
{
  "sellerUsernames": ["medimops"],
  "marketplace": "DE",
  "feedbackType": "Seller",
  "maxItems": 50
}
```

### Only feedback with buyer photos

```json
{
  "sellerUsernames": ["discountcomputerdepot"],
  "imagesOnly": true,
  "maxItems": 20
}
```

### Monitor new feedback with known IDs

```json
{
  "sellerUsernames": ["discountcomputerdepot"],
  "sortBy": "Newest",
  "stopAtFeedbackIds": ["2255274619024"],
  "maxItems": 100
}
```

### Search feedback for an item

```json
{
  "sellerUsernames": ["discountcomputerdepot"],
  "itemSearch": "Dell",
  "maxItems": 20
}
```

## Use cases

- **Seller due diligence** — read recent feedback, negative comments, replies and DSR scores before buying
- **Reputation audits** — track a seller's positive percentage, rating counts and DSR averages over time
- **Competitive benchmarking** — compare feedback volume, positive share and DSR across sellers
- **Complaint mining** — pull negative or neutral feedback and surface recurring shipping, condition or
  communication issues
- **Marketplace analytics** — collect the same seller across multiple eBay marketplaces
- **Research datasets** — export feedback rows with item, price and seller context for analysis

## Data source and reliability

This actor reads eBay's public seller feedback profiles (`https://www.ebay.<site>/fdbk/feedback_profile/<seller>`)
and public store pages. No login, cookies, API key or proxy setup is required, and none is accepted as
input. The actor handles connections automatically.

The actor tries eBay's feedback host and market site first, falls back to the public Google Translate
mirror when a market site serves a verification challenge, and keeps a muted headless-browser fallback for
the rare case where every HTTP path is blocked. Pages are fetched with retries and exponential backoff on
429/5xx. Pagination is server-side (`page_id`), so results are addressable and repeatable.

## Limitations

- **Exact feedback dates are not public.** eBay shows relative buckets ("Past month", "Past 6 months",
  "Past year", "More than a year ago"). The actor reports eBay's own wording and does not invent a date.
- **Buyer identities are masked by eBay.** The actor reports the public masked name (e.g. "r***c") and
  never attempts to unmask it.
- **No lifetime neutral total is published.** The actor reports the 1/6/12-month neutral counts that eBay
  publishes and does not infer a lifetime number.
- **Rating filters cover the last 12 months.** eBay only applies an overall-rating filter within that
  window; the actor requests the 12-month view when a rating filter is set with period "All".
- **Item-title/ID search cannot be combined with eBay's period or rating filters.** The actor searches the
  item title/ID and checks the rating (and period when possible) itself.
- **The public feedback list is finite.** eBay stopped serving older pages for some profiles; the actor
  stops cleanly at the source's last page or at your `maxPages` / `maxItems` cap and says so in the run
  status message.
- **Some sellers have no public feedback or a private profile.** Those sellers get an error row or a
  profile without the missing fields.
- **Item links are eBay listing pages.** A listing that has ended may return a 404/403 page even though the
  `itemUrl` is the canonical `/itm/<id>` link from eBay's feedback page; the feedback row itself remains
  valid.
- **Store metadata is only fetched in seller-profile modes.** Feedback-only runs include the store URL from
  the feedback page but not the store's items-sold/followers figures.
- **Full photo galleries need `includePhotos`.** eBay's feedback list exposes one preview per entry even when
  the buyer attached several photos. With `includePhotos`, the actor calls eBay's public feedback-detail
  endpoint once per entry that has more than one photo and returns the full gallery.
- **The Google Translate mirror can translate visible text when it is used as a fallback.** The actor
  requests the page in the marketplace's own language to keep comments in their original language; the
  direct eBay path is preferred.
- **The actor is not affiliated with eBay.** It reads only public pages and does not access private or
  login-gated data.

## FAQ

**Q: Do I need an eBay account or API key?**
A: No. The actor reads only public feedback and store pages.

**Q: Why is the buyer name partially hidden?**
A: eBay masks buyer names on public feedback profiles for privacy. The actor reports exactly what eBay
shows.

**Q: Why is there no exact feedback date?**
A: eBay publishes only relative time buckets for individual feedback entries on the public profile.

**Q: Can I get only seller feedback, not buyer feedback?**
A: Yes. Set `feedbackType` to `Seller`. Use `Buyer` or `LeftForOthers` for the other sides of the ledger,
or `All` for everything.

**Q: Can I get a seller's reputation without pulling every feedback row?**
A: Yes. Set `mode` to `sellerProfile`. You get one summary row per seller with the score, positive
percentage, rating counts, DSR and store metadata.

**Q: Can I collect the same seller on another eBay site?**
A: Yes. Set `marketplace` for plain usernames, or use a store URL on the site you want.

**Q: What happens when a seller does not exist?**
A: That seller gets a clear error row and the run continues with any other requested sellers.

**Q: Can I get every buyer photo?**
A: Yes. Set `includePhotos` to `true`; the actor fetches the public feedback-detail gallery for entries with
more than one photo. It adds one request per such entry.

**Q: Is there a row limit?**
A: Yes. `maxItems` caps rows across the run, `maxFeedbackPerSeller` caps one seller and `maxPages` is a
safety cap on pagination. eBay may also stop serving older pages.
