# Form notes: product data reconciliation task (final rework)

**Title:** Product data reconciliation across Sage 50, Shopify and Amazon UK, with API sync and go-live changes

**Response to the review:**
The previous submission attached the wrong file (a PNG screenshot) instead of the input archive. This rework attaches the complete input archive, **PRODUCT_task_inputs_COMPLETE.zip (about 0.7 MB)**, containing every input the prompt names:
- INPUTS.md and MANIFEST.sha256
- sage_stock_export.csv
- amazon_all_listings_report.txt and amazon_fba_inventory_report.txt
- fba_fee_tiers.csv
- channel_rules.md
- the three scans in supplier_price_lists/ (image-only, one rotated)
- mock_channels/ (server.py, README.md, data/seed.json)
- the four files in client_update/ (email, stocktake CSV, revised price-list scan, refreshed FBA report)

The archive was extracted into an empty folder and verified:
- every SHA-256 checksum in MANIFEST.sha256 matches
- no file is empty
- every scan opens as an image
- the mock server starts and serves both APIs

The prompt is unchanged from the one used in the self-test.

**Self-test (fresh session, complete inputs, unchanged prompt):**
- **Steps: 81.** Counted by count_steps.py from the native Claude Code session log. The log is attached as trace/product_selftest_session.jsonl, together with the step-count screenshot.
- The run completed all four parts and the verification:
  - 24 master rows
  - crosswalk of 25 Shopify variants and 26 Amazon listings, including the orphan, the duplicate product, blank SKUs and auto-generated Amazon SKUs
  - the 3 required Sage barcode corrections
  - a sync tool with 29 passing unittest tests
  - pushes through the mock Shopify and Amazon Feeds APIs, with rejections handled
  - the client update applied with its knock-on effects (kit stock, multipack price)
  - a live check matching every field on both channels (Shopify 125/125, Amazon 156/156)
  - an independent recompute with 0 mismatches

**Data:** All people, companies, products, barcodes and addresses are fictional and were created for this task; the .test domains are reserved. No third-party or licensed data is included.
