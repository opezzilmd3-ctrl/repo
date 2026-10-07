"""Shopify pagination/429/422 and Amazon feed handling, against a fake HTTP opener."""
import io
import json
import os
import sys
import unittest
import urllib.error
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
from shopify import ShopifyClient, ShopifyError, parse_link_header  # noqa: E402
from amazon import AmazonClient, parse_processing_report  # noqa: E402


class FakeResp:
    def __init__(self, status, body, headers=None):
        self.status = status
        self.headers = headers or {}
        self._body = body.encode() if isinstance(body, str) else body

    def read(self):
        return self._body


def http_error(url, status, body, headers):
    return urllib.error.HTTPError(url, status, "err", headers, io.BytesIO(body.encode()))


class FakeServer:
    """Records requests; `handler(req)` returns (status, body, headers)."""

    def __init__(self, handler):
        self.handler = handler
        self.requests = []

    def __call__(self, req):
        self.requests.append(req)
        status, body, headers = self.handler(req)
        if status >= 400:
            raise http_error(req.full_url, status, body, headers)
        return FakeResp(status, body, headers)


class ShopifyPagination(unittest.TestCase):
    def test_parse_link_header(self):
        h = ('<https://x/products.json?limit=2&page_info=abc>; rel="previous", '
             '<https://x/products.json?limit=2&page_info=def>; rel="next"')
        self.assertEqual(parse_link_header(h)["next"], "https://x/products.json?limit=2&page_info=def")
        self.assertEqual(parse_link_header(""), {})

    def test_follows_next_until_absent(self):
        products = [{"id": i} for i in range(7)]

        def handler(req):
            q = parse_qs(urlparse(req.full_url).query)
            limit = int(q["limit"][0])
            start = int(q.get("page_info", ["0"])[0])
            page = products[start:start + limit]
            headers = {}
            if start + limit < len(products):
                nxt = f"http://h/admin/api/2024-07/products.json?limit={limit}&page_info={start + limit}"
                headers["Link"] = f'<{nxt}>; rel="next"'
            return 200, json.dumps({"products": page}), headers

        srv = FakeServer(handler)
        c = ShopifyClient(base="http://h", opener=srv, sleep=lambda s: None)
        got = c.all_products(limit=3)
        self.assertEqual([p["id"] for p in got], list(range(7)))
        self.assertEqual(len(srv.requests), 3)
        # page_info requests carry only limit + page_info
        q = parse_qs(urlparse(srv.requests[1].full_url).query)
        self.assertEqual(set(q), {"limit", "page_info"})
        self.assertEqual(srv.requests[0].get_header("X-shopify-access-token"), "shpat_mock_northfield_9f2c")


class ShopifyRetry(unittest.TestCase):
    def test_429_honours_retry_after(self):
        calls = {"n": 0}

        def handler(req):
            calls["n"] += 1
            if calls["n"] <= 2:
                return 429, '{"errors":"Exceeded"}', {"Retry-After": "1.5"}
            return 200, '{"count": 17}', {}

        slept = []
        c = ShopifyClient(base="http://h", opener=FakeServer(handler), sleep=slept.append)
        self.assertEqual(c.product_count(), 17)
        self.assertEqual(slept, [1.5, 1.5])

    def test_429_gives_up_after_max_retries(self):
        c = ShopifyClient(base="http://h", max_retries=2, sleep=lambda s: None,
                          opener=FakeServer(lambda r: (429, "{}", {"Retry-After": "0"})))
        with self.assertRaises(ShopifyError) as cm:
            c.product_count()
        self.assertEqual(cm.exception.status, 429)

    def test_422_reported_clearly(self):
        body = json.dumps({"errors": {"barcode": ["is not a valid EAN-13"], "sku": ["has already been taken"]}})
        c = ShopifyClient(base="http://h", sleep=lambda s: None,
                          opener=FakeServer(lambda r: (422, body, {})))
        with self.assertRaises(ShopifyError) as cm:
            c.update_variant(1, {"barcode": "123"})
        e = cm.exception
        self.assertEqual(e.status, 422)
        self.assertIn("barcode: is not a valid EAN-13", e.describe())
        self.assertIn("sku: has already been taken", e.describe())
        self.assertIn("PUT", str(e))


class AmazonFeed(unittest.TestCase):
    REPORT = ("Feed Processing Summary:\n"
              "\tNumber of records processed\t3\n"
              "\tNumber of records successful\t2\n\n"
              "original-record-number\tsku\terror-code\terror-type\terror-message\n"
              "2\tNHG-1040-FBA\t8541\tError\tQuantity cannot be set for AFN listings\n")

    def test_parse_report(self):
        parsed = parse_processing_report(self.REPORT)
        self.assertEqual(parsed["summary"]["Number of records processed"], "3")
        self.assertEqual(parsed["summary"]["Number of records successful"], "2")
        self.assertEqual(len(parsed["errors"]), 1)
        self.assertEqual(parsed["errors"][0]["sku"], "NHG-1040-FBA")
        self.assertEqual(parsed["errors"][0]["error-code"], "8541")

    def test_submit_polls_until_done_and_returns_errors(self):
        state = {"polls": 0, "uploaded": None, "created": 0}

        def handler(req):
            u = urlparse(req.full_url)
            if req.get_method() == "POST" and u.path == "/feeds/2021-06-30/documents":
                return 200, json.dumps({"feedDocumentId": "doc1", "url": "http://h/upload/doc1"}), {}
            if req.get_method() == "PUT" and u.path == "/upload/doc1":
                assert req.get_header("X-amz-access-token") is None  # pre-signed
                state["uploaded"] = req.data.decode()
                return 200, "", {}
            if req.get_method() == "POST" and u.path == "/feeds/2021-06-30/feeds":
                state["created"] += 1
                if state["created"] == 1:
                    return 429, "{}", {"Retry-After": "5"}
                body = json.loads(req.data)
                assert body["feedType"] == "POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA"
                assert body["inputFeedDocumentId"] == "doc1"
                return 202, json.dumps({"feedId": "F1"}), {}
            if u.path == "/feeds/2021-06-30/feeds/F1":
                state["polls"] += 1
                st = ["IN_QUEUE", "IN_PROGRESS", "DONE"][min(state["polls"] - 1, 2)]
                body = {"feedId": "F1", "processingStatus": st}
                if st == "DONE":
                    body["resultFeedDocumentId"] = "res1"
                return 200, json.dumps(body), {}
            if u.path == "/feeds/2021-06-30/documents/res1":
                return 200, json.dumps({"url": "http://h/download/res1"}), {}
            if u.path == "/download/res1":
                return 200, self.REPORT, {}
            return 404, "{}", {}

        slept = []
        c = AmazonClient(base="http://h", opener=FakeServer(handler), sleep=slept.append, poll_interval=0.5)
        feed_id, feed, report, parsed = c.submit_feed("sku\tprice\nNHG-1001\t8.99\n")
        self.assertEqual(feed_id, "F1")
        self.assertEqual(feed["processingStatus"], "DONE")
        self.assertEqual(state["polls"], 3)
        self.assertEqual(state["uploaded"], "sku\tprice\nNHG-1001\t8.99\n")
        self.assertIn(5.0, slept)               # honoured Retry-After on createFeed
        self.assertEqual(slept.count(0.5), 2)   # two polls before DONE
        self.assertEqual([e["sku"] for e in parsed["errors"]], ["NHG-1040-FBA"])


if __name__ == "__main__":
    unittest.main()
