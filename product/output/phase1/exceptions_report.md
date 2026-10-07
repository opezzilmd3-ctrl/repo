# Exceptions for the client (phase 1)

These items need a decision or a fix by Northfield. Everything else has been reconciled and pushed.

## 1. Barcode corrections needed in Sage (`sage_updates.csv`)

| Stock code | Sage value | Correct value | Why |
|---|---|---|---|
| NHG-1042 Soy Wax Candle – Linen | 5060213450417 | **5060213450424** | Sage gives Linen the Cedar barcode (NHG-1041). Shopify and Amazon both carry 417 on Cedar and 424 on Linen. |
| NHG-1061 Gardening Gloves – Adult | 5060213450616 | **5060213450615** | Check digit wrong (should be 5); Shopify and Amazon have …615. |
| NHG-1081 Garden Kneeling Pad | *(blank)* | **5060213450813** | Missing in Sage; taken from Shopify. |

Not Sage errors (no action in Sage). These values were damaged only when the export was opened in Excel:
- NHG-1003 and NHG-1050 were shown as `5.06021E+12`. Correct values are 5060213450035 and 5060213450509, which agree with the visible digits.
- NHG-1090 lost its leading zero. The correct value is 0841234509064.

Please export from Sage as text (or format the Barcode column as Text) next time.

## 2. Stock problems in Sage

| Stock code | Sage figures | Treated as | Action |
|---|---|---|---|
| NHG-1041 Soy Wax Candle – Cedar | in stock **−4** | available 0 (Shopify 0, Amazon 0) | Count the stock and correct the negative figure in Sage. |
| NHG-1013 Bypass Pruning Shears | 20 in stock, **22 allocated** | available 0 (Shopify 0, Amazon 0) | Over-allocated by 2. Check open orders and allocations. |
| NHG-1030 Herb Garden Starter Kit | own stock 0/0 (ignored) | kit available **5** | Limited by NHG-1022 Coriander seeds (5 available). Reorder coriander to sell more kits. |
| NHG-1013 stock code | stored as `"NHG-1013 "` (trailing space) | trimmed to NHG-1013 | Remove the trailing space from the stock code in Sage. |

## 3. Inactive item still selling

- **NHG-1070 Hanging Bird Feeder** is flagged Inactive in Sage, but it was active on both channels. Shopify product 8100000231 is now `draft` with inventory 0, and the Amazon FBM listing `NHG-1070` now has quantity 0.
- **NHG-1070-FBA** still holds **4 fulfillable units** (and 2 unsellable) at Amazon. Amazon owns FBA stock, so no quantity was sent. Its price has been set by the rules (20.99) and it is still buyable. If the item really is finished, raise a removal order or close the FBA listing in Seller Central. If it should not be inactive, clear the flag in Sage.

## 4. Orphan Amazon listing

- **`OLD-WATERCAN-01`** Galvanised Watering Can 9L (ASIN B04AC9C1B0, EAN 5060213459991) matches no Sage item by SKU or EAN. Its price, minimum and maximum are unchanged (11.99 / 9.99 / 17.99) and its quantity is set to 0 (it was 3). Either add the item to Sage or close the listing.

## 5. Duplicate Shopify product

- **8100000283 "Stainless Hand Trowel"** (created 2026-08-21, variant 4400000355) duplicated 8100000127 (created 2023-04-02). Its inventory was set to 0, its SKU blanked, and it was archived. Archived products cannot be edited, so delete it in Shopify admin if you don't need the record. The original product 8100000127 now carries SKU NHG-1011.

## 6. Weight mismatches (Shopify not changed; Sage is correct)

| Stock code | Sage | Shopify | Action |
|---|---|---|---|
| NHG-1071 Wild Bird Seed Mix 2kg | 2 kg | 2.5 kg | Correct the Shopify weight (it affects shipping rates). |
| NHG-1080 Coir Doormat | 2.1 kg | 1.2 kg | Correct the Shopify weight (looks like transposed digits). |

## 7. Other points for information

- Shopify barcode for NHG-1091 Solar Fairy Lights was `5060213450913` (bad check digit). It is now `5060213450912`, as in Sage.
- Shopify had blank SKUs on the Hand Fork (NHG-1012) and Coriander seeds (NHG-1022). They were matched by barcode and the SKUs are now set.
- Amazon SKU `nhg-1002` (lowercase) and the auto-generated SKUs `2J-W8KQ-7ZPA` (NHG-1012) and `7Q-ZX4M-PL2C` (NHG-1060) were left as they are, because Amazon SKUs cannot be changed. If you want consistent SKUs, you would have to relist.
- NHG-1022 Coriander and NHG-1081 Kneeling Pad have no Amazon listing.
- Amazon marks FBM listings with quantity 0 as *Inactive*: NHG-1013, NHG-1041, NHG-1070 and OLD-WATERCAN-01. They come back automatically when stock is sent.
