# Changes report: phase 1 → final

This compares `output/phase1/` with `output/final/` field by field, using a script diff of master, Shopify targets, the Amazon feed, the crosswalk and the Sage updates. Every difference is listed below with its cause.
Causes: **stocktake** (stocktake_2026-10-09.csv), **MAP update** (Greenline rev2), **discontinuation** (NHG-1081), **FBA refresh** (FBA report of 10 Oct), and **knock-on** (a change that follows from another).

## 1. Sage codes (`master_products.csv`)

| Stock code | Field | Phase 1 | Final | Cause |
|---|---|---|---|---|
| NHG-1001 | qty_in_stock | 40 | 31 | stocktake |
| NHG-1001 | available | 35 | 26 | stocktake (31 − 5 allocated) |
| NHG-1011 | map | 9.49 | 10.99 | MAP update (GL-202) |
| NHG-1011 | shopify_price | 9.99 | 10.99 | MAP update (MAP-.99 of 10.99 = 10.99 > charm(7.50) = 7.99) |
| NHG-1013 | map | 15.99 | 13.99 | MAP update (GL-204) |
| NHG-1013 | shopify_price | 15.99 | 14.99 | MAP update (MAP-.99 13.99 < charm(14.99) = 14.99; MAP no longer sets the price) |
| NHG-1013 | qty_in_stock | 20 | 30 | stocktake |
| NHG-1013 | available | 0 | 8 | stocktake (30 − 22 allocated; over-allocation cleared) |
| NHG-1022 | qty_in_stock | 6 | 2 | stocktake |
| NHG-1022 | available | 5 | 1 | stocktake (2 − 1 allocated) |
| NHG-1030 (kit) | available | 5 | 1 | **knock-on**: kit = min(1001: 26, 1011: 55, 1020: 200, 1021: 176, 1022: 1) = 1 |
| NHG-1040 | fba_fulfillable | 24 | 18 | FBA refresh |
| NHG-1041 | qty_in_stock | −4 | 12 | stocktake |
| NHG-1041 | available | 0 | 12 | stocktake (negative stock cleared) |
| NHG-1050 | fba_fulfillable | 6 | 3 | FBA refresh |
| NHG-1051 | qty_in_stock | 9 | 0 | stocktake |
| NHG-1051 | available | 9 | 0 | stocktake |
| NHG-1061 | map | 6.99 | 7.49 | MAP update (GL-411) |
| NHG-1061 | shopify_price | 6.99 | 7.99 | MAP update (MAP-.99 of 7.49 = 7.99 > charm(7.00) = 6.99; MAP now sets the price) |
| NHG-1070 | fba_fulfillable | 4 | 0 | FBA refresh |
| NHG-1081 | active | Yes | Discontinued | discontinuation |

The `notes` column was updated to match on NHG-1001, 1011, 1013, 1022, 1041, 1051, 1061, 1071 and 1081. For example, "over-allocated" and "negative stock" are gone from 1013 and 1041, and stocktake and discontinuation notes were added.

No change: gross prices, VAT codes, barcodes and barcode sources, weights, Shopify and Amazon IDs, `amazon_skus`. NHG-1071 was counted at 90, the same as Sage. NHG-1090-FBA stayed at 15.

## 2. Shopify variants (targets in `shopify_updates.csv`; all pushed and confirmed live)

| Variant | Stock code | Field | Phase 1 | Final | Cause |
|---|---|---|---|---|---|
| 4400000201 | NHG-1001 | inventory | 35 | 26 | stocktake |
| 4400000229 | NHG-1011 | price | 9.99 | 10.99 | MAP update |
| 4400000243 | NHG-1013 | price | 15.99 | 14.99 | MAP update |
| 4400000243 | NHG-1013 | inventory | 0 | 8 | stocktake |
| 4400000264 | NHG-1022 | inventory | 5 | 1 | stocktake |
| 4400000271 | NHG-1030 | inventory | 5 | 1 | knock-on (kit, from NHG-1022 and NHG-1001) |
| 4400000285 | NHG-1041 | inventory | 0 | 12 | stocktake |
| 4400000306 | NHG-1051 | inventory | 9 | 0 | stocktake |
| 4400000320 | NHG-1061 | price | 6.99 | 7.99 | MAP update |
| 4400000348 | NHG-1081 | inventory | 41 | 0 | discontinuation (set first) |
| 8100000270 (product of 4400000348) | NHG-1081 | status | active | archived | discontinuation (after inventory 0) |

The other 16 variants did not change, and no SKU or barcode changed.

## 3. Amazon listings (`amazon_price_quantity.txt`; the 8 changed rows were sent as `amazon_price_quantity_delta.txt`)

| SKU | Field | Phase 1 | Final | Cause |
|---|---|---|---|---|
| NHG-1001 | quantity | 34 | 25 | stocktake |
| NHG-1011 | price | 9.99 | 10.99 | MAP update |
| NHG-1011 | minimum-seller-allowed-price | 9.49 | 10.99 | MAP update |
| NHG-1011 | maximum-seller-allowed-price | 14.99 | 16.49 | knock-on (price × 1.5) |
| NHG-1011-X3 | price | 28.99 | 32.99 | **knock-on** of the MAP update: pack floor 3 × 10.99 = 32.97 → 32.99 |
| NHG-1011-X3 | minimum-seller-allowed-price | 28.47 | 32.97 | knock-on (3 × MAP) |
| NHG-1011-X3 | maximum-seller-allowed-price | 43.49 | 49.49 | knock-on (price × 1.5) |
| NHG-1013 | price | 15.99 | 14.99 | MAP update |
| NHG-1013 | minimum-seller-allowed-price | 15.99 | 13.99 | MAP update |
| NHG-1013 | maximum-seller-allowed-price | 23.99 | 22.49 | knock-on (price × 1.5) |
| NHG-1013 | quantity | 0 | 7 | stocktake (8 − 1 buffer) |
| NHG-1030 | quantity | 4 | 0 | **knock-on** (kit available 1 − 1 buffer) |
| NHG-1041 | quantity | 0 | 11 | stocktake |
| NHG-1051 | quantity | 8 | 0 | stocktake |
| NHG-1061 | price | 6.99 | 7.99 | MAP update |
| NHG-1061 | minimum-seller-allowed-price | 6.99 | 7.49 | MAP update |
| NHG-1061 | maximum-seller-allowed-price | 10.49 | 11.99 | knock-on (price × 1.5) |

The other 18 listings did not change. That includes all four FBA listings: no FBA item's Shopify price changed, so their prices stand, and FBA quantities are never sent. NHG-1081 has no Amazon listing, so the discontinuation needed no Amazon change.

## 4. Unchanged files

- `crosswalk.csv`: identical. Matching is done on the source data, and no listing or variant was added or removed.
- `sage_updates.csv`: identical (NHG-1042, NHG-1061, NHG-1081).
- `supplier_map.csv`: GL-202, GL-204 and GL-411 MAPs changed, and the scan column of all Greenline rows now points to `client_update/greenline_price_list_rev2.pdf`.
