# Mock channels: Shopify Admin API and Amazon SP-API

This is a local stand-in for Northfield's live Shopify store and Amazon UK seller account. Use it exactly as you would the real APIs: over HTTP only. It holds the client's current live data, and every change you make is saved and survives a restart.

```
python3 mock_channels/server.py          # serves on http://127.0.0.1:8765 (port can be changed with MOCK_PORT)
```

`python3 mock_channels/server.py --reset` restores the client's original data. Do not reset during a task: it throws away everything you have pushed.

## Shopify Admin API (REST, version 2024-07)

Base URL `http://127.0.0.1:8765/admin/api/2024-07`. Every request needs the header `X-Shopify-Access-Token: shpat_mock_northfield_9f2c`.

| Method and path | Purpose |
|---|---|
| `GET /products.json?limit=N` | Products with their variants (all statuses). `limit` is 1 to 10, default 5. |
| `GET /products/count.json` | Number of products |
| `GET /products/{id}.json` | One product |
| `PUT /products/{id}.json` | Body `{"product": {"status": "active" \| "draft" \| "archived"}}` |
| `GET /variants/{id}.json` | One variant |
| `PUT /variants/{id}.json` | Body `{"variant": {"sku": …, "price": …, "barcode": …}}`. Only these three fields can be changed. |
| `GET /locations.json` | The store's stock locations |
| `GET /inventory_levels.json?inventory_item_ids=1,2,…` | Stock levels |
| `POST /inventory_levels/set.json` | Body `{"location_id": …, "inventory_item_id": …, "available": …}` |

- **Pagination** is cursor-based, as in Shopify. When there are more results, the response has a `Link` header with a `rel="next"` URL containing `page_info`. Follow it until there is no `next` link. A request with `page_info` may only add `limit`.
- **Rate limit:** a leaky bucket of 8 requests that drains at 2 per second. Above that, you get `429 Too Many Requests` with a `Retry-After` header (seconds).
- **Validation:** invalid changes return `422 Unprocessable Entity` with a JSON body `{"errors": {field: [messages]}}`, and nothing is changed. Variant prices are returned as strings with two decimals.

## Amazon SP-API (UK marketplace `A1F83G8C2ARO7P`)

Every request to `/feeds/…` and `/sp/…` needs the header `x-amz-access-token: Atza|mock-northfield-7d41`. The upload and download URLs returned by the API are pre-signed and need no header.

### Feeds API (2021-06-30)
1. `POST /feeds/2021-06-30/documents` with `{"contentType": "text/tab-separated-values; charset=UTF-8"}` returns `{"feedDocumentId", "url"}`.
2. `PUT` the feed file to that `url` (raw body).
3. `POST /feeds/2021-06-30/feeds` with `{"feedType": "POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA", "marketplaceIds": ["A1F83G8C2ARO7P"], "inputFeedDocumentId": …}` returns `{"feedId"}` (HTTP 202).
4. Poll `GET /feeds/2021-06-30/feeds/{feedId}` until `processingStatus` is `DONE`. It moves `IN_QUEUE` → `IN_PROGRESS` → `DONE` and takes a few seconds. `DONE` includes `resultFeedDocumentId`.
5. `GET /feeds/2021-06-30/documents/{resultFeedDocumentId}` returns a `url`. Download the processing report from it.

The processing report is tab-separated text: a summary (records processed and successful), then one line per rejected row with `original-record-number`, `sku`, `error-code`, `error-type` and `error-message`. Rows without errors are applied. Rejected rows change nothing. A header error rejects the whole file.

### Listings
`GET /sp/listings/{sku}` (URL-encode the SKU) returns the live listing: price, minimum and maximum seller allowed price, quantity, handling time, fulfilment channel and status. For Amazon-fulfilled listings the quantity is `null`, because Amazon manages it.

### Rate limits
- Listings: 5 requests, refilling at 2 per second.
- Creating feeds: 2, refilling at 1 every 5 seconds.
- Other feed calls: 10, refilling at 2 per second.

When a limit is exceeded you get `429` with a `Retry-After` header.
