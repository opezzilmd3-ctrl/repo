"""Build the reconciled dataset and channel files from the sources.

python3 sync/build.py --out output/phase1 [--shopify-snapshot file.json]
        [--stocktake file.csv] [--fba-report file.txt] [--supplier-map file.csv]
        [--discontinued NHG-1234,...]

Without --shopify-snapshot the current Shopify state is pulled live from the API
(all pages) and saved as <out>/shopify_snapshot.json.
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rules as R  # noqa: E402
from shopify import ShopifyClient  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def p(*parts):
    return os.path.join(ROOT, *parts)


# ---------------------------------------------------------------- loaders
def load_sage(path):
    with open(path, encoding="cp1252", newline="") as f:
        rows = list(csv.DictReader(f))
    items, problems = [], []
    for i, r in enumerate(rows, start=2):
        if not any((v or "").strip() for v in r.values()):
            problems.append(f"line {i}: blank row (Excel trailing row) ignored")
            continue
        raw_code = r["Stock Code"]
        code = raw_code.strip()
        item = {
            "line": i,
            "raw_code": raw_code,
            "stock_code": code,
            "description": r["Description"],
            "supplier": r["Supplier A/C"].strip(),
            "part_ref": r["Supplier Part Ref"].strip(),
            "vat_code": r["Tax Code"].strip(),
            "net_price": R.money(r["Sales Price"]),
            "qty_in_stock": int(r["Qty In Stock"]),
            "qty_allocated": int(r["Qty Allocated"]),
            "raw_barcode": r["Barcode"].strip(),
            "weight_kg": R.D(r["Weight"].strip()),
            "inactive": r["Inactive"].strip().lower() == "yes",
        }
        items.append(item)
    return items, problems


def load_tsv(path):
    with open(path, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f, delimiter="\t"))


def load_supplier_map(path):
    with open(path, newline="") as f:
        return {r["part_ref"]: R.D(r["map"]) for r in csv.DictReader(f)}


def load_stocktake(path):
    """Stocktake overrides: stock_code -> {column: value}."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def fetch_shopify_snapshot():
    c = ShopifyClient()
    products = c.all_products(limit=10)
    items = [v["inventory_item_id"] for pr in products for v in pr["variants"]]
    return {"products": products, "inventory_levels": c.inventory_levels(items),
            "locations": c.locations()}


# ---------------------------------------------------------------- build
def build(args):
    out = args.out
    os.makedirs(out, exist_ok=True)
    sage, sage_problems = load_sage(args.sage)
    by_code = {s["stock_code"]: s for s in sage}

    # stocktake / client overrides (Part 4)
    overrides = []
    if args.stocktake:
        for r in load_stocktake(args.stocktake):
            code = r["stock_code"].strip()
            s = by_code[code]
            # a stocktake count is the new quantity in stock; allocations unchanged
            if "counted_qty" in r and "qty_in_stock" not in r:
                r["qty_in_stock"] = r["counted_qty"]
            for col in ("qty_in_stock", "qty_allocated"):
                if (r.get(col) or "").strip() != "":
                    old, new = s[col], int(r[col])
                    overrides.append((code, col, old, new, "stocktake"))
                    s.setdefault("stocktake", []).append(f"stocktake: {col} {old} -> {new}")
                    s[col] = new
    discontinued = set(x.strip() for x in (args.discontinued or "").split(",") if x.strip())

    listings = load_tsv(args.listings)
    fba_rows = load_tsv(args.fba_report)
    fba_by_sku = {r["sku"]: r for r in fba_rows}
    maps = load_supplier_map(args.supplier_map)
    tiers = R.load_fee_tiers(args.fee_tiers)

    if args.shopify_snapshot:
        snap = json.load(open(args.shopify_snapshot))
    else:
        snap = fetch_shopify_snapshot()
    json.dump(snap, open(os.path.join(out, "shopify_snapshot.json"), "w"), indent=1)
    levels = {l["inventory_item_id"]: l["available"] for l in snap["inventory_levels"]}
    location_id = snap["locations"][0]["id"]
    # Matching and the crosswalk use the source snapshot. "Current" values for
    # shopify_updates (what still has to change) come from the live state.
    if args.current_snapshot:
        live = json.load(open(args.current_snapshot))
    elif args.live_current:
        live = fetch_shopify_snapshot()
        json.dump(live, open(os.path.join(out, "shopify_before_final_push.json"), "w"), indent=1)
    else:
        live = snap
    live_levels = {l["inventory_item_id"]: l["available"] for l in live["inventory_levels"]}
    live_v = {v["id"]: (v, pr) for pr in live["products"] for v in pr["variants"]}

    variants = []
    for prod in snap["products"]:
        for v in prod["variants"]:
            variants.append({**v, "product": prod, "available": levels.get(v["inventory_item_id"])})

    codes = set(by_code)

    # --- Shopify matching step 1/2: sku, normalised sku
    for v in variants:
        v["match"], v["method"] = None, None
        if v["sku"] in codes:
            v["match"], v["method"] = v["sku"], "sku"
        elif R.normalise_sku(v["sku"]) in codes:
            v["match"], v["method"] = R.normalise_sku(v["sku"]), "normalised sku"

    # --- Amazon matching step 1/2
    for l in listings:
        base, kind, n = R.split_amazon_sku(l["seller-sku"])
        l["kind"], l["pack_n"], l["match"], l["method"] = kind, n, None, None
        if l["fulfillment-channel"] == "AMAZON_EU":
            l["kind"] = "FBA"
        if base in codes:
            l["match"], l["method"] = base, "sku"
        elif R.normalise_sku(base) in codes:
            l["match"], l["method"] = R.normalise_sku(base), "normalised sku"

    # --- correct barcodes
    def shop_barcodes(code):
        return [v["barcode"] for v in variants if v["match"] == code]

    def amz_barcodes(code):
        return [l["product-id"] for l in listings if l["match"] == code and l["kind"] != "PACK"]

    sage_repaired = {}
    for s in sage:
        sage_repaired[s["stock_code"]] = R.repair_excel_barcode(s["raw_barcode"])
    shared = {}
    for code, (val, _) in sage_repaired.items():
        if val:
            shared.setdefault(val, []).append(code)
    shared = {k: v for k, v in shared.items() if len(v) > 1}

    sage_updates = []
    for s in sage:
        code = s["stock_code"]
        val, damage = sage_repaired[code]
        s["barcode_damage"] = damage
        notes = []
        sage_ok = val is not None and R.is_valid_ean13(val)
        sage_reason = None
        if val is None and damage == "missing":
            sage_reason = "missing in Sage"
        elif val is None:
            notes.append(f"Sage barcode '{s['raw_barcode']}' unreadable (Excel scientific notation)")
        elif not sage_ok:
            sage_reason = f"invalid check digit (expected {R.ean13_check_digit(val[:12]) if len(val) == 13 and val.isdigit() else 'n/a'})"
        if sage_ok and val in shared:
            owners = [c for c in shared[val] if val in shop_barcodes(c) or val in amz_barcodes(c)]
            if code not in owners:
                sage_ok = False
                sage_reason = f"belongs to {', '.join(owners)} (shared barcode)"
        chosen, source = None, None
        if sage_ok:
            chosen, source = val, "sage"
            if damage == "leading-zero-restored":
                notes.append(f"Sage export barcode '{s['raw_barcode']}' lost its leading zero in Excel; restored")
        else:
            for src, cands in (("shopify", shop_barcodes(code)), ("amazon", amz_barcodes(code))):
                good = [b for b in cands if R.is_valid_ean13(b)]
                if good:
                    chosen, source = good[0], src
                    break
        s["correct_barcode"], s["barcode_source"] = chosen, source
        if damage == "scientific-notation" and chosen:
            # Excel damage only: consistent if the visible leading digits agree
            mant = s["raw_barcode"].upper().split("E")[0].replace(".", "")
            if not chosen.startswith(mant):
                sage_reason = f"Sage value '{s['raw_barcode']}' inconsistent with {chosen}"
        if sage_reason:
            sage_updates.append({"stock_code": code, "field": "barcode",
                                 "sage_value": s["raw_barcode"], "correct_value": chosen or "",
                                 "reason": sage_reason})
            notes.append(f"Sage barcode wrong in Sage: {sage_reason}")
        s["notes"] = notes

    correct_to_code = {s["correct_barcode"]: s["stock_code"] for s in sage if s["correct_barcode"]}

    # --- Shopify matching step 3: barcode
    for v in variants:
        if v["match"] is None and v["barcode"] in correct_to_code:
            v["match"], v["method"] = correct_to_code[v["barcode"]], "barcode"
    # --- Amazon matching step 4: product-id
    for l in listings:
        if l["match"] is None and l["product-id"] in correct_to_code:
            l["match"], l["method"] = correct_to_code[l["product-id"]], "product-id"

    # --- duplicates
    by_match = {}
    for v in variants:
        if v["match"]:
            by_match.setdefault(v["match"], []).append(v)
    for code, vs in by_match.items():
        prods = sorted({v["product"]["id"]: v["product"] for v in vs}.values(), key=lambda x: x["created_at"])
        for v in vs:
            v["duplicate"] = v["product"]["id"] != prods[0]["id"]
    for v in variants:
        v.setdefault("duplicate", False)

    # --- stock
    for s in sage:
        s["available"] = R.available(s["qty_in_stock"], s["qty_allocated"])
        s["discontinued"] = s["stock_code"] in discontinued
    avail = {s["stock_code"]: s["available"] for s in sage}
    kit = by_code.get(R.KIT_CODE)
    if kit:
        kit["available"] = R.kit_available(avail)
        avail[R.KIT_CODE] = kit["available"]

    # --- pricing
    for s in sage:
        s["gross"] = R.gross_price(s["net_price"], s["vat_code"])
        s["map"] = maps.get(s["part_ref"]) if s["part_ref"] else None
        if s["part_ref"] and s["map"] is None:
            raise SystemExit(f"No MAP for {s['stock_code']} part {s['part_ref']}")
        s["shopify_price"] = R.shopify_price(s["gross"], s["map"])
        s["map_raised"] = s["map"] is not None and s["shopify_price"] > R.charm(s["gross"])
        s["sellable"] = not s["inactive"] and not s["discontinued"]

    # --- notes for stock / status / weights
    for s in sage:
        code = s["stock_code"]
        s["notes"].extend(s.get("stocktake", []))
        if s["raw_code"] != code:
            s["notes"].append(f"Sage stock code has stray whitespace ({s['raw_code']!r})")
        if code == R.KIT_CODE:
            s["notes"].append("kit: available from components; own Sage stock ignored")
        elif s["qty_in_stock"] < 0:
            s["notes"].append(f"negative stock in Sage ({s['qty_in_stock']}); treated as 0")
        elif s["qty_allocated"] > s["qty_in_stock"]:
            s["notes"].append(f"over-allocated ({s['qty_allocated']} allocated vs {s['qty_in_stock']} in stock); available 0")
        if s["inactive"]:
            s["notes"].append("inactive in Sage: Shopify draft, inventory 0, Amazon FBM 0")
        if s["discontinued"]:
            s["notes"].append("discontinued: Shopify archived, inventory 0, Amazon FBM 0")
        if s["map_raised"]:
            s["notes"].append(f"MAP {s['map']} raised price from {R.charm(s['gross'])} to {s['shopify_price']}")
        mv = [v for v in variants if v["match"] == code and not v["duplicate"]]
        s["variant"] = mv[0] if mv else None
        if mv:
            v = mv[0]
            if v["sku"] != code:
                s["notes"].append(f"Shopify SKU {v['sku']!r} corrected to {code}" if v["sku"]
                                  else f"Shopify SKU blank; set to {code} (matched by {v['method']})")
            if (v["barcode"] or "") != (s["correct_barcode"] or ""):
                why = ("blank" if not v["barcode"] else
                       "invalid check digit" if not R.is_valid_ean13(v["barcode"]) else "differs")
                s["notes"].append(f"Shopify barcode {v['barcode']!r} ({why}) set to {s['correct_barcode']}")
            if s["inactive"] and v["product"]["status"] == "active":
                s["notes"].append("inactive item still active on Shopify")
            w =R.D(str(v["weight"])) / (1000 if v["weight_unit"] == "g" else 1)
            if v["weight_unit"] == "lb":
                w = R.D(str(v["weight"])) * R.D("0.45359237")
            elif v["weight_unit"] == "oz":
                w = R.D(str(v["weight"])) * R.D("0.0283495231")
            s["shopify_weight_kg"] = w
            if abs(w - s["weight_kg"]) > R.D("0.01"):
                s["notes"].append(f"weight mismatch: Sage {s['weight_kg']} kg vs Shopify {v['weight']} {v['weight_unit']}")
        else:
            s["notes"].append("no Shopify variant")

    # --- Amazon targets
    feed_rows = []
    for l in listings:
        code = l["match"]
        s = by_code.get(code) if code else None
        if s is None:
            l["orphan"] = True
            row = {"sku": l["seller-sku"], "price": l["price"],
                   "minimum-seller-allowed-price": l["minimum-seller-allowed-price"],
                   "maximum-seller-allowed-price": l["maximum-seller-allowed-price"],
                   "quantity": "0", "handling-time": "2", "fulfillment-channel": "DEFAULT"}
            if l["fulfillment-channel"] == "AMAZON_EU":
                row.update({"quantity": "", "handling-time": "", "fulfillment-channel": "AMAZON_EU"})
            feed_rows.append(row)
            continue
        l["orphan"] = False
        if l["kind"] == "FBA":
            fee = R.fba_fee(s["weight_kg"], tiers)
            price = R.fba_price(s["shopify_price"], fee)
            l["fba_fee"] = fee
            row = {"sku": l["seller-sku"], "price": R.fmt(price),
                   "minimum-seller-allowed-price": R.fmt(R.min_price(price, s["map"])),
                   "maximum-seller-allowed-price": R.fmt(R.max_price(price)),
                   "quantity": "", "handling-time": "", "fulfillment-channel": "AMAZON_EU"}
        else:
            n = l["pack_n"]
            if l["kind"] == "PACK":
                price = R.multipack_price(s["gross"], n, s["map"])
            else:
                price = s["shopify_price"]
            qty = R.fbm_quantity(s["available"], n) if s["sellable"] else 0
            row = {"sku": l["seller-sku"], "price": R.fmt(price),
                   "minimum-seller-allowed-price": R.fmt(R.min_price(price, s["map"], n)),
                   "maximum-seller-allowed-price": R.fmt(R.max_price(price)),
                   "quantity": str(qty), "handling-time": "2", "fulfillment-channel": "DEFAULT"}
        feed_rows.append(row)
    for l, row in zip(listings, feed_rows):
        l["target"] = row

    # ------------------------------------------------------------ write files
    def w_csv(name, fields, rows, delim=","):
        path = os.path.join(out, name)
        with open(path, "w", newline="", encoding="utf-8") as f:
            wr = csv.DictWriter(f, fieldnames=fields, delimiter=delim, lineterminator="\n")
            wr.writeheader()
            wr.writerows(rows)
        return path

    master = []
    for s in sage:
        v = s["variant"]
        amz = [l["seller-sku"] for l in listings if l["match"] == s["stock_code"]]
        fba = [fba_by_sku[k]["afn-fulfillable-quantity"] for k in amz if k in fba_by_sku]
        master.append({
            "stock_code": s["stock_code"],
            "title": v["product"]["title"] if v else "",
            "variant": v["title"] if v else "",
            "vat_code": s["vat_code"],
            "net_price": R.fmt(s["net_price"]),
            "gross_price": R.fmt(s["gross"]),
            "map": R.fmt(s["map"]) if s["map"] is not None else "",
            "shopify_price": R.fmt(s["shopify_price"]),
            "correct_barcode": s["correct_barcode"] or "",
            "barcode_source": s["barcode_source"] or "",
            "qty_in_stock": s["qty_in_stock"],
            "qty_allocated": s["qty_allocated"],
            "available": s["available"],
            "active": "No" if s["inactive"] else ("Discontinued" if s["discontinued"] else "Yes"),
            "weight_kg": f"{s['weight_kg']}",
            "shopify_product_id": v["product"]["id"] if v else "",
            "shopify_variant_id": v["id"] if v else "",
            "shopify_inventory_item_id": v["inventory_item_id"] if v else "",
            "amazon_skus": ";".join(amz),
            "fba_fulfillable": ";".join(fba),
            "notes": "; ".join(s["notes"]),
        })
    w_csv("master_products.csv", list(master[0].keys()), master)

    cross = []
    for v in variants:
        status = "orphan" if not v["match"] else ("duplicate" if v["duplicate"] else "matched")
        cross.append({"channel": "shopify", "channel_key": v["id"],
                      "shopify_product_id": v["product"]["id"], "sku": v["sku"],
                      "title": f"{v['product']['title']} / {v['title']}",
                      "barcode_or_product_id": v["barcode"], "fulfilment": "",
                      "stock_code": v["match"] or "", "match_method": v["method"] or "none",
                      "status": status, "notes": ""})
    for c, v in zip(cross, variants):
        if v["duplicate"]:
            keep = [x for x in by_match[v["match"]] if not x["duplicate"]][0]
            c["notes"] = (f"duplicate product (created {v['product']['created_at']}); earlier product "
                          f"{keep['product']['id']} (created {keep['product']['created_at']}) kept")
        elif not v["sku"]:
            c["notes"] = "blank SKU"
        elif v["method"] == "normalised sku":
            c["notes"] = f"SKU format differs from Sage ({v['sku']!r})"
    for l in listings:
        cross.append({"channel": "amazon", "channel_key": l["seller-sku"], "shopify_product_id": "",
                      "sku": l["seller-sku"], "title": l["item-name"],
                      "barcode_or_product_id": l["product-id"],
                      "fulfilment": ("FBA" if l["kind"] == "FBA" else
                                     (f"FBM multipack x{l['pack_n']}" if l["kind"] == "PACK" else "FBM single")),
                      "stock_code": l["match"] or "", "match_method": l["method"] or "none",
                      "status": "orphan" if l["orphan"] else "matched",
                      "notes": ("no Sage item has this SKU or EAN" if l["orphan"] else
                                ("Amazon auto-generated SKU" if l["method"] == "product-id" else
                                 ("SKU case differs from Sage (Amazon SKU kept)" if l["method"] == "normalised sku" else "")))})
    w_csv("crosswalk.csv", list(cross[0].keys()), cross)

    # Shopify updates
    upd = []
    sku_of = {}
    for v in variants:
        prod = v["product"]
        if v["duplicate"]:
            tgt = {"sku": "", "price": v["price"], "barcode": v["barcode"], "inventory": 0, "status": "archived"}
            role = "duplicate"
        elif v["match"]:
            s = by_code[v["match"]]
            inv = s["available"] if s["sellable"] else 0
            status = "archived" if s["discontinued"] else ("draft" if s["inactive"] else "active")
            tgt = {"sku": s["stock_code"], "price": R.fmt(s["shopify_price"]),
                   "barcode": s["correct_barcode"], "inventory": inv, "status": status}
            role = "master"
        else:
            continue
        lv, lp = live_v[v["id"]]
        prod = lp
        cur = {"sku": lv["sku"], "price": lv["price"], "barcode": lv["barcode"] or "",
               "inventory": live_levels.get(lv["inventory_item_id"]), "status": lp["status"]}
        changes = [k for k in ("sku", "price", "barcode", "inventory", "status")
                   if str(cur[k]) != str(tgt[k])]
        if prod["status"] == "archived" and changes:
            changes = ["BLOCKED-archived:" + ",".join(changes)]
        upd.append({"variant_id": v["id"], "product_id": prod["id"],
                    "inventory_item_id": v["inventory_item_id"], "location_id": location_id,
                    "stock_code": v["match"], "role": role,
                    "current_sku": cur["sku"], "new_sku": tgt["sku"],
                    "current_price": cur["price"], "new_price": tgt["price"],
                    "current_barcode": cur["barcode"], "new_barcode": tgt["barcode"],
                    "current_inventory": cur["inventory"], "new_inventory": tgt["inventory"],
                    "current_status": cur["status"], "new_status": tgt["status"],
                    "changes": ";".join(changes)})
    w_csv("shopify_updates.csv", list(upd[0].keys()), upd)

    feed_fields = ["sku", "price", "minimum-seller-allowed-price", "maximum-seller-allowed-price",
                   "quantity", "handling-time", "fulfillment-channel"]
    w_csv("amazon_price_quantity.txt", feed_fields, feed_rows, delim="\t")
    if args.previous_feed:
        prev = {r["sku"]: r for r in load_tsv(args.previous_feed)}
        delta = [r for r in feed_rows if prev.get(r["sku"]) != r]
        w_csv("amazon_price_quantity_delta.txt", feed_fields, delta, delim="\t")
        print(f"delta feed: {len(delta)} changed rows vs {args.previous_feed}")
    w_csv("sage_updates.csv", ["stock_code", "field", "sage_value", "correct_value", "reason"], sage_updates)

    json.dump({"sage_problems": sage_problems, "overrides": overrides,
               "shared_barcodes": shared}, open(os.path.join(out, "build_info.json"), "w"), indent=1)
    print(f"master {len(master)} rows, crosswalk {len(cross)}, shopify updates "
          f"{sum(1 for u in upd if u['changes'])}/{len(upd)} with changes, feed {len(feed_rows)}, "
          f"sage updates {len(sage_updates)}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--sage", default=p("sage_stock_export.csv"))
    ap.add_argument("--listings", default=p("amazon_all_listings_report.txt"))
    ap.add_argument("--fba-report", default=p("amazon_fba_inventory_report.txt"))
    ap.add_argument("--supplier-map", default=p("output", "phase1", "supplier_map.csv"))
    ap.add_argument("--fee-tiers", default=p("fba_fee_tiers.csv"))
    ap.add_argument("--shopify-snapshot")
    ap.add_argument("--stocktake")
    ap.add_argument("--discontinued")
    ap.add_argument("--live-current", action="store_true",
                    help="match on --shopify-snapshot but diff against the live Shopify state")
    ap.add_argument("--current-snapshot",
                    help="match on --shopify-snapshot but diff against this saved Shopify state")
    ap.add_argument("--previous-feed", help="last pushed feed; writes amazon_price_quantity_delta.txt")
    build(ap.parse_args())


if __name__ == "__main__":
    main()
