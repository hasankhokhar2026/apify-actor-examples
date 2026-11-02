# Full-Page Website Screenshot & PDF Capture

Hand this actor a list of URLs and get back a full-page screenshot or PDF for each one — with control over viewport size, lazy-load scrolling, page-load timing, and which elements (like cookie banners) to hide before the shot is taken.

## What this actor does

- Captures full-page screenshots as PNG images, or renders pages as printable PDF documents
- Lets you set a custom viewport width to test how a page looks at a given screen size
- Scrolls to the bottom of the page first, on request, so lazy-loaded images and infinite-scroll content appear in the capture
- Hides chosen elements (cookie banners, popups, ad slots) by CSS selector before the screenshot is taken
- Records the final URL after any redirects, alongside the URL you originally submitted

## Output per URL

- `startUrl` — the URL you originally submitted
- `url` — the final URL after any redirects
- `screenshotUrl` — public download link for the captured screenshot or PDF; `null` if the capture failed
- `screenshotKey` — the file's key in the run's key-value store; `null` if the capture failed
- `format` — `png` or `pdf`
- `status` — `success`, or an `error: ...` description if the capture failed
- `timestamp` — ISO 8601 timestamp of when the capture was taken

## Input

| Field | Type | Default | Description |
|---|---|---|---|
| `urls` | array | – | **Required.** Web page URLs to capture |
| `format` | string | `png` | Output format: `png` or `pdf` |
| `waitUntil` | string | `load` | Page-load condition to wait for: `load`, `domcontentloaded`, or `networkidle` |
| `delay` | integer | `0` | Milliseconds to wait after the page loads before capturing (0–3,600,000) |
| `viewportWidth` | integer | `1280` | Browser viewport width in pixels (100–3,840); height is fixed at 1080px |
| `scrollToBottom` | boolean | `false` | Scroll to the bottom of the page before capturing |
| `delayAfterScrolling` | integer | `2500` | Milliseconds to wait after scrolling, when `scrollToBottom` is enabled |
| `waitUntilNetworkIdleAfterScroll` | boolean | `false` | After scrolling, wait until no network activity for 500ms before capturing |
| `waitUntilNetworkIdleAfterScrollTimeout` | integer | `30000` | Maximum milliseconds to wait for network idle after scrolling |
| `proxyConfiguration` | object | – | Optional proxy settings; most sites don't need one |
| `selectorsToHide` | string | – | Comma-separated CSS selectors of elements to hide before capturing |

### Example: desktop screenshot with network-idle wait

```json
{
    "urls": [
        {"url": "https://www.example.com"},
        {"url": "https://news.ycombinator.com"}
    ],
    "format": "png",
    "waitUntil": "networkidle",
    "viewportWidth": 1920
}
```

### Example: PDF with lazy-load scrolling and a hidden popup

```json
{
    "urls": [
        {"url": "https://www.wikipedia.org"}
    ],
    "format": "pdf",
    "scrollToBottom": true,
    "selectorsToHide": ".cookie-banner, #popup"
}
```

## Use cases

- **Website monitoring** — schedule regular screenshots to track how a page's visual design changes over time
- **QA testing** — verify how a page renders at different viewport widths before a release
- **Archiving and compliance** — keep a visual record of a page's content on a given date
- **Competitive research** — capture competitor pages for design comparison
- **Bug reporting** — attach a real screenshot as visual evidence of a display issue
- **Content verification** — confirm published content actually appears correctly on the live page

## FAQ

**Do I need a proxy?** No — most publicly accessible sites work without one; only enable `proxyConfiguration` if a specific site blocks the capture.

**What's the difference between PNG and PDF?** PNG is a single full-page image including everything below the fold; PDF uses the page's print layout, which can paginate content differently than how it looks on screen.

**How do I hide a cookie banner?** Pass its CSS selector in `selectorsToHide`, e.g. `.cookie-banner, #gdpr-consent, [class*="cookie"]` — comma-separate multiple selectors.

**Can I control the viewport height?** No — height is fixed at 1080px, but the screenshot always captures the full page length regardless of viewport height.

**Why would I enable `scrollToBottom`?** Many pages only load images or sections as you scroll; scrolling first ensures that content has actually rendered before the capture happens.

**Can I capture multiple URLs in one run?** Yes — list as many URLs as you want in `urls`; each produces its own screenshot and dataset record.

**Can I simulate a mobile screenshot?** Yes — set `viewportWidth` to a mobile width such as 375 or 390.

**Can this capture pages that require a login?** No — it only captures what's visible to an anonymous visitor; it doesn't handle authentication.
