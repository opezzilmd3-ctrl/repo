# Source audit: Northfield Home & Garden (final, after the client update of 10 Oct 2026)

Sections 1–5 are the phase 1 audit of the original sources. Each finding is still true of those sources; where the client update changes the outcome, the entry says so. Section 6 covers the client-update files.

Sources checked: `sage_stock_export.csv` (24 stock codes), Shopify Admin API (17 products / 25 variants, read through all 4 pages at limit 5 and again at limit 10), `amazon_all_listings_report.txt` (26 listings), `amazon_fba_inventory_report.txt` (4 FBA listings), and the three supplier scans.
Input check: `sha256sum -c MANIFEST.sha256` gave all 15 files OK, and the folder matches INPUTS.md. The CSV and TSV files parse, all three scans open (1 page each, 200 dpi greyscale JPEG, no text layer), and the server answered `products/count.json` = 17.

Rule references (§) are to `channel_rules.md`.

## 1. Sage 50 export (`sage_stock_export.csv`)

| # | Problem | Evidence | Rule / resolution |
|---|---|---|---|
| S1 | File re-saved by Excel: cp1252 encoding, CRLF, en-dash bytes `0x96` in descriptions, trailing empty row `,,,,,,,,,,` | raw bytes (`M-^V`), last line | Parsed as cp1252. The blank row is ignored; it is not a stock code. |
| S2 | Prices lost trailing zeros (`7.5`, `32.5`, `15`) | NHG-1001, 1050, 1051, 1080 | Formatting only. Read as 7.50, 32.50, 15.00. |
| S3 | **Barcode in scientific notation** `5.06021E+12` (unreadable) | NHG-1003, NHG-1050 | §3 Excel damage: take the next source. Shopify `5060213450035` / `5060213450509` (both valid). The visible digits `506021` agree, so this is export damage, **not** a Sage correction. |
| S4 | **12-digit barcode** `841234509064` (Excel dropped the leading zero) | NHG-1090 | §3: restore to `0841234509064`. Check digit 4 is valid, so source = sage. Not a Sage correction. |
| S5 | **Invalid check digit** `5060213450616` (computed check digit is 5) | NHG-1061 | §3: take the next source, Shopify `5060213450615` (valid; Amazon product-id agrees). **Sage correction.** |
| S6 | **Shared barcode** `5060213450417` on NHG-1041 *and* NHG-1042 | Sage rows for Cedar and Linen | §3 shared barcode: the Shopify variant (4400000285) and Amazon listing NHG-1041 of **NHG-1041 (Cedar)** carry 417, so it belongs to 1041. NHG-1042 skips its Sage barcode and takes Shopify `5060213450424` (valid; Amazon agrees). **Sage correction for NHG-1042.** |
| S7 | **Missing barcode** | NHG-1081 Garden Kneeling Pad (blank) | §3: next source, Shopify `5060213450813` (valid). **Sage correction.** |
| S8 | **Stock code with a trailing space** `"NHG-1013 "` | Sage row 8 | §1: a stock code has the form `NHG-` + 4 digits. Whitespace is not part of the code, so it is trimmed to `NHG-1013` for every match. Reported for clean-up in Sage (it is not a barcode, so it is not in `sage_updates.csv`). |
| S9 | **Over-allocation**: 20 in stock, 22 allocated | NHG-1013 | §4: available = max(0, 20−22) = 0. Reported. *Final:* the stocktake counted 30, so available = 8 and the over-allocation is gone (Sage still shows 20 until the count is keyed in). |
| S10 | **Negative stock** −4 | NHG-1041 | §4: treated as 0. Reported. *Final:* the stocktake counted 12, so available = 12 (Sage still shows −4 until the count is keyed in). |
| S11 | **Inactive item still selling**: Inactive = Yes | NHG-1070 Hanging Bird Feeder: Shopify product was `active` with 18 in stock; Amazon FBM `NHG-1070` had qty 12; FBA `NHG-1070-FBA` holds 4 fulfillable units | §4 inactive: Shopify `draft` + inventory 0, Amazon FBM qty 0. FBA quantity is Amazon's and is never sent, so the 4 FBA units stay on sale. Reported to the client. |
| S12 | Kit has its own stock figures (0 / 0) | NHG-1030 | §4 kit: ignored. Kit available = min(1001: 35, 1011: 55, 1020: 200, 1021: 176, 1022: 5) = **5**, limited by NHG-1022 Coriander. *Final:* min(1001: 26, 1011: 55, 1020: 200, 1021: 176, 1022: **1**) = **1**. |
| S13 | Kit has no supplier or part ref, so it has no MAP | NHG-1030 | §5: price = charm(gross) = 22.99. Amazon minimum = listing price. |

## 2. Shopify (Admin API)

| # | Problem | Evidence | Rule / resolution |
|---|---|---|---|
| H1 | **SKU format differs** from Sage | v4400000208 `nhg-1002`, v4400000215 `NHG1003`, v4400000229 `nhg1011`, v4400000243 `NHG-1013 ` (trailing space) | §2 step 2, normalised SKU match. §1: SKU corrected to the Sage form. |
| H2 | **Blank SKUs** | v4400000236 (Stainless Hand Fork), v4400000264 (Herb Seeds / Coriander) | §2 step 3, barcode match: `5060213450127` = NHG-1012 and `5060213450226` = NHG-1022 (both are the correct Sage barcodes). SKUs set to NHG-1012 / NHG-1022. |
| H3 | **Duplicate product**: two products both match NHG-1011 | 8100000127 "Stainless Hand Trowel" created 2023-04-02 (SKU `nhg1011`, active) and 8100000283 "Stainless Hand Trowel" created **2026-08-21** (SKU `NHG-1011`, draft, inventory 5, same barcode) | §2: the later one (8100000283 / v4400000355) is the duplicate. Keep 8100000127. §4: duplicate inventory → 0, SKU blanked, then archived (done in that order). The kept variant then took SKU NHG-1011. |
| H4 | **Invalid barcode** `5060213450913` (computed check digit is 2) | v4400000369 NHG-1091 Solar Fairy Lights | §3: the Sage barcode `5060213450912` is valid, so it is correct. The Shopify barcode is reset to it. |
| H5 | **Missing barcode** | v4400000313 NHG-1060 Children's gloves | Set to the correct (Sage) barcode `5060213450608`. |
| H6 | **Weight mismatch** > 0.01 kg | NHG-1071 Wild Bird Seed Mix: Shopify 2.5 kg vs Sage 2 kg. NHG-1080 Coir Doormat: Shopify 1.2 kg vs Sage 2.1 kg | §6: reported only; Shopify weights not changed. Other weights in grams (seeds 20 g, NHG-1051 1100 g, NHG-1081 400 g) agree after g ÷ 1000. |
| H7 | **Inactive item active** | 8100000231 Hanging Bird Feeder `active`, inventory 18 | Set to `draft`, inventory 0 (S11). |
| H8 | **Prices off-rule / below MAP** | e.g. NHG-1011 7.99 (MAP 9.49), NHG-1003 21.99 (MAP 24.99), NHG-1013 14.99 (MAP 15.99), NHG-1080 17.99 (MAP 19.99), NHG-1002 12.99 (rule 13.99), NHG-1071 5.49 (rule 5.99) | §5 Shopify price = max(charm(gross), MAP-.99). |
| H9 | **Inventory differs from Sage available** on 19 variants (for example NHG-1013 showed 6 but has 0 available, and NHG-1041 showed 3 against negative stock) | see `shopify_updates.csv` | §4: Shopify inventory = available. |
| H10 | No Shopify variant is an orphan; every Sage code has exactly one kept variant. | crosswalk | — |

## 3. Amazon (All Listings + FBA inventory)

| # | Problem | Evidence | Rule / resolution |
|---|---|---|---|
| A1 | **SKU case differs**: `nhg-1002` | listing 1044Z01X4QQ | §1: Amazon SKUs are never changed. Matched by normalised SKU; the feed uses `nhg-1002` exactly. |
| A2 | **Auto-generated SKUs** | `2J-W8KQ-7ZPA` (EAN 5060213450127) and `7Q-ZX4M-PL2C` (EAN 5060213450608) | §1/§2 step 4, product-id: matched to NHG-1012 and NHG-1060. SKU kept. |
| A3 | **Orphan listing** | `OLD-WATERCAN-01` Galvanised Watering Can 9L, EAN 5060213459991, qty 3. There is no Sage code and no Sage/Shopify barcode match | §2: orphan. §4/§7: price 11.99 / min 9.99 / max 17.99 kept, quantity 0. |
| A4 | **Multipack listings** carry their own pack EANs (5060213459113, 5060213459205) | NHG-1011-X3, NHG-1020-X5 | Matched by SKU after removing `-X<n>`. Pack EANs are not used as item barcodes (§3 takes the item's own Amazon product-id). |
| A5 | **Multipack below n × MAP** | NHG-1011-X3 at 20.99 with min 18.00 (3 × MAP = 28.47) | §5 multipack: 28.99, min 28.47. |
| A6 | **FBA listing of an inactive item** | NHG-1070-FBA: 4 fulfillable, 2 unsellable | FBA stock is Amazon's: no quantity sent. Reported (client decides on a removal order). |
| A7 | **Listed quantities do not match Sage** (for example NHG-1013 listed 5 with 0 available; NHG-1041 listed 2 against negative stock; NHG-1030 kit listed 8 with only 5 buildable) | All Listings report | §4 FBM quantity = max(0, available − 1), packs ÷ n. |
| A8 | **Prices / min / max off-rule** | e.g. NHG-1003 min 19.99 below MAP 24.99; NHG-1040-FBA 12.99 is below Shopify price + FBA fee | §5. |
| A9 | Inconsistent product-id formatting: `0841234509064` (13 digits, correct) on Amazon vs 12 digits in the Sage export | NHG-1090-FBA | Confirms that S4 is Excel damage. |
| A10 | Items with no Amazon listing | NHG-1022, NHG-1081 | Not an error. Nothing is created (the feed is price/quantity only). |

## 4. Supplier price lists (scans)

| # | Observation | Resolution |
|---|---|---|
| P1 | The three lists use **different column orders**. Greenline: Trade, RRP, **MAP**. Hearth & Home: RRP, **MAP**, Trade. Terracotta: **MAP**, Trade, RRP. | Each MAP was read from the column headed "MAP £". Every row was checked again at native 200 dpi. |
| P2 | Terracotta scan is **rotated 90° anticlockwise** (2200×1700). | Rotated 90° clockwise before reading. |
| P3 | Lists include parts Northfield does not stock (GL-206, GL-304, GL-412, HH-504, HH-612, HH-803, TT-113, TT-131). | Kept in `supplier_map.csv` for completeness; not used. |
| P4 | Every Sage part ref (21 of them) has a MAP; the kit has none. | — |

## 5. Matching decisions that needed judgement

- **Trailing space in Sage `NHG-1013 `**: I treated the trimmed `NHG-1013` as the stock code (S8). Amazon `NHG-1013` therefore matches by `sku`. Shopify `NHG-1013 ` (also with a trailing space) matches by `normalised sku`, because it does not equal the code exactly.
- **Shared barcode order**: the owner of 417 was decided from the matched Shopify variant and Amazon listing (both SKU-matched to NHG-1041) before any barcode-based matching ran, so the decision does not depend on itself.
- **Duplicate**: both trowel products resolve to NHG-1011. The 2026 product matches by exact SKU and the 2023 one only by normalised SKU, but §2 decides by creation date, not match strength. The 2023 product is kept.

## 6. Client update (opened in Part 4)

| # | Source | Observation | Resolution |
|---|---|---|---|
| U1 | `email_from_priya_2026-10-10.md` | Four instructions: (1) stocktake counts are the new qty in stock, allocations unchanged; (2) use the Greenline rev2 list from 8 Oct; (3) discontinue NHG-1081; (4) use the 10 Oct FBA report. | Each applied as below. "Push only what needs to change" was followed: the Shopify diff was taken against the live state, and the Amazon feed sent only the changed rows (`amazon_price_quantity_delta.txt`, 8 rows). |
| U2 | `stocktake_2026-10-09.csv` (UTF-8, CRLF, column `counted_qty`) | Six counts: NHG-1001 31 (Sage 40), NHG-1013 30 (20), NHG-1022 2 (6), NHG-1041 12 (−4), NHG-1051 0 (9), NHG-1071 90 (90, unchanged). | `counted_qty` replaces qty_in_stock; Sage allocations are kept. The stock codes all match Sage exactly. |
| U3 | `greenline_price_list_rev2.pdf` (upright scan, no text layer, MAP is the last column as before) | Three MAPs changed: GL-202 9.49 → **10.99**, GL-204 15.99 → **13.99**, GL-411 6.99 → **7.49**. The rest are unchanged; the trade price is unchanged; RRP changed for GL-202 (13.99) and GL-204 (16.99). | `final/supplier_map.csv` uses rev2 for all Greenline rows (the scan column names rev2). |
| U4 | Email item 3 | NHG-1081 Garden Kneeling Pad discontinued. It has no Amazon listing. | §4 discontinued: Shopify inventory 0, *then* product archived (8100000270). Amazon: nothing to send. Its Sage barcode is still missing, so it stays in `sage_updates.csv`. |
| U5 | `amazon_fba_inventory_report_2026-10-10.txt` | Fulfillable: 1040-FBA 24 → 18, 1050-FBA 6 → 3, **1070-FBA 4 → 0** (2 unsellable), 1090-FBA 15 → 15. | Used for `fba_fulfillable` and the summary only; FBA quantities are never sent. FBA prices are unchanged because no Shopify price on an FBA item changed. |
