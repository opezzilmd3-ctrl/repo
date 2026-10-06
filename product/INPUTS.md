# Task inputs: Northfield Home & Garden product reconciliation (complete set)

| Path | What it is |
|---|---|
| sage_stock_export.csv | Sage 50 stock export (24 stock codes), opened and saved in Excel (cp1252, CRLF) |
| amazon_all_listings_report.txt | Amazon UK All Listings report, tab-separated (26 listings) |
| amazon_fba_inventory_report.txt | Amazon FBA inventory report, tab-separated (4 FBA listings) |
| fba_fee_tiers.csv | FBA fulfilment fee tiers by weight |
| channel_rules.md | The client's rules for matching, barcodes, stock, pricing and feeds |
| supplier_price_lists/greenline_price_list.pdf | Greenline Garden Supplies price list: scanned image, no text layer |
| supplier_price_lists/hearth_home_price_list.pdf | Hearth & Home Wholesale price list: scanned image, no text layer |
| supplier_price_lists/terracotta_trading_price_list.pdf | Terracotta Trading Co price list: scanned image, no text layer, rotated |
| mock_channels/server.py | Mock Shopify Admin API and Amazon SP-API server (Python 3 standard library only) |
| mock_channels/README.md | How to use the mock APIs |
| mock_channels/data/seed.json | The server's starting data (part of the black box; not for the agent to read) |
| client_update/email_from_priya_2026-10-10.md | Client's email with the changes (Part 4 only) |
| client_update/stocktake_2026-10-09.csv | Stocktake counts (Part 4 only) |
| client_update/greenline_price_list_rev2.pdf | Greenline revised price list: scanned image (Part 4 only) |
| client_update/amazon_fba_inventory_report_2026-10-10.txt | Refreshed FBA inventory report (Part 4 only) |

15 input files, plus this list and MANIFEST.sha256. Check them with `sha256sum -c MANIFEST.sha256`.
The server creates mock_channels/data/state.json when it first runs; that file is not an input.
All people, companies, products, barcodes and addresses are fictional. The .test domains are reserved and do not exist.
