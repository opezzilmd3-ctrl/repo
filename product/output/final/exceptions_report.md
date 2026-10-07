# Exceptions for the client (final, after the 10 Oct update)

These items need Northfield's attention. Everything else is reconciled, pushed and confirmed live.

## 1. Barcode corrections needed in Sage (`sage_updates.csv`, unchanged from phase 1)

| Stock code | Sage value | Correct value | Why |
|---|---|---|---|
| NHG-1042 Soy Wax Candle – Linen | 5060213450417 | **5060213450424** | Sage gives Linen the Cedar barcode (NHG-1041). Shopify and Amazon both carry 417 on Cedar and 424 on Linen. |
| NHG-1061 Gardening Gloves – Adult | 5060213450616 | **5060213450615** | Check digit wrong (should be 5); Shopify and Amazon have …615. |
| NHG-1081 Garden Kneeling Pad | *(blank)* | **5060213450813** | Missing in Sage. The item is now discontinued, but the record should still carry its correct barcode before it is made inactive. |

Not Sage errors (no action in Sage). These values were damaged only when the export was opened in Excel:
- NHG-1003 and NHG-1050 were shown as `5.06021E+12`. Correct values are 5060213450035 and 5060213450509.
- NHG-1090 lost its leading zero. The correct value is 0841234509064.

## 2. Stock: stocktake counts to key into Sage

The channels now use these counts. Sage still holds the old figures until they are keyed in.

| Stock code | Sage now | Counted | Available now |
|---|---|---|---|
| NHG-1001 Glazed Plant Pot – Small | 40 | **31** | 26 (5 allocated) |
| NHG-1013 Bypass Pruning Shears | 20 | **30** | 8. This also clears the phase 1 over-allocation (22 allocated). |
| NHG-1022 Organic Herb Seeds – Coriander | 6 | **2** | 1. This limits the Herb Garden Starter Kit to **1**. |
| NHG-1041 Soy Wax Candle – Cedar | **−4** | **12** | 12. This fixes the negative stock. |
| NHG-1051 Wool Throw – Oat | 9 | **0** | 0. Out of stock on both channels. |
| NHG-1071 Wild Bird Seed Mix 2kg | 90 | 90 | 84 (no change) |

Other stock points:
- **NHG-1030 Herb Garden Starter Kit**: only 1 can be built (Coriander). Shopify shows 1. The Amazon FBM quantity is 0 because of the 1-unit buffer, so the kit is effectively off Amazon until coriander is restocked.
- **NHG-1013** stock code is stored in Sage as `"NHG-1013 "` (trailing space). Remove the space.

## 3. Discontinued item

- **NHG-1081 Garden Kneeling Pad**: Shopify inventory was set to 0, then product 8100000270 was archived. There is no Amazon listing. Mark it inactive in Sage, as planned. The 41 units in stock (Sage) are still yours to clear through another route.

## 4. Inactive item

- **NHG-1070 Hanging Bird Feeder** (Inactive in Sage): Shopify is `draft` with inventory 0, and the Amazon FBM listing has quantity 0.
- **NHG-1070-FBA**: the 10 Oct FBA report shows **0 fulfillable and 2 unsellable** units (it was 4 fulfillable on the earlier report). The listing is still active at 20.99. Close it, or raise a removal/disposal order for the 2 unsellable units in Seller Central.

## 5. Orphan Amazon listing

- **`OLD-WATERCAN-01`** Galvanised Watering Can 9L (EAN 5060213459991) matches no Sage item. Its quantity is 0 and its price and limits are unchanged (11.99 / 9.99 / 17.99). Add it to Sage or close the listing.

## 6. Duplicate Shopify product

- **8100000283 "Stainless Hand Trowel"** (created 2026-08-21) duplicated 8100000127 (created 2023-04-02). It now has inventory 0 and a blank SKU, and it is archived. Delete it in Shopify admin if the record is not needed.

## 7. Weight mismatches (Sage is correct; Shopify not changed)

| Stock code | Sage | Shopify |
|---|---|---|
| NHG-1071 Wild Bird Seed Mix 2kg | 2 kg | 2.5 kg |
| NHG-1080 Coir Doormat | 2.1 kg | 1.2 kg |

## 8. MAP changes to note (Greenline rev2, from 8 Oct)

- NHG-1011 Hand Trowel: MAP 9.49 → 10.99. Price is now 10.99 everywhere, and the Amazon 3-pack is now 32.99.
- NHG-1013 Pruning Shears: MAP 15.99 → 13.99. MAP no longer sets the price, which falls back to the rule price of 14.99.
- NHG-1061 Adult Gloves: MAP 6.99 → 7.49. Price rises from 6.99 to 7.99.

## 9. For information

- The Amazon SKUs `nhg-1002`, `2J-W8KQ-7ZPA` (NHG-1012) and `7Q-ZX4M-PL2C` (NHG-1060) are kept, because Amazon SKUs cannot be changed.
- These FBM listings now have quantity 0 and Amazon shows them as Inactive: **NHG-1030** (kit), **NHG-1051**, **NHG-1070** and **OLD-WATERCAN-01**. NHG-1013 and NHG-1041 are back in stock.
