#!/usr/bin/env python3
"""Extract ALL variant prices for a priceoye.pk product page - no browser needed.

The page embeds `window.product_data` as a JS object literal containing
product_config.dataPrices[colour][size] = [ {product_price, product_id, ...} ].

Usage:  python3 priceoye_variants.py https://priceoye.pk/mobiles/samsung/samsung-galaxy-a07
"""
import json
import sys
import urllib.request

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=40).read().decode("utf-8", "replace")


def extract_product_data(html):
    """Brace-match the JS object literal after `window.product_data`."""
    i = html.index("window.product_data")
    start = html.index("{", i)
    depth = 0
    instr = False
    esc = False
    for j in range(start, len(html)):
        c = html[j]
        if instr:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                instr = False
            continue
        if c == '"':
            instr = True
        elif c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return json.loads(html[start:j + 1])
    raise ValueError("unterminated product_data object")


def main():
    url = sys.argv[1]
    data = extract_product_data(fetch(url))
    cfg = data.get("product_config", {})
    print("PRODUCT:", data.get("product_title") or data.get("title"))
    print("URL:", data.get("url") or url)
    print("BRAND:", data.get("brand"), "| RATING:", data.get("average_rating"),
          "(count:", data.get("total_rattings_count"), ")")
    print("PRICE RANGE:", data.get("min_price"), "-", data.get("max_price"))
    print()

    prices = {}  # size -> set of prices across colours
    for colour, variants in cfg.get("dataPrices", {}).items():
        for size, offers in variants.items():
            for o in offers:
                prices.setdefault(size, set()).add(o["product_price"])

    print("=== ALL VARIANTS ===")
    for size in sorted(prices):
        vals = sorted(prices[size])
        print(f"  {size.upper():20} Rs. {', '.join(vals)}")


if __name__ == "__main__":
    main()