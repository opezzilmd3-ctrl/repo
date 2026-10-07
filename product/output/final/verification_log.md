# Verification log

## 0. Input check (before any work)
- `sha256sum -c MANIFEST.sha256`: all 15 files OK. The folder matches INPUTS.md.
- The Sage CSV (cp1252), both Amazon TSVs and fba_fee_tiers.csv parse. Each of the 3 supplier PDFs (and later the rev2 PDF) is one page holding a 200 dpi greyscale JPEG with no text layer.
- The server answered `GET /admin/api/2024-07/products/count.json` → `{"count": 17}`, and `locations.json` returned one location (7788001).

## 1. Supplier scans re-read: every MAP confirmed
I looked at each scan again, one at a time, as a native-resolution crop of its table (Terracotta rotated 90° clockwise first), and compared every row with `supplier_map.csv`:

| Scan | Rows | MAP column | Result |
|---|---|---|---|
| greenline_price_list.pdf | 14 | last (Trade, RRP, **MAP**) | 14/14 match `phase1/supplier_map.csv` |
| hearth_home_price_list.pdf | 11 | middle (RRP, **MAP**, Trade) | 11/11 match (phase 1 and final) |
| terracotta_trading_price_list.pdf (rotated) | 6 | first (**MAP**, Trade, RRP) | 6/6 match (phase 1 and final) |
| client_update/greenline_price_list_rev2.pdf | 14 | last | 14/14 match `final/supplier_map.csv` (GL-202 10.99, GL-204 13.99, GL-411 7.49) |

No mismatches. No trade price or RRP appears in either map.

## 2. Barcode check digits rechecked
`sync/verify_independent.py` has its own EAN-13 routine and does not import `rules.py`. It checked 52 barcodes per output set: 24 master `correct_barcode`, 25 Shopify target barcodes and 3 `sage_updates` values. It also compared every master barcode and source with values derived by hand from the evidence (Excel-damaged NHG-1003/1050 → Shopify; 1042 shared → Shopify 424; 1061 invalid → Shopify 615; 1081 missing → Shopify 813; 1090 restored zero → Sage; every other code → its valid Sage value). It confirmed that `sage_updates.csv` is exactly {1042, 1061, 1081}. **0 mismatches** in phase 1 and in final.

## 3. Prices and quantities recomputed independently
`verify_independent.py` recomputes everything from the raw inputs: the Sage CSV, the stocktake, the FBA report, supplier_map, the fee tiers and the All Listings report. It uses integer pence and thousandths with explicit half-up rounding, its own charm and ".99 ceiling" logic, and its own kit and FBM-buffer arithmetic. No code is shared with `rules.py` or `build.py`. It compares:
- master: available, qty_in_stock, gross, MAP, Shopify price for all 24 codes
- Shopify targets: SKU, price, barcode, inventory, status for all 25 variants (including duplicate → blank SKU / 0 / archived)
- Amazon feed: all 7 columns for all 26 rows, in report order (FBA rows with blank quantity and handling time; orphan rows with original prices and qty 0; packs at n × MAP and charm(n × gross × 0.9))
- master `fba_fulfillable` against the relevant FBA report

Result: phase 1 **0 mismatches**; final **0 mismatches**.

To prove the checker can fail, I made a scratch copy of `final/` with three planted errors (X3 pack price 20.99, kit available 5, NHG-1091 barcode …913). It reported all three (5 mismatch lines) and exited 1.

## 4. Live API state compared with output/final/
- `sync/live_check.py` (uses the sync clients) re-read all 17 products and 25 variants with inventory levels, and all 26 listings through `GET /sp/listings/{sku}`. Result: **Shopify 125/125 fields match, Amazon 156/156 fields match** (`final/live_check.csv`). All 4 FBA listings have live quantity `null` (never sent).
- `verify_independent.py --live` repeated the comparison with a separate plain-urllib reader that has its own Link pagination (limit 3) and its own 429 handling. Result: **25 variants and 26 listings, 0 mismatches**.

## 5. Tests
`python3 -m unittest discover sync/tests` → **Ran 29 tests, OK**:

```
test_parse_report (test_clients.AmazonFeed.test_parse_report) ... ok
test_submit_polls_until_done_and_returns_errors (test_clients.AmazonFeed.test_submit_polls_until_done_and_returns_errors) ... ok
test_follows_next_until_absent (test_clients.ShopifyPagination.test_follows_next_until_absent) ... ok
test_parse_link_header (test_clients.ShopifyPagination.test_parse_link_header) ... ok
test_422_reported_clearly (test_clients.ShopifyRetry.test_422_reported_clearly) ... ok
test_429_gives_up_after_max_retries (test_clients.ShopifyRetry.test_429_gives_up_after_max_retries) ... ok
test_429_honours_retry_after (test_clients.ShopifyRetry.test_429_honours_retry_after) ... ok
test_fba_fee_tiers_boundaries (test_rules.ChannelPricing.test_fba_fee_tiers_boundaries) ... ok
test_fba_price (test_rules.ChannelPricing.test_fba_price) ... ok
test_multipack_map_wins (test_rules.ChannelPricing.test_multipack_map_wins) ... ok
test_multipack_rounds_before_charm (test_rules.ChannelPricing.test_multipack_rounds_before_charm) ... ok
test_check_digit_zero_case (test_rules.CheckDigit.test_check_digit_zero_case) ... ok
test_excel_repair (test_rules.CheckDigit.test_excel_repair) ... ok
test_valid_codes (test_rules.CheckDigit.test_valid_codes) ... ok
test_wrong_check_digit (test_rules.CheckDigit.test_wrong_check_digit) ... ok
test_wrong_length_or_chars (test_rules.CheckDigit.test_wrong_length_or_chars) ... ok
test_charm_other (test_rules.Rounding.test_charm_other) ... ok
test_charm_x00 (test_rules.Rounding.test_charm_x00) ... ok
test_charm_x99 (test_rules.Rounding.test_charm_x99) ... ok
test_charm_x995_rounds_first (test_rules.Rounding.test_charm_x995_rounds_first) ... ok
test_gross_half_penny_up (test_rules.Rounding.test_gross_half_penny_up) ... ok
test_map_99 (test_rules.Rounding.test_map_99) ... ok
test_min_max (test_rules.Rounding.test_min_max) ... ok
test_shopify_price_map_floor (test_rules.Rounding.test_shopify_price_map_floor) ... ok
test_normalise (test_rules.Skus.test_normalise) ... ok
test_split (test_rules.Skus.test_split) ... ok
test_available_never_negative (test_rules.Stock.test_available_never_negative) ... ok
test_fbm_quantity (test_rules.Stock.test_fbm_quantity) ... ok
test_kit (test_rules.Stock.test_kit) ... ok
----------------------------------------------------------------------
Ran 29 tests in 0.003s
OK
```

The client tests use a fake HTTP opener. They cover 3-page Link pagination (and check that page_info requests carry only limit + page_info), two 429s with `Retry-After: 1.5` honoured, giving up after max retries, the 422 field-error message, and a feed lifecycle (429 on createFeed honoured, pre-signed upload sent without the token, IN_QUEUE → IN_PROGRESS → DONE polling, report download and row-error parsing).

## 6. Mismatches found during the work and what I changed

| # | Found by | Mismatch | Fix (upstream) | Re-check |
|---|---|---|---|---|
| 1 | first test run | `parse_processing_report` lost the summary because the report lines are tab-indented (empty first cell) | `amazon.py`: summary parsing ignores empty cells | 29/29 tests pass; the real reports 50001/50002 parse (26/26, 8/8) |
| 2 | phase 1 → final diff | The first final build matched Shopify against the *post-push* live state, so the final crosswalk showed blank-SKU variants as `sku` matches and the duplicate as a `barcode` match, and the original problem notes were gone | `build.py`: matching and the crosswalk use the source snapshot (`--shopify-snapshot`); the "current" values come from the state before the final push (`--current-snapshot`). Final rebuilt. | The rebuilt `shopify_updates.csv` and feed are byte-identical to what was pushed, so no re-push was needed. The crosswalk match methods are identical to phase 1. Phase 1 rebuild is byte-identical (git clean). |
| 3 | push-log tally | channel_summary said 12 variant calls in phase 1; the log shows 11 | corrected (32 successful Shopify calls) | — |
| 4 | feed recount | channel_summary listing counts for FBM singles (19/15) were wrong | corrected to 20 listings, 16 with stock, in both phases | recount from the feed files |
| 5 | changes_report review | "other 14 variants unchanged" should be 16 (25 − 9) | corrected | — |

No API or feed rejections occurred in either push. Shopify returned 0 × 422 (14 × 429 were retried per Retry-After), and both feeds processed every record with 0 row errors. So no data fix was needed for a rejection.

## 7. Final result
- Shopify live = final files: 25/25 variants, 125/125 fields.
- Amazon live = final feed: 26/26 listings, 156/156 fields. FBA quantity is null on all 4 FBA listings; no FBA quantity was ever sent (checked in the phase 1 feed, the final feed and the delta feed).
- Independent recompute: 0 mismatches. Tests: 29/29 OK.
- **No unresolved mismatch remains.**
