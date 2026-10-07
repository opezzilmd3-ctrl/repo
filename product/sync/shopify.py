"""Minimal Shopify Admin REST client (2024-07) for the Northfield sync tool.

Features: token auth, Link-header cursor pagination, 429 retry honouring
Retry-After, and clear reporting of 422 validation errors.
"""
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "2024-07"
DEFAULT_BASE = "http://127.0.0.1:8765"
DEFAULT_TOKEN = "shpat_mock_northfield_9f2c"


class ShopifyError(Exception):
    def __init__(self, status, method, path, body):
        self.status = status
        self.method = method
        self.path = path
        self.body = body
        super().__init__(f"{method} {path} -> HTTP {status}: {self.describe()}")

    def describe(self):
        """Flatten a 422 body {"errors": {field: [msg, ...]}} into readable text."""
        errs = self.body.get("errors") if isinstance(self.body, dict) else None
        if isinstance(errs, dict):
            return "; ".join(f"{f}: {', '.join(m) if isinstance(m, list) else m}"
                             for f, m in errs.items())
        if errs is not None:
            return str(errs)
        return json.dumps(self.body) if not isinstance(self.body, str) else self.body


def parse_link_header(value):
    """Return {rel: url} from an RFC 5988 Link header."""
    links = {}
    if not value:
        return links
    for part in value.split(","):
        m = re.match(r'\s*<([^>]*)>\s*;\s*rel="?([^";]+)"?', part)
        if m:
            links[m.group(2)] = m.group(1)
    return links


class ShopifyClient:
    def __init__(self, base=DEFAULT_BASE, token=DEFAULT_TOKEN, max_retries=8,
                 sleep=time.sleep, opener=None, log=None):
        self.base = base.rstrip("/")
        self.token = token
        self.max_retries = max_retries
        self.sleep = sleep
        self.opener = opener or urllib.request.urlopen
        self.log = log  # optional callable(dict)

    def _url(self, path):
        if path.startswith("http://") or path.startswith("https://"):
            return path
        return f"{self.base}/admin/api/{API_VERSION}/{path.lstrip('/')}"

    def request(self, method, path, body=None):
        """Send a request; returns (status, json_body, headers). Retries 429s."""
        url = self._url(path)
        data = json.dumps(body).encode() if body is not None else None
        attempt = 0
        while True:
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header("X-Shopify-Access-Token", self.token)
            req.add_header("Accept", "application/json")
            if data is not None:
                req.add_header("Content-Type", "application/json")
            try:
                resp = self.opener(req)
                status, headers, raw = resp.status, dict(resp.headers), resp.read()
            except urllib.error.HTTPError as e:
                status, headers, raw = e.code, dict(e.headers or {}), e.read()
            try:
                payload = json.loads(raw.decode() or "null")
            except ValueError:
                payload = raw.decode(errors="replace")
            if status == 429 and attempt < self.max_retries:
                wait = float(_header(headers, "Retry-After") or 1)
                attempt += 1
                if self.log:
                    self.log({"method": method, "url": url, "status": 429,
                              "result": f"rate limited; retry {attempt} after {wait}s"})
                self.sleep(wait)
                continue
            if self.log:
                self.log({"method": method, "url": url, "status": status,
                          "request": body, "response": payload})
            if status >= 400:
                raise ShopifyError(status, method, url, payload)
            return status, payload, headers

    def get(self, path):
        return self.request("GET", path)[1]

    def put(self, path, body):
        return self.request("PUT", path, body)[1]

    def post(self, path, body):
        return self.request("POST", path, body)[1]

    def paginate(self, path, key):
        """Yield every item under `key`, following rel="next" Link headers."""
        url = path
        while url:
            _, payload, headers = self.request("GET", url)
            for item in payload.get(key, []):
                yield item
            url = parse_link_header(_header(headers, "Link")).get("next")

    # convenience wrappers
    def all_products(self, limit=10):
        return list(self.paginate(f"products.json?limit={limit}", "products"))

    def product_count(self):
        return self.get("products/count.json")["count"]

    def locations(self):
        return self.get("locations.json")["locations"]

    def inventory_levels(self, item_ids):
        out = []
        ids = list(item_ids)
        for i in range(0, len(ids), 50):
            chunk = ",".join(str(x) for x in ids[i:i + 50])
            out.extend(self.paginate(f"inventory_levels.json?inventory_item_ids={chunk}",
                                     "inventory_levels"))
        return out

    def update_variant(self, variant_id, fields):
        return self.put(f"variants/{variant_id}.json", {"variant": fields})

    def set_status(self, product_id, status):
        return self.put(f"products/{product_id}.json", {"product": {"status": status}})

    def set_inventory(self, location_id, inventory_item_id, available):
        return self.post("inventory_levels/set.json",
                         {"location_id": location_id,
                          "inventory_item_id": inventory_item_id,
                          "available": available})


def _header(headers, name):
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            return v
    return None
