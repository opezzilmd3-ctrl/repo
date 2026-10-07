"""Minimal Amazon SP-API Feeds client (2021-06-30) for the Northfield sync tool."""
import csv
import io
import json
import time
import urllib.error
import urllib.parse
import urllib.request

DEFAULT_BASE = "http://127.0.0.1:8765"
DEFAULT_TOKEN = "Atza|mock-northfield-7d41"
MARKETPLACE_UK = "A1F83G8C2ARO7P"
FEED_TYPE = "POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA"
CONTENT_TYPE = "text/tab-separated-values; charset=UTF-8"


class AmazonError(Exception):
    pass


class AmazonClient:
    def __init__(self, base=DEFAULT_BASE, token=DEFAULT_TOKEN, max_retries=10,
                 sleep=time.sleep, opener=None, log=None, poll_interval=1.0, poll_timeout=120):
        self.base = base.rstrip("/")
        self.token = token
        self.max_retries = max_retries
        self.sleep = sleep
        self.opener = opener or urllib.request.urlopen
        self.log = log
        self.poll_interval = poll_interval
        self.poll_timeout = poll_timeout

    def _raw(self, method, url, data=None, headers=None, signed=True):
        attempt = 0
        while True:
            req = urllib.request.Request(url, data=data, method=method)
            if signed:
                req.add_header("x-amz-access-token", self.token)
            for k, v in (headers or {}).items():
                req.add_header(k, v)
            try:
                resp = self.opener(req)
                status, hdrs, body = resp.status, dict(resp.headers), resp.read()
            except urllib.error.HTTPError as e:
                status, hdrs, body = e.code, dict(e.headers or {}), e.read()
            if status == 429 and attempt < self.max_retries:
                wait = float(_header(hdrs, "Retry-After") or 1)
                attempt += 1
                if self.log:
                    self.log({"method": method, "url": url, "status": 429,
                              "result": f"rate limited; retry {attempt} after {wait}s"})
                self.sleep(wait)
                continue
            if self.log:
                self.log({"method": method, "url": url, "status": status,
                          "response": body[:500].decode(errors="replace")})
            if status >= 400:
                raise AmazonError(f"{method} {url} -> HTTP {status}: {body.decode(errors='replace')}")
            return status, body

    def _json(self, method, path, body=None):
        data = json.dumps(body).encode() if body is not None else None
        hdrs = {"Content-Type": "application/json"} if data is not None else {}
        _, raw = self._raw(method, self.base + path, data, hdrs)
        return json.loads(raw.decode() or "null")

    # ------------------------------------------------------------------ feeds
    def create_document(self):
        return self._json("POST", "/feeds/2021-06-30/documents", {"contentType": CONTENT_TYPE})

    def upload(self, url, content):
        self._raw("PUT", url, content.encode("utf-8"), {"Content-Type": CONTENT_TYPE}, signed=False)

    def create_feed(self, document_id, feed_type=FEED_TYPE):
        return self._json("POST", "/feeds/2021-06-30/feeds",
                          {"feedType": feed_type, "marketplaceIds": [MARKETPLACE_UK],
                           "inputFeedDocumentId": document_id})["feedId"]

    def get_feed(self, feed_id):
        return self._json("GET", f"/feeds/2021-06-30/feeds/{feed_id}")

    def wait_for_feed(self, feed_id):
        waited = 0.0
        while True:
            feed = self.get_feed(feed_id)
            if feed.get("processingStatus") in ("DONE", "CANCELLED", "FATAL"):
                return feed
            if waited >= self.poll_timeout:
                raise AmazonError(f"feed {feed_id} still {feed.get('processingStatus')} after {waited}s")
            self.sleep(self.poll_interval)
            waited += self.poll_interval

    def get_report(self, document_id):
        doc = self._json("GET", f"/feeds/2021-06-30/documents/{document_id}")
        _, raw = self._raw("GET", doc["url"], signed=False)
        return raw.decode("utf-8")

    def submit_feed(self, content):
        """Upload, submit, poll to DONE and return (feed_id, feed, report_text, parsed)."""
        doc = self.create_document()
        self.upload(doc["url"], content)
        feed_id = self.create_feed(doc["feedDocumentId"])
        feed = self.wait_for_feed(feed_id)
        if feed.get("processingStatus") != "DONE":
            raise AmazonError(f"feed {feed_id} ended {feed.get('processingStatus')}")
        report = self.get_report(feed["resultFeedDocumentId"])
        return feed_id, feed, report, parse_processing_report(report)

    # --------------------------------------------------------------- listings
    def get_listing(self, sku):
        return self._json("GET", "/sp/listings/" + urllib.parse.quote(sku, safe=""))


def parse_processing_report(text):
    """Return {"summary": {...}, "errors": [ {original-record-number, sku, ...}, ... ]}."""
    summary, errors, header = {}, [], None
    for line in text.splitlines():
        if not line.strip():
            continue
        cells = line.split("\t")
        if header is None and "original-record-number" in cells:
            header = cells
            continue
        if header is not None:
            errors.append(dict(zip(header, cells)))
        else:
            # summary lines: "label<TAB>value" or "label: value" (possibly indented)
            cells = [c.strip() for c in cells if c.strip()]
            if len(cells) >= 2:
                summary[cells[0].rstrip(":")] = cells[-1]
            elif ":" in line:
                k, v = line.split(":", 1)
                summary[k.strip()] = v.strip()
            else:
                summary[line.strip()] = ""
    return {"summary": summary, "errors": errors}


def read_feed_file(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def feed_rows(content):
    return list(csv.DictReader(io.StringIO(content), delimiter="\t"))


def _header(headers, name):
    for k, v in (headers or {}).items():
        if k.lower() == name.lower():
            return v
    return None
