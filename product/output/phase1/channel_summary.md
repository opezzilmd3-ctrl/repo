# Channel summary (phase 1, live state confirmed)

## Counts

| | Count |
|---|---|
| Sage stock codes | 24 (23 active, 1 inactive: NHG-1070) |
| Shopify products | 17: 15 active, 1 draft (8100000231 Bird Feeder, inactive), 1 archived (8100000283 duplicate) |
| Shopify variants | 25: 24 matched to Sage codes, 1 duplicate |
| Amazon listings | 26: 25 matched, 1 orphan (OLD-WATERCAN-01) |
| Sage barcode corrections | 3 (NHG-1042, NHG-1061, NHG-1081) |

## Amazon listings by fulfilment type

| Type | Listings | SKUs |
|---|---|---|
| FBM single | 20 (19 matched + 1 orphan) | includes `nhg-1002`, `2J-W8KQ-7ZPA`, `7Q-ZX4M-PL2C`, `OLD-WATERCAN-01` |
| FBM multipack | 2 | NHG-1011-X3, NHG-1020-X5 |
| FBA | 4 | NHG-1040-FBA, NHG-1050-FBA, NHG-1070-FBA, NHG-1090-FBA |

## Units offered

| Channel | Units |
|---|---|
| Shopify (sum of inventory, all on active products) | **1,037** |
| Amazon FBM singles (sum of quantity) | **882** across 19 listings (16 with stock; NHG-1013, NHG-1041, NHG-1070 and the orphan are 0) |
| Amazon FBM multipacks | **57 packs**: NHG-1011-X3 18 packs (54 trowels), NHG-1020-X5 39 packs (195 seed packets) |
| Amazon FBM total (feed quantity column) | **939** |
| Amazon FBA fulfillable (Amazon's stock, not sent) | **49**: NHG-1040-FBA 24, NHG-1050-FBA 6, NHG-1070-FBA 4, NHG-1090-FBA 15 |

The channel totals overlap: Shopify, FBM singles and FBM packs all draw on the same Sage stock. The 1-unit FBM buffer and the pack division keep Amazon below Sage availability. FBA stock is separate (held at Amazon).

## Where MAP set the price

| Item | Gross | charm(gross) | MAP | Price set |
|---|---|---|---|---|
| NHG-1003 Glazed Plant Pot – Large (Shopify + Amazon FBM) | 22.00 | 21.99 | 24.99 | **24.99** |
| NHG-1011 Stainless Hand Trowel (Shopify + Amazon FBM) | 7.50 | 7.99 | 9.49 | **9.99** |
| NHG-1013 Bypass Pruning Shears (Shopify + Amazon FBM) | 14.99 | 14.99 | 15.99 | **15.99** |
| NHG-1080 Coir Doormat (Shopify + Amazon FBM) | 18.00 | 17.99 | 19.99 | **19.99** |
| NHG-1011-X3 Trowel pack of 3 (Amazon) | 3 × 7.50 × 0.9 = 20.25 | 20.99 | 3 × 9.49 = 28.47 | **28.99** |
| NHG-1020-X5 Basil seeds pack of 5 (Amazon) | 5 × 1.65 × 0.9 = 7.43 | 7.99 | 5 × 1.99 = 9.95 | **9.99** |

The FBA listings of NHG-1003, 1011, 1013 and 1080 do not exist. All FBA prices come from the Shopify price plus the fee: 1040 9.99+3.38 → 13.99, 1050 38.99+4.27 → 43.99, 1070 16.99+3.38 → 20.99, 1090 24.99+3.38 → 28.99.

## Push result

- Shopify: 23 variants changed with 32 successful calls (inventory 19, variant 11, status 2). No 422s; 12 rate-limit 429s were retried per Retry-After.
- Amazon: feed 50001 processed 26 of 26 records successfully, with 0 row errors.
- Live check (`live_check.csv`): Shopify 125 of 125 fields match and Amazon 156 of 156 fields match. All 4 FBA listings show quantity `null` (not sent).
