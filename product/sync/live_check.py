"""Re-read live Shopify variants and Amazon listings and compare with the target files.

python3 sync/live_check.py --dir output/phase1   -> writes <dir>/live_check.csv
"""
import argparse
import csv
import os
import sys
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import ShopifyClient  # noqa: E402
from amazon import AmazonClient  # noqa: E402


def same(expected, live):
    e, l = ("" if expected is None else str(expected)), ("" if live is None else str(live))
    try:
        return Decimal(e) == Decimal(l)
    except Exception:
        return e == l


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    a = ap.parse_args()
    shop = ShopifyClient()
    amz = AmazonClient()
    rows = []

    targets = list(csv.DictReader(open(os.path.join(a.dir, "shopify_updates.csv"), encoding="utf-8")))
    products = shop.all_products(limit=10)
    live_v = {v["id"]: (v, pr) for pr in products for v in pr["variants"]}
    levels = {l["inventory_item_id"]: l["available"]
              for l in shop.inventory_levels([v["inventory_item_id"] for v, _ in live_v.values()])}
    seen = set()
    for t in targets:
        vid = int(t["variant_id"])
        seen.add(vid)
        v, pr = live_v.get(vid, (None, None))
        live = {"sku": v and v["sku"], "price": v and v["price"], "barcode": v and (v["barcode"] or ""),
                "inventory": v and levels.get(v["inventory_item_id"]), "status": pr and pr["status"]}
        for f in ("sku", "price", "barcode", "inventory", "status"):
            rows.append({"channel": "shopify", "item": f"{t['stock_code']} ({t['role']})",
                         "key": vid, "field": f, "expected": t[f"new_{f}"], "live": live[f],
                         "match": "yes" if same(t[f"new_{f}"], live[f]) else "NO"})
    for vid, (v, pr) in live_v.items():
        if vid not in seen:
            rows.append({"channel": "shopify", "item": v["sku"], "key": vid, "field": "variant",
                         "expected": "(not in target files)", "live": "present", "match": "NO"})

    feed = list(csv.DictReader(open(os.path.join(a.dir, "amazon_price_quantity.txt"), encoding="utf-8"),
                               delimiter="\t"))
    fmap = {"price": "price", "minimum-seller-allowed-price": "minimumSellerAllowedPrice",
            "maximum-seller-allowed-price": "maximumSellerAllowedPrice", "quantity": "quantity",
            "handling-time": "handlingTime", "fulfillment-channel": "fulfillmentChannel"}
    for r in feed:
        live = amz.get_listing(r["sku"])
        for f, lf in fmap.items():
            exp = r[f]
            lv = live.get(lf)
            if r["fulfillment-channel"] == "AMAZON_EU" and f in ("quantity", "handling-time"):
                exp = "(not sent; Amazon-managed)"
                ok = lv is None or f == "handling-time"
                rows.append({"channel": "amazon", "item": r["sku"], "key": r["sku"], "field": f,
                             "expected": exp, "live": "null" if lv is None else lv,
                             "match": "yes" if ok else "NO"})
                continue
            rows.append({"channel": "amazon", "item": r["sku"], "key": r["sku"], "field": f,
                         "expected": exp, "live": lv, "match": "yes" if same(exp, lv) else "NO"})

    path = os.path.join(a.dir, "live_check.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["channel", "item", "key", "field", "expected", "live", "match"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(rows)
    bad = [r for r in rows if r["match"] != "yes"]
    for ch in ("shopify", "amazon"):
        n = sum(1 for r in rows if r["channel"] == ch)
        nb = sum(1 for r in bad if r["channel"] == ch)
        print(f"{ch}: {n} checks, {nb} mismatches")
    for r in bad:
        print("  MISMATCH", r)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
