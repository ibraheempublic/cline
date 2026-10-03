# Samsung Galaxy A07 — variant prices, priceoye.pk

Source: <https://priceoye.pk/mobiles/samsung/samsung-galaxy-a07> (product ID 11683)
Retrieved: 2026. Rating 4.9 (841 ratings). Brand: Samsung.

## All 3 variants

| Variant | Price (PKR) |
|---|---|
| 64GB — 4GB RAM  | **Rs. 35,495** |
| 128GB — 4GB RAM | **Rs. 42,495** |
| 128GB — 6GB RAM | **Rs. 51,495** |

Price range across variants: Rs. 35,495 – Rs. 51,495.
Prices are identical across colours (`black`, `light_violet`).

## How this was obtained — no browser needed

Two things that would normally require a headless browser, but don't here:

1. **The rendered markup is server-side.** The storage/RAM variant selector is real
   HTML in the response:
   ```html
   <div class="h4">Storage</div>
   <ul class="sizes colors">
     <li class="size-item active ..."><a class="ga-dataset 64gb - 4gb ram active">…</a>
     <span class="">64GB - 4GB RAM</span></li>
     <li class="size-item ..."><span class="">128GB - 4GB RAM</span></li>
     <li class="size-item ..."><span class="">128GB - 6GB RAM</span></li>
   </ul>
   ```
   (The active variant is `64gb - 4gb ram` — that's why a naive scrape of `<title>`/
   meta/JSON-LD shows only **Rs. 35,495** and looks like the phone has one price.)

2. **The per-variant price table is embedded as a JS global** in the HTML, so no
   XHR / JS execution is required to read it:
   ```html
   <script> window.product_data = {"product_config":{"dataPrices":{
     "black":{"64gb - 4gb ram":[{"product_id":11683,"flavor_id":25406,
              "product_price":"35,495", ...}],
              "128gb - 4gb ram":[{"product_price":"42,495", ...}],
              "128gb - 6gb ram":[{"product_price":"51,495", ...}]},
     "light_violet":{ ... same 3 sizes ... }}}, ... };
   </script>
   ```
   The page's **JSON-LD `Product/Offer` block only advertises the selected variant**
   (`"price":"35495.00"`) — it is *not* a source for all variants. Use `dataPrices`.

## Extraction recipe (pure curl + Python, no headless browser)

```python
import json, re, urllib.request

req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 ... Chrome/126.0 Safari/537.36'})
s = urllib.request.urlopen(req, timeout=40).read().decode('utf-8', 'replace')

# window.product_data is a JS object literal -> brace-match, then json.loads
i = s.index('window.product_data'); start = s.index('{', i)
depth = instr = esc = False; depth = 0
for j in range(start, len(s)):
    c = s[j]
    if instr:
        if esc: esc = False
        elif c == '\\': esc = True
        elif c == '"': instr = False
        continue
    if c == '"': instr = True
    elif c == '{': depth += 1
    elif c == '}':
        depth -= 1
        if depth == 0: end = j + 1; break

d = json.loads(s[start:end])
for colour, variants in d['product_config']['dataPrices'].items():
    for size, offers in variants.items():
        for o in offers:
            print(colour, size, 'Rs.', o['product_price'])
```

Note: a non-greedy regex like `(\{.*?\});` **fails** here (`Extra data` / truncated
JSON at char ~108k) — the object is large and contains nested `{...}` plus `;`
inside strings. Brace-matching as above is required.

Also useful in `product_data`: `min_price` / `max_price` (here `35,495` / `51,495`)
give the variant range directly.

## Generalises to other models
Every product page `/mobiles/<brand>/<slug>` carries `window.product_data`, so
variant pricing for other phones can be extracted the same way from raw HTML.