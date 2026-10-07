"""Apply shopify_updates.csv and submit amazon_price_quantity.txt, logging every call.

python3 sync/push.py --dir output/phase1 [--only shopify|amazon] [--log push_log.csv]

The log is appended to <dir>/push_log.csv (one line per API call and per feed row error).
Exit status is non-zero when any Shopify call failed or the feed reported row errors.
"""
import argparse
import csv
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from shopify import ShopifyClient, ShopifyError  # noqa: E402
from amazon import AmazonClient, AmazonError, read_feed_file  # noqa: E402

LOG_FIELDS = ["timestamp", "run", "channel", "action", "target", "method", "url",
              "http_status", "request", "result"]


class PushLog:
    def __init__(self, path, run):
        self.path, self.run = path, run
        new = not os.path.exists(path)
        self.f = open(path, "a", newline="", encoding="utf-8")
        self.w = csv.DictWriter(self.f, fieldnames=LOG_FIELDS, lineterminator="\n")
        if new:
            self.w.writeheader()
        self.ctx = {}

    def http(self, entry):
        self.write(method=entry.get("method"), url=entry.get("url"),
                   http_status=entry.get("status"),
                   request=json.dumps(entry["request"]) if entry.get("request") is not None else "",
                   result=entry.get("result") or _short(entry.get("response")))

    def write(self, **kw):
        row = {"timestamp": dt.datetime.now().isoformat(timespec="seconds"), "run": self.run, **self.ctx, **kw}
        self.w.writerow({k: row.get(k, "") for k in LOG_FIELDS})
        self.f.flush()


def _short(x):
    s = x if isinstance(x, str) else json.dumps(x)
    return (s or "")[:300]


def push_shopify(path, log):
    rows = [r for r in csv.DictReader(open(path, newline="", encoding="utf-8")) if r["changes"]]
    # duplicates first so their SKU is released before the kept variant takes it
    rows.sort(key=lambda r: 0 if r["role"] == "duplicate" else 1)
    client = ShopifyClient(log=log.http)
    failures = []
    for r in rows:
        changes = r["changes"].split(";")
        if any(c.startswith("BLOCKED") for c in changes):
            log.ctx = {"channel": "shopify", "action": "skip", "target": r["variant_id"]}
            log.write(result=f"product archived; cannot edit ({r['changes']})")
            failures.append((r["variant_id"], "archived product cannot be edited"))
            continue
        steps = []
        if "inventory" in changes:
            steps.append(("inventory", lambda r=r: client.set_inventory(
                int(r["location_id"]), int(r["inventory_item_id"]), int(r["new_inventory"]))))
        fields = {}
        for f in ("sku", "price", "barcode"):
            if f in changes:
                fields[f] = r[f"new_{f}"]
        if fields:
            steps.append(("variant", lambda r=r, fields=fields: client.update_variant(int(r["variant_id"]), fields)))
        if "status" in changes:
            steps.append(("status", lambda r=r: client.set_status(int(r["product_id"]), r["new_status"])))
        for action, fn in steps:
            log.ctx = {"channel": "shopify", "action": action, "target": f"{r['stock_code']} v{r['variant_id']}"}
            try:
                fn()
            except ShopifyError as e:
                log.write(result=f"ERROR {e.status}: {e.describe()}")
                failures.append((r["variant_id"], action, e.status, e.describe()))
                print(f"  shopify {action} {r['stock_code']} v{r['variant_id']}: HTTP {e.status} {e.describe()}")
    log.ctx = {}
    return failures


def push_amazon(path, log):
    content = read_feed_file(path)
    log.ctx = {"channel": "amazon", "action": "feed", "target": os.path.basename(path)}
    client = AmazonClient(log=log.http)
    feed_id, feed, report, parsed = client.submit_feed(content)
    log.write(result=f"feed {feed_id} {feed.get('processingStatus')}; summary {json.dumps(parsed['summary'])}")
    report_path = os.path.join(os.path.dirname(path), f"feed_report_{feed_id}.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    for e in parsed["errors"]:
        log.ctx = {"channel": "amazon", "action": "feed-row-error", "target": e.get("sku", "")}
        log.write(result=json.dumps(e))
        print(f"  amazon row {e.get('original-record-number')} {e.get('sku')}: "
              f"{e.get('error-code')} {e.get('error-type')} {e.get('error-message')}")
    log.ctx = {}
    return feed_id, parsed


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dir", required=True)
    ap.add_argument("--only", choices=["shopify", "amazon"])
    ap.add_argument("--log", default="push_log.csv")
    ap.add_argument("--shopify-file", default="shopify_updates.csv")
    ap.add_argument("--feed-file", default="amazon_price_quantity.txt")
    a = ap.parse_args()
    run = dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    log = PushLog(os.path.join(a.dir, a.log), run)
    ok = True
    if a.only in (None, "shopify"):
        fails = push_shopify(os.path.join(a.dir, a.shopify_file), log)
        print(f"shopify: {len(fails)} failures")
        ok &= not fails
    if a.only in (None, "amazon"):
        try:
            feed_id, parsed = push_amazon(os.path.join(a.dir, a.feed_file), log)
            print(f"amazon feed {feed_id}: {json.dumps(parsed['summary'])}; {len(parsed['errors'])} row errors")
            ok &= not parsed["errors"]
        except AmazonError as e:
            log.write(channel="amazon", action="feed", result=f"ERROR {e}")
            print(f"amazon: {e}")
            ok = False
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
