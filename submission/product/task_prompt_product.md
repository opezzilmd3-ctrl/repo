I'm an e-commerce operations contractor. Northfield Home & Garden Ltd sells through its own Shopify store and on Amazon UK, while stock and prices live in Sage 50. The three systems have drifted apart, and the client wants one clean, reconciled product dataset pushed to both channels before go-live on 12 October. Work in the folder that contains sage_stock_export.csv, the two Amazon reports, fba_fee_tiers.csv, channel_rules.md, supplier_price_lists/, mock_channels/ and client_update/.

## Inputs
- sage_stock_export.csv: Sage 50 stock export. Someone opened and saved it in Excel, so expect damage.
- Shopify: available only through the mock Admin API. Start `python3 mock_channels/server.py` and read mock_channels/README.md. Treat the server as a black box: use it over HTTP only, and do not read or edit its other files. It paginates and rate-limits, and it validates what you send.
- amazon_all_listings_report.txt and amazon_fba_inventory_report.txt: Amazon reports (tab-separated). Updates go through the mock Amazon Feeds API on the same server.
- supplier_price_lists/: three supplier price lists. They are scans with no text layer (one is rotated), and no OCR software is installed, so you must read each one yourself. They hold the MAP for each supplier part reference, alongside trade and RRP prices that you must not confuse with it.
- channel_rules.md: the client's rules for matching, barcodes, stock, pricing and feeds. Follow them exactly.
- client_update/: changes that arrive after your first delivery. Do not open client_update/ until Part 4.
- INPUTS.md and MANIFEST.sha256: the list of input files and their checksums.

## Before you start: confirm the inputs
Check that you received the complete file set:
- Run `sha256sum -c MANIFEST.sha256` and compare the folder with INPUTS.md.
- Confirm that the CSV and report files parse and that the three supplier scans open as images.
- Start the server and confirm that it answers (for example `GET /admin/api/2024-07/products/count.json` with the token from the README).

If anything is missing, empty or unreadable, stop and tell me exactly what. Do not guess or work around missing client files. For client_update/, only the checksums are checked here; its contents are still opened only in Part 4.

## How to work
- Do all of the work yourself in this session. Do not hand any part of it to sub-agents, background tasks or parallel workers. I review your own trace, and work done elsewhere is not in it.
- Read each supplier scan yourself, one page at a time, at a size where every figure is legible (turn the rotated one upright first). Do not combine scans into a montage or contact sheet.
- Matching and audit decisions must come from the evidence in the files and the API, checked against channel_rules.md. Scripts are fine for mechanical work (parsing, calculating, calling the APIs, writing files), but look at the data yourself before you rely on a script's result.
- Work through to the end without stopping to ask me questions. Where the inputs leave something open, decide by the rules and record the reasoning in source_audit.md or exceptions_report.md. Stop early only for the input problem described above.

## Part 1: Reconcile (output/phase1/)
1. Pull every Shopify product and variant through the API (all pages). Read both Amazon reports and the Sage export. Read all three supplier scans and write supplier_map.csv (supplier, part_ref, description, MAP, and the scan it came from).
2. Write source_audit.md: every data problem you find in each source (damaged or invalid barcodes, shared barcodes, SKU format differences, blank SKUs, duplicate products, negative or over-allocated stock, inactive items still selling, orphan listings, weight mismatches), each with the evidence and the rule that resolves it.
3. Build master_products.csv: one row per Sage stock code, with columns stock_code, title (from Shopify), variant, vat_code, net_price, gross_price, map, shopify_price, correct_barcode, barcode_source, qty_in_stock, qty_allocated, available, active, weight_kg, shopify_product_id, shopify_variant_id, shopify_inventory_item_id, amazon_skus, fba_fulfillable, notes.
4. Build crosswalk.csv: every Shopify variant and every Amazon listing mapped to its Sage code (or marked orphan), with the match method (sku, normalised sku, barcode, product-id).
5. Produce the channel files: shopify_updates.csv (variant_id, current and new sku, price, barcode, inventory, and product status changes), amazon_price_quantity.txt (the exact feed file, one row per listing), and sage_updates.csv.

## Part 2: Sync tool (sync/)
Write a small Python tool that the client can rerun:
- shopify.py: a client with auth, Link-header pagination, 429 handling that honours Retry-After, and clear 422 error reporting.
- amazon.py: submits a feed, polls until DONE, fetches the processing report and returns the row errors.
- rules.py: the pricing, charm rounding, stock and barcode-check-digit logic from channel_rules.md.
- push.py: applies shopify_updates.csv and submits amazon_price_quantity.txt, logging every call and result to a push log.
- tests/ (unittest; run with `python3 -m unittest discover sync/tests`): check-digit validation, charm rounding edge cases (x.00, x.99, x.995 before rounding), multipack and FBA pricing, the kit stock calculation, Link pagination and the 429 retry. Make them pass.

## Part 3: Push and confirm (output/phase1/)
1. Push the Shopify updates and the Amazon feed with push.py. Read every API error and every row in the feed processing report. Fix the cause in your data or your code, never by hand-editing around it, and push again until both channels accept everything. Save push_log.csv.
2. Confirm the live state. Re-read every Shopify variant through the API and every Amazon listing through `GET /sp/listings/{sku}`, and compare them with master_products.csv and the feed file. Write live_check.csv listing each item, the expected and live values, and whether they match.
3. Write exceptions_report.md (everything that needs the client's attention: orphans, inactive items, stock problems, barcode corrections for Sage, the duplicate product, weight mismatches) and channel_summary.md (counts by channel, listings by fulfilment type, the total units offered per channel, and the items where MAP raised the price).

## Part 4: Client update (output/final/)
Now open client_update/ and apply everything in it under the rules. Rebuild the master, crosswalk and channel files, push only what changed (Shopify and an Amazon feed), handle any rejections, and confirm the live state again. output/final/ must contain the complete current version of every Part 1 and Part 3 file. Also write:
- changes_report.md: every field that changed for every Sage code, Shopify variant and Amazon listing between phase 1 and final, with the cause (stocktake, MAP update, discontinuation, FBA refresh, or a knock-on effect such as the kit).
- client_note.md: a short note to the client covering what changed, what was pushed, and what still needs her action in Sage.

## Verification
Before finishing:
- Look at every supplier scan again and confirm every MAP in supplier_map.csv.
- Recheck every barcode's check digit.
- Recompute every price and quantity independently from the rules (not with the same code path) and compare.
- Compare the live API state with output/final/.
- Run the tests again.

If you find a mismatch, fix the upstream cause, rebuild what depends on it, push the correction and check again. Write verification_log.md listing each check, the mismatches found, what you changed, the final live-check result for both channels and the test output.

## Acceptance checks (how I will judge the result)
- supplier_map.csv matches the scans exactly (MAP, not trade or RRP).
- master_products.csv has one correct row per Sage code, with the correct barcode, available stock, gross price, MAP and Shopify price under the rules.
- crosswalk.csv maps every Shopify variant and Amazon listing correctly, including blank SKUs and auto-generated Amazon SKUs, and identifies the orphan and the duplicate product.
- The live Shopify state (SKUs, prices, barcodes, inventory, statuses) and the live Amazon listings (prices, min/max, quantities) equal the final files, and FBA quantities are never sent.
- sage_updates.csv lists exactly the Sage barcode corrections that are needed.
- The tests pass and really exercise the rules, pagination, retries and feed handling.
- changes_report.md and client_note.md match the real differences between phase 1 and final, including knock-on effects.
- verification_log.md shows real independent checks, and no unresolved mismatch remains.

When finished, give me a short summary:
- the data problems found per source
- the barcode corrections
- the API and feed rejections you hit and how you fixed them
- the final Shopify and Amazon counts
- the items where MAP set the price
- what changed after the client update
- the test results
