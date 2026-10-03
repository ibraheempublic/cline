# Browsing priceoye.pk from this sandbox

## Question
Do we have a headless browser, and can we browse https://priceoye.pk?

## Findings (2026)

### Headless browser: NO (not usable)
- No browser was pre-installed. Only Node v24 and Python 3.11.
- Playwright (npm) **is** installable and the registry is reachable:
  `npm i -D playwright@1.63.0 && npx playwright install chromium` → downloads
  `chrome-headless-shell-linux64` (~114 MiB) + ffmpeg successfully.
- But Chromium **cannot launch** — missing system shared libraries:
  ```
  error while loading shared libraries: libglib-2.0.so.0: cannot open shared object file
  ```
- `npx playwright install --with-deps` fails: it needs to become root
  (`su: Authentication failure`). We run as `node` (uid 1000), no `sudo` binary.
- Local-lib workaround also dead: `apt-get download` fails with
  `Unable to locate package ...` (no package indexes, and no root to `apt-get update`).
  `ldconfig -p` shows 0 of libglib / libnss3 / libgbm present.

### Browsing over plain HTTP: YES ✔
The site is **server-rendered** (Drupal-ish), so `curl` retrieves fully-formed HTML —
no JS execution required.

Verified with a desktop Chrome User-Agent:

| URL | Status | Rendered title |
|---|---|---|
| `https://priceoye.pk` | 200 (1.29 MB) | `Lowest Mobile Price In Pakistan - Priceoye` |
| `https://priceoye.pk/mobiles/apple` | 200 | `Latest Price List of Apple Mobile Phones in Pakistan \| Priceoye` |
| `https://priceoye.pk/search?q=iphone%2015` | 200 | (search results) |
| `https://priceoye.pk/mobiles/samsung` | 200 | (category listing) |

Prices (`Rs. 1,23,456` form) and product links are present in the raw HTML.

### Useful structure observed
- Category listings: `/mobiles/<brand>` (apple, samsung, honor, infinix, itel, kxd,
  motorola, nokia, nothing, oppo, qmobile, realme, sego, faywa, gfive, …)
- Price-range buckets: `/mobiles/pricelist?price_range=25000to40000` etc.
- Search: `/search?q=<query>`
- Static assets on `https://static.priceoye.pk/js/*.min.js`

## Caveats
- JS-only widgets (lazy-loaded sections, add-to-cart, login, BNPL flows) may not
  appear in the static HTML — those would need a real browser.
- If a headless browser becomes necessary, the blocker is purely OS packages
  (root/apt). Any image that ships `libglib2.0-0 libnss3 libgbm1 libasound2 libx11-6`
  will let `/workspace/scripts/browse.mjs` run as-is.
