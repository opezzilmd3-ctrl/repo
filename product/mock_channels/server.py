#!/usr/bin/env python3
"""Mock Shopify Admin API and Amazon SP-API (Feeds + Listings) for Northfield Home & Garden.

Run:  python3 mock_channels/server.py            (serves on http://127.0.0.1:8765)
      python3 mock_channels/server.py --reset    (restore the client's original data, then serve)
State is kept in mock_channels/data/state.json and survives restarts.
"""
import base64, json, math, os, re, shutil, sys, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

HERE = os.path.dirname(os.path.abspath(__file__))
SEED = os.path.join(HERE, "data", "seed.json")
STATE = os.path.join(HERE, "data", "state.json")
PORT = int(os.environ.get("MOCK_PORT", "8765"))
SHOP_TOKEN = "shpat_mock_northfield_9f2c"
AMZ_TOKEN = "Atza|mock-northfield-7d41"
API = "/admin/api/2024-07"
FEED_TYPE = "POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA"
FEED_HEADER = ["sku", "price", "minimum-seller-allowed-price", "maximum-seller-allowed-price", "quantity",
               "handling-time", "fulfillment-channel"]
LOCK = threading.RLock()


def load_state(reset=False):
    if reset or not os.path.exists(STATE):
        shutil.copyfile(SEED, STATE)
    with open(STATE) as fh:
        st = json.load(fh)
    st.setdefault("feeds", {}); st.setdefault("documents", {}); st.setdefault("counters", {"doc": 0, "feed": 50000})
    return st


def save():
    tmp = STATE + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(S, fh, indent=1)
    os.replace(tmp, STATE)


class Bucket:
    def __init__(self, cap, rate):
        self.cap, self.rate, self.tokens, self.t = cap, rate, cap, time.monotonic()

    def take(self):
        with LOCK:
            now = time.monotonic()
            self.tokens = min(self.cap, self.tokens + (now - self.t) * self.rate)
            self.t = now
            if self.tokens >= 1:
                self.tokens -= 1
                return 0
            return max(1, math.ceil((1 - self.tokens) / self.rate))


BUCKETS = {"shopify": Bucket(8, 2.0), "listings": Bucket(5, 2.0), "feeds_create": Bucket(2, 0.2), "feeds": Bucket(10, 2.0)}


def gtin_ok(code):
    if not re.fullmatch(r"\d{8}|\d{12}|\d{13}|\d{14}", code or ""):
        return False
    digits = [int(c) for c in code]
    body, check = digits[:-1], digits[-1]
    s = sum(d * (3 if i % 2 == 0 else 1) for i, d in enumerate(reversed(body)))
    return (10 - s % 10) % 10 == check


PRICE_RE = re.compile(r"^\d+(\.\d{1,2})?$")
FEED_PRICE_RE = re.compile(r"^\d+\.\d{2}$")


def variant_index():
    out = {}
    for p in S["shopify"]["products"]:
        for v in p["variants"]:
            out[v["id"]] = (p, v)
    return out


def product_json(p):
    inv = S["shopify"]["inventory"]
    q = dict(p)
    q["variants"] = [dict(v, inventory_quantity=inv.get(str(v["inventory_item_id"]), 0),
                          price=f'{float(v["price"]):.2f}') for v in p["variants"]]
    return q


class H(BaseHTTPRequestHandler):
    server_version = "MockChannels/1.0"

    def log_message(self, fmt, *args):
        sys.stdout.write("%s %s\n" % (time.strftime("%H:%M:%S"), fmt % args)); sys.stdout.flush()

    # ---------- helpers ----------
    def send(self, code, body=None, headers=None, raw=None, ctype="application/json"):
        data = raw if raw is not None else (json.dumps(body).encode() if body is not None else b"")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        for k, v in (headers or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(data)

    def body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return self.rfile.read(n) if n else b""

    def json_body(self):
        try:
            return json.loads(self.body() or b"{}")
        except json.JSONDecodeError:
            return None

    def limited(self, name):
        wait = BUCKETS[name].take()
        if wait:
            msg = {"errors": "Exceeded 2 calls per second for api client. Reduce request rates to resume uninterrupted service."} \
                if name == "shopify" else {"errors": [{"code": "QuotaExceeded", "message": "You exceeded your quota for the requested resource."}]}
            self.send(429, msg, {"Retry-After": str(wait)})
            return True
        return False

    def route(self, method):
        u = urlparse(self.path)
        path, qs = u.path, parse_qs(u.query)
        try:
            if path.startswith("/admin/api/"):
                if not path.startswith(API + "/"):
                    return self.send(404, {"errors": "Not Found: this store only serves API version 2024-07"})
                if self.headers.get("X-Shopify-Access-Token") != SHOP_TOKEN:
                    return self.send(401, {"errors": "[API] Invalid API key or access token (unrecognized login or wrong password)"})
                if self.limited("shopify"):
                    return
                with LOCK:
                    return self.shopify(method, path[len(API):], qs)
            if path.startswith("/uploads/") or path.startswith("/downloads/"):
                with LOCK:
                    return self.documents(method, path)
            if path.startswith("/feeds/") or path.startswith("/sp/"):
                if self.headers.get("x-amz-access-token") != AMZ_TOKEN:
                    return self.send(403, {"errors": [{"code": "Unauthorized", "message": "Access to requested resource is denied."}]})
                with LOCK:
                    return self.amazon(method, path, qs)
            return self.send(404, {"errors": "Not Found"})
        except Exception as e:  # keep the mock alive
            return self.send(500, {"errors": f"internal error: {e.__class__.__name__}"})

    def do_GET(self): self.route("GET")
    def do_POST(self): self.route("POST")
    def do_PUT(self): self.route("PUT")
    def do_DELETE(self): self.route("DELETE")

    # ---------- Shopify ----------
    def shopify(self, m, p, qs):
        shop = S["shopify"]
        if m == "GET" and p == "/locations.json":
            return self.send(200, {"locations": [shop["location"]]})
        if m == "GET" and p == "/products/count.json":
            return self.send(200, {"count": len(shop["products"])})
        if m == "GET" and p == "/products.json":
            extra = set(qs) - {"limit", "page_info"}
            if "page_info" in qs and extra:
                return self.send(400, {"errors": "page_info cannot be combined with other parameters except limit"})
            try:
                limit = int(qs.get("limit", ["5"])[0])
            except ValueError:
                limit = -1
            if not 1 <= limit <= 10:
                return self.send(400, {"errors": "limit must be between 1 and 10"})
            offset = 0
            if "page_info" in qs:
                try:
                    tok = base64.urlsafe_b64decode(qs["page_info"][0] + "==").decode()
                    offset = int(tok.split(":")[1])
                except Exception:
                    return self.send(400, {"errors": "Invalid page_info"})
            prods = sorted(shop["products"], key=lambda x: x["id"])
            page = prods[offset:offset + limit]
            host = self.headers.get("Host", f"127.0.0.1:{PORT}")
            links = []

            def mk(off):
                tok = base64.urlsafe_b64encode(f"o:{off}:{int(time.time())}".encode()).decode().rstrip("=")
                return f"<http://{host}{API}/products.json?limit={limit}&page_info={tok}>"
            if offset > 0:
                links.append(mk(max(0, offset - limit)) + '; rel="previous"')
            if offset + limit < len(prods):
                links.append(mk(offset + limit) + '; rel="next"')
            hdr = {"Link": ", ".join(links)} if links else {}
            return self.send(200, {"products": [product_json(x) for x in page]}, hdr)
        mm = re.fullmatch(r"/products/(\d+)\.json", p)
        if mm:
            prod = next((x for x in shop["products"] if x["id"] == int(mm.group(1))), None)
            if not prod:
                return self.send(404, {"errors": "Not Found"})
            if m == "GET":
                return self.send(200, {"product": product_json(prod)})
            if m == "PUT":
                b = self.json_body()
                if not isinstance(b, dict) or not isinstance(b.get("product"), dict):
                    return self.send(400, {"errors": {"product": "Required parameter missing or invalid"}})
                upd = b["product"]
                bad = [k for k in upd if k not in ("id", "status")]
                if bad:
                    return self.send(422, {"errors": {k: ["is not supported by this store's API scope"] for k in bad}})
                if "status" in upd:
                    if upd["status"] not in ("active", "draft", "archived"):
                        return self.send(422, {"errors": {"status": ["is not included in the list"]}})
                    prod["status"] = upd["status"]
                save()
                return self.send(200, {"product": product_json(prod)})
        mm = re.fullmatch(r"/variants/(\d+)\.json", p)
        if mm:
            idx = variant_index()
            vid = int(mm.group(1))
            if vid not in idx:
                return self.send(404, {"errors": "Not Found"})
            prod, var = idx[vid]
            if m == "GET":
                return self.send(200, {"variant": product_json(prod)["variants"][prod["variants"].index(var)]})
            if m == "PUT":
                b = self.json_body()
                if not isinstance(b, dict) or not isinstance(b.get("variant"), dict):
                    return self.send(400, {"errors": {"variant": "Required parameter missing or invalid"}})
                upd = b["variant"]
                errs = {}
                for k in upd:
                    if k == "inventory_quantity":
                        errs[k] = ["is read-only; set stock with POST inventory_levels/set.json"]
                    elif k not in ("id", "sku", "price", "barcode"):
                        errs[k] = ["cannot be updated through this endpoint"]
                if prod["status"] == "archived":
                    errs.setdefault("base", []).append("Archived products cannot be edited. Unarchive the product first.")
                if "price" in upd:
                    pr = str(upd["price"])
                    if not PRICE_RE.match(pr) or float(pr) <= 0:
                        errs["price"] = ["must be a positive amount with at most 2 decimal places"]
                if "barcode" in upd:
                    bc = upd["barcode"]
                    if bc is None:
                        bc = ""
                    if not isinstance(bc, str) or (bc and not gtin_ok(bc)):
                        errs["barcode"] = ["is not a valid GTIN (check digit or length)"]
                if "sku" in upd:
                    sku = upd["sku"]
                    if sku is None:
                        sku = ""
                    if not isinstance(sku, str) or sku != sku.strip():
                        errs["sku"] = ["cannot have leading or trailing whitespace"]
                    elif sku:
                        for op, ov in idx.values():
                            if ov["id"] != vid and ov["sku"] == sku:
                                errs["sku"] = [f"has already been taken (variant {ov['id']})"]
                if errs:
                    return self.send(422, {"errors": errs})
                if "price" in upd:
                    var["price"] = f'{float(upd["price"]):.2f}'
                if "barcode" in upd:
                    var["barcode"] = upd["barcode"] or ""
                if "sku" in upd:
                    var["sku"] = upd["sku"] or ""
                save()
                return self.send(200, {"variant": product_json(prod)["variants"][prod["variants"].index(var)]})
        if m == "GET" and p == "/inventory_levels.json":
            ids = qs.get("inventory_item_ids", [""])[0].split(",")
            levels = [{"inventory_item_id": int(i), "location_id": shop["location"]["id"],
                       "available": shop["inventory"].get(i, 0)} for i in ids if i in shop["inventory"]]
            return self.send(200, {"inventory_levels": levels})
        if m == "POST" and p == "/inventory_levels/set.json":
            b = self.json_body()
            if not isinstance(b, dict):
                return self.send(400, {"errors": "Invalid JSON"})
            errs = {}
            if b.get("location_id") != shop["location"]["id"]:
                errs["location_id"] = ["location not found"]
            iid = str(b.get("inventory_item_id"))
            if iid not in shop["inventory"]:
                return self.send(404, {"errors": "Inventory item not found"})
            av = b.get("available")
            if not isinstance(av, int) or isinstance(av, bool) or av < 0:
                errs["available"] = ["must be an integer greater than or equal to 0"]
            owner = next(pp for pp in shop["products"] for v in pp["variants"] if str(v["inventory_item_id"]) == iid)
            if owner["status"] == "archived":
                errs.setdefault("base", []).append("Inventory of archived products cannot be changed.")
            if errs:
                return self.send(422, {"errors": errs})
            shop["inventory"][iid] = av
            save()
            return self.send(200, {"inventory_level": {"inventory_item_id": int(iid), "location_id": shop["location"]["id"], "available": av}})
        return self.send(404, {"errors": "Not Found"})

    # ---------- Amazon ----------
    def listing(self, sku):
        return next((l for l in S["amazon"]["listings"] if l["sku"] == sku), None)

    def amazon(self, m, p, qs):
        amz = S["amazon"]
        mm = re.fullmatch(r"/sp/listings/(.+)", p)
        if m == "GET" and mm:
            if self.limited("listings"):
                return
            l = self.listing(unquote(mm.group(1)))
            if not l:
                return self.send(404, {"errors": [{"code": "NOT_FOUND", "message": "SKU not found for this seller"}]})
            fba = l["fulfillment_channel"] == "AMAZON_EU"
            status = "Active" if fba or (l["quantity"] or 0) > 0 else "Inactive"
            return self.send(200, {"sku": l["sku"], "asin": l["asin"], "productId": l["product_id"], "itemName": l["item_name"],
                                   "fulfillmentChannel": l["fulfillment_channel"], "status": status, "price": l["price"],
                                   "minimumSellerAllowedPrice": l["min"], "maximumSellerAllowedPrice": l["max"],
                                   "quantity": None if fba else l["quantity"], "handlingTime": None if fba else l["handling_time"],
                                   "note": "Quantity of Amazon-fulfilled listings is managed by Amazon" if fba else None})
        if m == "POST" and p == "/feeds/2021-06-30/documents":
            if self.limited("feeds"):
                return
            b = self.json_body()
            if not isinstance(b, dict) or "contentType" not in b:
                return self.send(400, {"errors": [{"code": "InvalidInput", "message": "contentType is required"}]})
            S["counters"]["doc"] += 1
            did = f"amzn1.tortuga.4.eu.{S['counters']['doc']:06d}"
            S["documents"][did] = {"content": None, "kind": "input", "contentType": b["contentType"]}
            save()
            host = self.headers.get("Host", f"127.0.0.1:{PORT}")
            return self.send(201, {"feedDocumentId": did, "url": f"http://{host}/uploads/{did}"})
        if m == "POST" and p == "/feeds/2021-06-30/feeds":
            if self.limited("feeds_create"):
                return
            b = self.json_body()
            if not isinstance(b, dict):
                return self.send(400, {"errors": [{"code": "InvalidInput", "message": "Invalid JSON"}]})
            if b.get("feedType") != FEED_TYPE:
                return self.send(400, {"errors": [{"code": "InvalidInput", "message": f"feedType must be {FEED_TYPE}"}]})
            if amz["marketplace_id"] not in (b.get("marketplaceIds") or []):
                return self.send(400, {"errors": [{"code": "InvalidInput", "message": "marketplaceIds must include the UK marketplace A1F83G8C2ARO7P"}]})
            doc = S["documents"].get(b.get("inputFeedDocumentId"))
            if not doc or doc["kind"] != "input" or doc["content"] is None:
                return self.send(400, {"errors": [{"code": "InvalidInput", "message": "inputFeedDocumentId has no uploaded content"}]})
            S["counters"]["feed"] += 1
            fid = str(S["counters"]["feed"])
            S["feeds"][fid] = {"feedId": fid, "feedType": FEED_TYPE, "doc": b["inputFeedDocumentId"], "polls": 0,
                               "created": time.time(), "status": "IN_QUEUE", "result": None}
            save()
            return self.send(202, {"feedId": fid})
        mm = re.fullmatch(r"/feeds/2021-06-30/feeds/(\d+)", p)
        if m == "GET" and mm:
            if self.limited("feeds"):
                return
            f = S["feeds"].get(mm.group(1))
            if not f:
                return self.send(404, {"errors": [{"code": "NotFound", "message": "Feed not found"}]})
            f["polls"] += 1
            age = time.time() - f["created"]
            if f["status"] == "IN_QUEUE" and f["polls"] >= 2:
                f["status"] = "IN_PROGRESS"
            elif f["status"] == "IN_PROGRESS" and f["polls"] >= 3 and age >= 3:
                f["result"] = self.process_feed(S["documents"][f["doc"]]["content"])
                f["status"] = "DONE"
            save()
            out = {"feedId": f["feedId"], "feedType": f["feedType"], "marketplaceIds": [amz["marketplace_id"]],
                   "processingStatus": f["status"]}
            if f["status"] == "DONE":
                out["resultFeedDocumentId"] = f["result"]
            return self.send(200, out)
        mm = re.fullmatch(r"/feeds/2021-06-30/documents/(.+)", p)
        if m == "GET" and mm:
            if self.limited("feeds"):
                return
            d = S["documents"].get(mm.group(1))
            if not d:
                return self.send(404, {"errors": [{"code": "NotFound", "message": "Document not found"}]})
            host = self.headers.get("Host", f"127.0.0.1:{PORT}")
            return self.send(200, {"feedDocumentId": mm.group(1), "url": f"http://{host}/downloads/{mm.group(1)}"})
        return self.send(404, {"errors": [{"code": "NotFound", "message": "Resource not found"}]})

    def documents(self, m, path):
        kind, did = path.split("/")[1], unquote(path.split("/", 2)[2])
        d = S["documents"].get(did)
        if not d:
            return self.send(404, raw=b"NoSuchKey", ctype="text/plain")
        if kind == "uploads" and m == "PUT":
            if d["kind"] != "input":
                return self.send(403, raw=b"AccessDenied", ctype="text/plain")
            d["content"] = base64.b64encode(self.body()).decode()
            save()
            return self.send(200, raw=b"", ctype="text/plain")
        if kind == "downloads" and m == "GET":
            if d["content"] is None:
                return self.send(404, raw=b"NoSuchKey", ctype="text/plain")
            return self.send(200, raw=base64.b64decode(d["content"]), ctype="text/tab-separated-values; charset=UTF-8")
        return self.send(405, raw=b"MethodNotAllowed", ctype="text/plain")

    def process_feed(self, content_b64):
        raw = base64.b64decode(content_b64)
        errors, processed, ok = [], 0, 0
        try:
            text = raw.decode("utf-8")
        except UnicodeDecodeError:
            text = None
        lines = text.replace("\r\n", "\n").split("\n") if text is not None else []
        if text is None or not lines or lines[0].lstrip("﻿").split("\t") != FEED_HEADER:
            errors.append(("0", "", "90000", "Fatal",
                           "The header row is missing or invalid. Expected: " + "\t".join(FEED_HEADER) if text is not None
                           else "The file is not valid UTF-8 text"))
        else:
            seen = set()
            for n, line in enumerate(lines[1:], start=2):
                if not line.strip():
                    continue
                processed += 1
                cols = line.split("\t")
                if len(cols) != len(FEED_HEADER):
                    errors.append((str(n), cols[0] if cols else "", "90001", "Error", f"Expected {len(FEED_HEADER)} columns, found {len(cols)}"))
                    continue
                r = dict(zip(FEED_HEADER, cols))
                sku = r["sku"]
                l = self.listing(sku)
                if not l:
                    errors.append((str(n), sku, "8560", "Error", "SKU does not match any listing in your inventory. SKUs are case-sensitive."))
                    continue
                if sku in seen:
                    errors.append((str(n), sku, "8058", "Error", "The SKU appears more than once in this feed"))
                    continue
                seen.add(sku)
                fba = l["fulfillment_channel"] == "AMAZON_EU"
                fc = r["fulfillment-channel"]
                if fc and fc != l["fulfillment_channel"]:
                    errors.append((str(n), sku, "90057", "Error",
                                   f"fulfillment-channel {fc} does not match the listing ({l['fulfillment_channel']}); converting fulfilment is not allowed in this feed"))
                    continue
                if fba and (r["quantity"] or r["handling-time"]):
                    errors.append((str(n), sku, "90111", "Error", "quantity and handling-time cannot be set for Amazon-fulfilled listings"))
                    continue
                new = {}
                bad = None
                for col, key in (("price", "price"), ("minimum-seller-allowed-price", "min"), ("maximum-seller-allowed-price", "max")):
                    v = r[col]
                    if v == "":
                        continue
                    if not FEED_PRICE_RE.match(v) or float(v) <= 0:
                        bad = f"{col} '{v}' is invalid: use a positive number with exactly two decimals and no currency sign"
                        break
                    new[key] = v
                if bad:
                    errors.append((str(n), sku, "90220", "Error", bad)); continue
                if not fba:
                    if r["quantity"] != "":
                        if not re.fullmatch(r"\d+", r["quantity"]):
                            errors.append((str(n), sku, "90220", "Error", f"quantity '{r['quantity']}' must be a whole number >= 0")); continue
                        new["quantity"] = int(r["quantity"])
                    if r["handling-time"] != "":
                        if not re.fullmatch(r"\d+", r["handling-time"]) or not 1 <= int(r["handling-time"]) <= 30:
                            errors.append((str(n), sku, "90220", "Error", "handling-time must be a whole number of days from 1 to 30")); continue
                        new["handling_time"] = int(r["handling-time"])
                price = float(new.get("price", l["price"])); mn = float(new.get("min", l["min"])); mx = float(new.get("max", l["max"]))
                if not mn <= price <= mx:
                    errors.append((str(n), sku, "90244", "Error",
                                   f"price {price:.2f} is outside the minimum ({mn:.2f}) and maximum ({mx:.2f}) seller allowed price"))
                    continue
                l.update(new)
                ok += 1
        S["counters"]["doc"] += 1
        did = f"amzn1.tortuga.4.eu.{S['counters']['doc']:06d}"
        out = ["Feed Processing Summary:", f"\tNumber of records processed\t\t{processed}",
               f"\tNumber of records successful\t\t{ok}", "",
               "original-record-number\tsku\terror-code\terror-type\terror-message"]
        out += ["\t".join(e) for e in errors]
        S["documents"][did] = {"content": base64.b64encode(("\n".join(out) + "\n").encode()).decode(), "kind": "result"}
        return did


if __name__ == "__main__":
    S = load_state(reset="--reset" in sys.argv)
    if "--reset" in sys.argv:
        print("state reset to the client's original data")
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print(f"mock channels listening on http://127.0.0.1:{PORT}  (Ctrl+C to stop)"); sys.stdout.flush()
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass
