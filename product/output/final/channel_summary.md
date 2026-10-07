# Channel summary (final, live state confirmed)

## Counts

| | Count |
|---|---|
| Sage stock codes | 24: 22 on sale, 1 inactive (NHG-1070), 1 discontinued (NHG-1081) |
| Shopify products | 17: **14 active**, 1 draft (8100000231 Bird Feeder, inactive), **2 archived** (8100000283 duplicate; 8100000270 Kneeling Pad, discontinued) |
| Shopify variants | 25: 24 matched to Sage codes, 1 duplicate. 22 on active products. |
| Amazon listings | 26: 25 matched, 1 orphan (OLD-WATERCAN-01) |
| Sage barcode corrections | 3 (NHG-1042, NHG-1061, NHG-1081) |

## Amazon listings by fulfilment type

| Type | Listings | SKUs |
|---|---|---|
| FBM single | 20 (19 matched + 1 orphan) | includes `nhg-1002`, `2J-W8KQ-7ZPA`, `7Q-ZX4M-PL2C`, `OLD-WATERCAN-01` |
| FBM multipack | 2 | NHG-1011-X3, NHG-1020-X5 |
| FBA | 4 | NHG-1040-FBA, NHG-1050-FBA, NHG-1070-FBA, NHG-1090-FBA |

## Units offered

| Channel | Final | Phase 1 |
|---|---|---|
| Shopify (sum of inventory; all on active products) | **990** | 1,037 |
| Amazon FBM singles | **879** across 20 FBM single listings (16 with stock; zero on NHG-1030, NHG-1051, NHG-1070, OLD-WATERCAN-01) | 882 |
| Amazon FBM multipacks | **57 packs**: NHG-1011-X3 18 (54 trowels), NHG-1020-X5 39 (195 seed packets) | 57 |
| Amazon FBM total (feed quantity column) | **936** | 939 |
| Amazon FBA fulfillable (10 Oct report; Amazon's stock, not sent) | **36**: 1040-FBA 18, 1050-FBA 3, 1070-FBA 0, 1090-FBA 15 | 49 |

Shopify, FBM singles and FBM packs all draw on the same Sage stock, so their totals overlap. FBA stock is held separately at Amazon.

Shopify change from 1,037 to 990: NHG-1001 −9, NHG-1022 −4, kit −4, NHG-1013 +8, NHG-1041 +12, NHG-1051 −9, NHG-1081 −41 (discontinued).

## Where MAP set the price (final)

| Item | Gross | charm(gross) | MAP | Price set |
|---|---|---|---|---|
| NHG-1003 Glazed Plant Pot – Large (Shopify + Amazon FBM) | 22.00 | 21.99 | 24.99 | **24.99** |
| NHG-1011 Stainless Hand Trowel (Shopify + Amazon FBM) | 7.50 | 7.99 | 10.99 (rev2) | **10.99** |
| NHG-1061 Gardening Gloves – Adult (Shopify + Amazon FBM) | 7.00 | 6.99 | 7.49 (rev2) | **7.99** (new in final) |
| NHG-1080 Coir Doormat (Shopify + Amazon FBM) | 18.00 | 17.99 | 19.99 | **19.99** |
| NHG-1011-X3 Trowel pack of 3 (Amazon) | 3 × 7.50 × 0.9 = 20.25 | 20.99 | 3 × 10.99 = 32.97 | **32.99** |
| NHG-1020-X5 Basil seeds pack of 5 (Amazon) | 5 × 1.65 × 0.9 = 7.43 | 7.99 | 5 × 1.99 = 9.95 | **9.99** |

No longer MAP-set: **NHG-1013** Pruning Shears. Its MAP fell to 13.99 (rev2), so the price is charm(14.99) = **14.99** (it was 15.99 in phase 1).

FBA prices (Shopify price + fee by Sage weight, then up to .99) are unchanged: 1040 13.99, 1050 43.99, 1070 20.99, 1090 28.99.

## Push result

| Push | Shopify | Amazon |
|---|---|---|
| Phase 1 | 23 variants, 32 successful calls (inventory 19, variant 11, status 2). 0 × 422; 12 × 429 retried per Retry-After. | Feed 50001: 26/26 records successful, 0 row errors |
| Final (changes only) | 9 variants, 11 successful calls (inventory 7, variant 3, status 1). 0 × 422; 2 × 429 retried. | Feed 50002 (delta, 8 rows): 8/8 successful, 0 row errors |

Live check (`live_check.csv`): Shopify 125/125 and Amazon 156/156 fields match the final files. All 4 FBA listings show quantity `null`.
