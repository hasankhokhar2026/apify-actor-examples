# Complete Page Capture - Screenshot & PDF

Capture complete full-page screenshots or PDFs of any URL list. This actor scrolls lazy content into view, waits for images and fonts, removes fixed headers and consent overlays, supports real device emulation, and tells you when a page was blocked or truncated instead of returning a broken image as a success.

## Why this actor

- **Complete captures** - scrolls through the page to trigger lazy images and infinite-scroll widgets, then captures with the page reset to the top.
- **Clean captures** - can hide fixed headers, overlays and common cookie banners before the shot without deleting sticky content cards.
- **Honest results** - reports HTTP status, page title, block reason, truncation, image failures and file metadata for every URL.
- **Real device modes** - desktop, laptop, tablet, iPhone, Pixel and Galaxy presets with the right viewport, user agent, touch support and pixel density.
- **Useful formats** - PNG, JPEG, WebP and PDF, with PDF paper size, orientation, margins, backgrounds and a one-page mode.
- **Bulk friendly** - concurrent captures, bounded retries, per-URL timeouts and a hard cap for very long or infinite pages.

## Quick start

```json
{
  "urls": [
    {"url": "https://www.apify.com/"},
    {"url": "https://en.wikipedia.org/wiki/World_War_II"}
  ],
  "format": "png",
  "device": "desktop",
  "scrollToBottom": true
}
```

Every URL produces one dataset record and one file in the run's key-value store. The `screenshotUrl` field is a public download link; no Apify token is needed to open it.

## Inputs

| Field | Default | What it does |
|---|---|---|
| `urls` | - | Required. URL list; accepts URL objects or plain strings. Bare domains use https. |
| `format` | `png` | `png`, `jpeg`, `webp` or `pdf`. |
| `quality` | `85` | JPEG/WebP quality, 1-100. |
| `fullPage` | `true` | Capture the whole scrollable page. Turn off for the first screen only. |
| `selector` | - | Capture one element by CSS selector instead of the page. |
| `device` | `custom` | `custom`, `desktop`, `desktop_hd`, `laptop`, `tablet`, `ipad`, `iphone_15`, `iphone_se`, `pixel_8`, `galaxy_s23`. |
| `viewportWidth` | `1280` | Width for `device=custom`, 100-3840. |
| `viewportHeight` | `1080` | Height for `device=custom`, 100-4320. |
| `deviceScaleFactor` | `1` | Pixel density for `device=custom`, 1-3. |
| `colorScheme` | `no-preference` | `no-preference`, `light` or `dark`. |
| `locale` | `en-US` | Browser language for localized pages. |
| `waitUntil` | `load` | `load`, `domcontentloaded`, `networkidle` or `commit`. |
| `waitForSelector` | - | Wait for a selector to become visible before capture. |
| `waitForImages` | `true` | Wait up to 5 seconds for images after scrolling. |
| `waitForFonts` | `true` | Wait up to 5 seconds for web fonts. |
| `delay` | `0` | Extra milliseconds after navigation. |
| `scrollToBottom` | `true` | Scroll through the page to trigger lazy content. |
| `maxScrollSteps` | `400` | Hard scroll-step cap. |
| `scrollStepPx` | `250` | Pixels per scroll step. |
| `delayAfterScrolling` | `1000` | Milliseconds to settle after scrolling. |
| `waitUntilNetworkIdleAfterScroll` | `false` | Wait for network idle after scrolling. |
| `waitUntilNetworkIdleAfterScrollTimeout` | `15000` | Network-idle timeout in milliseconds. |
| `hideFixedElements` | `false` | Hide fixed headers, full-screen overlays and chat widgets. Sticky content blocks stay in place. |
| `cookieBannerAction` | `hide` | `hide`, `accept` or `off`. |
| `selectorsToHide` | - | Extra comma/newline-separated CSS selectors to hide. |
| `pdfPageSize` | `web` | `web`, `a4`, `letter`, `legal`, `a3`, `a5` or `tabloid`. |
| `pdfLandscape` | `false` | Landscape PDF pages. |
| `pdfPrintBackground` | `true` | Include CSS backgrounds and colors in the PDF. |
| `pdfFitOnePage` | `false` | One tall PDF page instead of paginated paper. |
| `pdfMargin` | `none` | `none`, `narrow`, `normal` or `wide`. |
| `maxConcurrency` | `1` | URLs captured in parallel, 1-5. Use 1 for long pages at 2048 MB. |
| `maxRetries` | `1` | Retries for transient navigation failures and blocks. |
| `navigationTimeoutSecs` | `60` | Per-URL navigation and selector timeout. |
| `maxPageHeight` | `0` | Clip full-page images at this CSS height; 0 is unlimited. PDFs keep their full document height. |
| `proxyConfiguration` | - | Optional proxy override. The actor starts direct and escalates to an AUTO datacenter proxy only after a real block. |

## Output

Each dataset record contains:

| Field | Meaning |
|---|---|
| `startUrl` | URL you submitted. |
| `url` | Final URL after redirects. |
| `screenshotUrl` | Public download link for the file. |
| `screenshotKey` | Key of the file in the run's key-value store. |
| `format` | `png`, `jpeg`, `webp` or `pdf`. |
| `status` | `success` for a real stored capture, otherwise `error: ...`. |
| `timestamp` | ISO-8601 UTC capture time. |
| `pageTitle` | Page title at capture time. |
| `httpStatus` | Main document HTTP status. |
| `contentType` | Main response content type. |
| `blocked` / `blockReason` | Whether the page was a block, captcha or login wall, and which kind. |
| `errorType` | Machine-readable error category. |
| `device`, `viewportWidth`, `viewportHeight`, `deviceScaleFactor`, `colorScheme` | Rendering settings used. |
| `fullPage`, `selector` | Capture scope. |
| `imageWidth`, `imageHeight`, `fileSizeBytes` | File dimensions and size. |
| `pageHeight`, `capturedHeight`, `truncated` | Page height, captured height and whether a cap clipped it. |
| `pdfPages`, `pdfPageSize` | PDF page count and paper size. |
| `durationMs`, `imagesTotal`, `imagesFailed`, `retries` | Capture evidence. Image counts cover visible images only; hidden tracking pixels are ignored. |
| `warnings` | Human-readable notes such as failed images or a hit scroll cap. |

Blocked pages are not stored as screenshots and do not produce a success record. The record says `blocked: true` and `status: error: blocked (...)`, so a challenge page cannot be mistaken for page content.

## Examples

### Mobile screenshot

```json
{
  "urls": [{"url": "https://stripe.com/"}],
  "device": "iphone_15",
  "format": "jpeg",
  "quality": 85
}
```

### Full-page, dark PDF

```json
{
  "urls": [{"url": "https://tailwindcss.com/"}],
  "format": "pdf",
  "colorScheme": "dark",
  "pdfPageSize": "a4",
  "pdfFitOnePage": true,
  "cookieBannerAction": "hide"
}
```

### Capture one section

```json
{
  "urls": [{"url": "https://www.apify.com/"}],
  "selector": "main",
  "fullPage": false,
  "format": "png"
}
```

## What changed in this revamp

- `scrollToBottom` now defaults to `true` so lazy images are actually loaded.
- `hideFixedElements` defaults to `false`: resetting to the top already avoids repeated headers on most pages, and this keeps sticky content cards in the image. Turn it on to remove fixed headers/overlays.
- `cookieBannerAction` now defaults to `hide`.
- `maxConcurrency` now defaults to `1` for safe 2048 MB memory use; raise it only when you have memory headroom.
- The `screenshotUrl` field now returns a working public link.
- `waitUntil=domcontentloaded` is the prefill because `networkidle` can stall on analytics-heavy pages.
- Pages that return 403/captcha/login walls are reported as blocked errors, not successes.

You can turn each of these off from the input form.

## Limitations

- Only public, anonymous pages are supported. Login-protected pages are outside this actor's design.
- Some sites use CAPTCHA or bot defenses that cannot be bypassed. Those URLs are reported as blocked and are not charged as successful captures.
- Consent banners are handled on a best-effort basis. Hide is more reliable than click-accept; use `selectorsToHide` for a site-specific banner.
- Some lazy images never load because of the site's own rules or missing assets. Only visible images are counted in `imagesFailed` and listed in `warnings`; hidden tracking pixels and empty placeholders are ignored.
- Fixed headers are kept by default. Enable `hideFixedElements` to remove fixed headers, full-screen overlays and chat widgets; sticky content cards are intentionally preserved.
- Very long or infinite pages are capped by `maxScrollSteps` and `maxPageHeight`; the record sets `truncated: true` when a cap clips the capture.
- A direct PDF URL is copied when `format=pdf`; asking for an image of a PDF is reported as an error because Chromium downloads the file instead of rendering it.
- PDF pagination follows the browser's print layout, which can differ from the screen layout.

## FAQ

**Do I need a proxy?** No. The actor starts with a direct connection and only uses an AUTO datacenter proxy after a real block. If you supply your own proxy, it is used instead.

**Can I capture a page that requires a login?** No. Authenticated pages are intentionally out of scope.

**How do I hide a cookie banner?** Leave `cookieBannerAction` on `hide`. If a site uses a custom banner, add its selector to `selectorsToHide`.

**Why is a page reported as blocked?** The actor saw an HTTP 403/429/451, a CAPTCHA/Cloudflare challenge, or a login wall. The block page is not saved as a normal screenshot.

**Why is my image shorter than the page?** Check `truncated` and `warnings`. `maxPageHeight` or `maxScrollSteps` may have capped the capture.

**Can I capture multiple URLs?** Yes. Each URL produces its own record and file. Keep `maxConcurrency` at 1 for very long pages at 2048 MB; use a larger memory setting before raising concurrency.

**Can I make a single-page PDF?** Set `format=pdf` and `pdfFitOnePage=true`. For paper output, choose `pdfPageSize` and `pdfMargin`.
