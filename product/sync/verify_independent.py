"""Independent re-computation for verification. Deliberately does NOT import rules.py,
build.py or the API clients: money is integer pence, and the expected values come
straight from the raw inputs, the client update and supplier_map.csv.

python3 sync/verify_independent.py --dir output/final --final     (with client update)
python3 sync/verify_independent.py --dir output/phase1            (phase 1 inputs)
Add --live to also compare the live APIs with the files.
"""
import argparse
import csv
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
problems = []


def bad(msg):
    problems.append(msg)
    print("  MISMATCH:", msg)


def pence(s):
    s = s.strip()
    neg = s.startswith("-")
    s = s.lstrip("-")
    whole, _, frac = s.partition(".")
    frac = (frac + "00")[:3]          # keep a third digit for rounding
    v = int(whole or 0) * 1000 + int(frac)
    return (-v if neg else v)         # thousandths of a pound


def round_half_up_thousandths(x):     # thousandths -> pence, half up
    return (x + 5) // 10


def to_str(p):
    return f"{p // 100}.{p % 100:02d}"


def ean_ok(b):
    if len(b) != 13 or not b.isdigit():
        return False
    s = 0
    for i in range(12):
        s += int(b[i]) * (3 if i % 2 else 1)
    return (10 - s % 10) % 10 == int(b[12])


def charm_p(p):
    r = p % 100
    if r == 99:
        return p
    if r == 0:
        return p - 1
    return p - r + 99


def up99(x_thousandths):
    """lowest .99 price (pence) whose value >= x (x in thousandths of a pound)."""
    pounds = x_thousandths // 1000
    cand = pounds * 100 + 99
    while cand * 10 < x_thousandths:
        cand += 100
    return cand


def load(dirname):
    def rd(name, delim=","):
        with open(os.path.join(dirname, name), encoding="utf-8", newline="") as f:
            return list(csv.DictReader(f, delimiter=delim))
    return rd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--final", action="store_true")
    ap.add_argument("--live", action="store_true")
    a = ap.parse_args()
    rd = load(a.dir)

    # ---- raw inputs
    raw = open(os.path.join(ROOT, "sage_stock_export.csv"), "rb").read().decode("cp1252").splitlines()
    hdr = raw[0].split(",")
    sage = {}
    for line in raw[1:]:
        cells = line.split(",")
        if not cells[0].strip():
            continue
        r = dict(zip(hdr, cells))
        sage[r["Stock Code"].strip()] = r
    stock = {c: int(r["Qty In Stock"]) for c, r in sage.items()}
    alloc = {c: int(r["Qty Allocated"]) for c, r in sage.items()}
    discontinued = set()
    fba_path = os.path.join(ROOT, "amazon_fba_inventory_report.txt")
    if a.final:
        for r in csv.DictReader(open(os.path.join(ROOT, "client_update", "stocktake_2026-10-09.csv"),
                                     encoding="utf-8-sig")):
            stock[r["stock_code"]] = int(r["counted_qty"])
        discontinued = {"NHG-1081"}
        fba_path = os.path.join(ROOT, "client_update", "amazon_fba_inventory_report_2026-10-10.txt")
    maps = {r["part_ref"]: pence(r["map"]) // 10 for r in rd("supplier_map.csv")}
    tiers = [(pence(r["max_weight_kg"]), pence(r["fee_gbp"]) // 10)
             for r in csv.DictReader(open(os.path.join(ROOT, "fba_fee_tiers.csv")))]
    listings = list(csv.DictReader(open(os.path.join(ROOT, "amazon_all_listings_report.txt"), encoding="utf-8"),
                                   delimiter="\t"))
    fba_rep = {r["sku"]: r for r in csv.DictReader(open(fba_path, encoding="utf-8"), delimiter="\t")}

    master = {r["stock_code"]: r for r in rd("master_products.csv")}
    feed = rd("amazon_price_quantity.txt", "\t")
    shop = rd("shopify_updates.csv")
    cross = rd("crosswalk.csv")
    sage_upd = rd("sage_updates.csv")

    print(f"== {a.dir}: {len(master)} master rows, {len(feed)} feed rows, {len(shop)} shopify rows")
    if set(master) != set(sage):
        bad(f"master codes {sorted(set(master) ^ set(sage))}")

    # ---- barcodes: every barcode in every file is a valid EAN-13
    n_bc = 0
    for c, r in master.items():
        n_bc += 1
        if not ean_ok(r["correct_barcode"]):
            bad(f"{c} master barcode {r['correct_barcode']} invalid")
    for r in shop:
        n_bc += 1
        if r["new_barcode"] and not ean_ok(r["new_barcode"]):
            bad(f"shopify {r['variant_id']} barcode {r['new_barcode']} invalid")
    for r in sage_upd:
        n_bc += 1
        if not ean_ok(r["correct_value"]):
            bad(f"sage_updates {r['stock_code']} {r['correct_value']} invalid")
    print(f"  barcodes checked: {n_bc}")
    # barcode choice re-derived by hand-listed expectations from the evidence
    expected_bc = {
        "NHG-1003": ("5060213450035", "shopify"), "NHG-1050": ("5060213450509", "shopify"),
        "NHG-1042": ("5060213450424", "shopify"), "NHG-1061": ("5060213450615", "shopify"),
        "NHG-1081": ("5060213450813", "shopify"), "NHG-1090": ("0841234509064", "sage"),
    }
    for c, r in master.items():
        exp = expected_bc.get(c)
        if exp is None:
            sb = sage[c]["Barcode"].strip()
            exp = (sb, "sage")
            if not ean_ok(sb):
                bad(f"{c}: Sage barcode {sb} invalid but not in expected override list")
        if (r["correct_barcode"], r["barcode_source"]) != exp:
            bad(f"{c} barcode {r['correct_barcode']}/{r['barcode_source']} expected {exp}")
    if sorted((r["stock_code"], r["correct_value"]) for r in sage_upd) != [
            ("NHG-1042", "5060213450424"), ("NHG-1061", "5060213450615"), ("NHG-1081", "5060213450813")]:
        bad(f"sage_updates rows {[(r['stock_code'], r['correct_value']) for r in sage_upd]}")

    # ---- stock
    avail = {c: max(0, stock[c] - alloc[c]) for c in sage}
    avail["NHG-1030"] = min(avail[c] for c in ("NHG-1001", "NHG-1011", "NHG-1020", "NHG-1021", "NHG-1022"))
    for c in sage:
        if int(master[c]["available"]) != avail[c]:
            bad(f"{c} available {master[c]['available']} expected {avail[c]}")
        if c != "NHG-1030" and int(master[c]["qty_in_stock"]) != stock[c]:
            bad(f"{c} qty_in_stock {master[c]['qty_in_stock']} expected {stock[c]}")

    # ---- prices
    vat = {"T0": 0, "T1": 20, "T5": 5}
    gross, shop_p, mapp = {}, {}, {}
    for c, r in sage.items():
        net_th = pence(r["Sales Price"])                       # thousandths
        g_th = net_th * (100 + vat[r["Tax Code"]])             # hundred-thousandths
        g = (g_th + 500) // 1000                               # pence, half up
        gross[c] = g
        m = maps.get(r["Supplier Part Ref"].strip())
        mapp[c] = m
        p = charm_p(g)
        if m is not None:
            p = max(p, up99(m * 10))
        shop_p[c] = p
        mr = master[c]
        if pence(mr["gross_price"]) // 10 != g:
            bad(f"{c} gross {mr['gross_price']} expected {to_str(g)}")
        if pence(mr["shopify_price"]) // 10 != p:
            bad(f"{c} shopify_price {mr['shopify_price']} expected {to_str(p)}")
        if (mr["map"] and pence(mr["map"]) // 10) != (m if m is not None else ""):
            if not (m is None and mr["map"] == ""):
                bad(f"{c} map {mr['map']} expected {m}")

    # ---- shopify targets
    inactive = {c for c, r in sage.items() if r["Inactive"].strip() == "Yes"}
    for r in shop:
        c = r["stock_code"]
        if r["role"] == "duplicate":
            exp = ("", 0, "archived")
            got = (r["new_sku"], int(r["new_inventory"]), r["new_status"])
            if got != exp:
                bad(f"duplicate {r['variant_id']} {got} expected {exp}")
            continue
        st = "archived" if c in discontinued else ("draft" if c in inactive else "active")
        inv = 0 if (c in discontinued or c in inactive) else avail[c]
        exp = (c, to_str(shop_p[c]), master[c]["correct_barcode"], inv, st)
        got = (r["new_sku"], r["new_price"], r["new_barcode"], int(r["new_inventory"]), r["new_status"])
        if got != exp:
            bad(f"shopify {r['variant_id']} {got} expected {exp}")

    # ---- amazon feed
    if [r["sku"] for r in feed] != [l["seller-sku"] for l in listings]:
        bad("feed order / SKUs differ from All Listings report")
    xw = {r["channel_key"]: r for r in cross if r["channel"] == "amazon"}
    for l, f in zip(listings, feed):
        sku = l["seller-sku"]
        c = xw[sku]["stock_code"]
        if not c:
            exp = (l["price"], l["minimum-seller-allowed-price"], l["maximum-seller-allowed-price"], "0", "2", "DEFAULT")
        elif l["fulfillment-channel"] == "AMAZON_EU":
            w = pence(sage[c]["Weight"])
            fee = next(fee for mx, fee in tiers if mx >= w)
            price = up99((shop_p[c] + fee) * 10)
            exp = (to_str(price), to_str(mapp[c]), to_str((price * 15 + 5) // 10), "", "", "AMAZON_EU")
        else:
            n = 1
            if "-X" in sku:
                n = int(sku.rsplit("-X", 1)[1])
            if n > 1:
                disc = (n * gross[c] * 90 + 50) // 100              # pence, half up
                price = max(charm_p(disc), up99(n * mapp[c] * 10))
            else:
                price = shop_p[c]
            mn = n * mapp[c] if mapp[c] is not None else price
            q = 0 if (c in inactive or c in discontinued) else max(0, avail[c] - 1) // n
            exp = (to_str(price), to_str(mn), to_str((price * 15 + 5) // 10), str(q), "2", "DEFAULT")
        got = tuple(f[k] for k in ("price", "minimum-seller-allowed-price", "maximum-seller-allowed-price",
                                   "quantity", "handling-time", "fulfillment-channel"))
        if got != exp:
            bad(f"feed {sku} {got} expected {exp}")
    # FBA figures in master
    for c, r in master.items():
        exp = ";".join(fba_rep[s]["afn-fulfillable-quantity"] for s in r["amazon_skus"].split(";") if s in fba_rep)
        if r["fba_fulfillable"] != exp:
            bad(f"{c} fba_fulfillable {r['fba_fulfillable']} expected {exp}")

    # ---- live
    if a.live:
        def get(url, hdr):
            for _ in range(20):
                try:
                    resp = urllib.request.urlopen(urllib.request.Request(url, headers=hdr))
                    return json.loads(resp.read()), dict(resp.headers)
                except urllib.error.HTTPError as e:
                    if e.code == 429:
                        time.sleep(float(e.headers.get("Retry-After", 1)))
                        continue
                    raise
        H = {"X-Shopify-Access-Token": "shpat_mock_northfield_9f2c"}
        base = "http://127.0.0.1:8765/admin/api/2024-07/"
        url, prods = base + "products.json?limit=3", []
        while url:
            body, hd = get(url, H)
            prods += body["products"]
            link = hd.get("Link", "")
            url = None
            for part in link.split(","):
                if 'rel="next"' in part:
                    url = part.split("<")[1].split(">")[0]
        lv = {}
        items = [v["inventory_item_id"] for p in prods for v in p["variants"]]
        body, _ = get(base + "inventory_levels.json?inventory_item_ids=" + ",".join(map(str, items)), H)
        for x in body["inventory_levels"]:
            lv[x["inventory_item_id"]] = x["available"]
        tgt = {int(r["variant_id"]): r for r in shop}
        nv = 0
        for p in prods:
            for v in p["variants"]:
                nv += 1
                r = tgt.get(v["id"])
                if r is None:
                    bad(f"live variant {v['id']} not in shopify_updates")
                    continue
                got = (v["sku"], v["price"], v["barcode"] or "", lv[v["inventory_item_id"]], p["status"])
                exp = (r["new_sku"], r["new_price"], r["new_barcode"], int(r["new_inventory"]), r["new_status"])
                if got != exp:
                    bad(f"live shopify {v['id']} {got} expected {exp}")
        print(f"  live shopify: {len(prods)} products, {nv} variants compared")
        HA = {"x-amz-access-token": "Atza|mock-northfield-7d41"}
        for f in feed:
            body, _ = get("http://127.0.0.1:8765/sp/listings/" + urllib.parse.quote(f["sku"], safe=""), HA)
            got = (body["price"], body["minimumSellerAllowedPrice"], body["maximumSellerAllowedPrice"],
                   "" if body["quantity"] is None else str(body["quantity"]),
                   "" if body["handlingTime"] is None else str(body["handlingTime"]), body["fulfillmentChannel"])
            exp = tuple(f[k] for k in ("price", "minimum-seller-allowed-price", "maximum-seller-allowed-price",
                                       "quantity", "handling-time", "fulfillment-channel"))
            if got != exp:
                bad(f"live amazon {f['sku']} {got} expected {exp}")
        print(f"  live amazon: {len(feed)} listings compared")

    print(f"RESULT: {len(problems)} mismatches")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
