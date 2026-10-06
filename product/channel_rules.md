# Northfield Home & Garden Ltd: channel rules

These rules govern the product data in Sage 50, Shopify and Amazon UK. **Sage 50 is the master** for stock codes, VAT codes, net prices, stock, weights and whether an item is active. Shopify owns titles and its own product, variant and inventory-item IDs. Amazon owns ASINs, its listing SKUs and FBA stock.

## 1. Stock codes and SKUs
- Sage stock codes have the form `NHG-` followed by four digits (for example `NHG-1011`).
- Shopify SKUs must equal the Sage stock code exactly. Shopify SKUs that differ only in format are corrected to the Sage form.
- **Normalised SKU** (for matching only): uppercase, remove all spaces, and if the result is `NHG` followed directly by four digits, insert the hyphen. `nhg1011`, `NHG1011 ` and `nhg-1011` all normalise to `NHG-1011`.
- **Amazon SKUs are never changed.** Feeds must use the SKU exactly as Amazon has it.
  - `<stock code>` is a merchant-fulfilled (FBM) single.
  - `<stock code>-FBA` is the FBA listing of that item.
  - `<stock code>-X<n>` is a merchant-fulfilled multipack of n units of that item.
  - Any other SKU (for example Amazon's auto-generated `2J-W8KQ-7ZPA` style) is matched by its product-id (EAN).

## 2. Matching (record the method used for each row of the crosswalk)
Try these in order and use the first that works:
1. `sku`: the SKU equals a Sage stock code exactly (after removing an Amazon `-FBA` / `-X<n>` suffix).
2. `normalised sku`: the normalised SKU equals a Sage stock code.
3. `barcode`: a Shopify variant's barcode equals an item's correct barcode (section 3).
4. `product-id`: an Amazon listing's product-id (EAN) equals an item's correct barcode.

A listing or variant that matches nothing is an **orphan**.
If two Shopify products match the same Sage code, the one created later is a **duplicate**. Keep the earlier product.

## 3. Barcodes (EAN-13)
- An EAN-13 is valid only when it has exactly 13 digits and a correct check digit. To compute the check digit, weight the first 12 digits alternately 1, 3, 1, 3 … from the left, sum them, and take (10 − sum mod 10) mod 10.
- **Correct barcode for a Sage item:** use the first of these that is valid:
  1. the Sage barcode
  2. the Shopify variant barcode
  3. the Amazon product-id
- **Shared barcode:** if two Sage items carry the same barcode, it belongs to the item whose Shopify variant or Amazon product-id also carries it. The other item skips its Sage barcode and takes the next source.
- Record which source it came from in `barcode_source` (`sage`, `shopify` or `amazon`).
- **Excel damage:** the Sage export was opened and saved in Excel.
  - A 12-digit Sage barcode is an EAN-13 whose leading zero Excel removed. Restore the zero before checking it.
  - A barcode shown in scientific notation (for example `5.06021E+12`) is unreadable, so take the barcode from the next source.
  - Excel damage is a fault of the export file, not of Sage. If the restored or unreadable value is consistent with the correct barcode (same leading digits), **do not** list it in `sage_updates.csv`.
- **Sage corrections:** `sage_updates.csv` lists every item whose barcode is wrong **in Sage itself** (invalid check digit, belonging to another item, or missing), with the correct value. Columns: `stock_code, field, sage_value, correct_value, reason`.
- Shopify variant barcodes are set to the correct barcode.

## 4. Stock
- `available = qty_in_stock − qty_allocated`, but never below 0.
  - Negative stock in Sage is a data problem: treat it as 0 and report it.
  - Allocations above stock (over-allocation) also give 0 and must be reported.
- **Kit:** `NHG-1030` Herb Garden Starter Kit is assembled to order from 1 × NHG-1001, 1 × NHG-1011, 1 × NHG-1020, 1 × NHG-1021 and 1 × NHG-1022.
  - Kit available = the lowest value of (component available ÷ quantity per kit), rounded down.
  - The kit's own Sage stock figures are ignored.
- **Inactive items** (Sage inactive flag set):
  - Shopify product status `draft`, Shopify inventory 0.
  - Amazon FBM quantity 0.
- **Discontinued items** (when the client says so):
  - Shopify product status `archived`, inventory 0 (set before archiving).
  - Amazon FBM quantity 0.
- **Duplicate Shopify product:** set its inventory to 0, blank its variant SKU, then archive it. Archived products cannot be edited.
- **Shopify inventory** = available.
- **Amazon FBM quantity:**
  - Singles: `max(0, available − 1)`. The 1 unit is a buffer against overselling.
  - Multipacks of n: `floor(max(0, available − 1) ÷ n)`.
  - Orphan FBM listings get quantity 0.
- **FBA stock is Amazon's.** Never send a quantity for an FBA listing. Report FBA fulfillable stock from the FBA inventory report.

## 5. Pricing
- **VAT codes:** T0 = 0 %, T1 = 20 %, T5 = 5 %.
- **Gross price** = net price × (1 + VAT rate), rounded to the penny, with half-pennies rounded up.
- **Charm rounding** of a price p (already rounded to the penny):
  - If p ends in .99, keep it.
  - If p ends in .00, take off 1p (20.00 → 19.99).
  - Otherwise raise it to the .99 of the same pound (13.50 → 13.99).
- **MAP** (minimum advertised price) comes from the supplier price lists, per supplier part reference. Do not confuse it with the trade price or the RRP. The lowest price ending in .99 that is not below a MAP m is called **MAP-.99**: it is m itself if m ends in .99, otherwise the .99 of the same pound (20.00 → 20.99, 9.49 → 9.99).
- **Shopify price** = charm(gross), but never below MAP-.99. Items with no MAP (the kit) use charm(gross).
- **Amazon FBM single:** price = Shopify price.
- **Amazon FBA:** price = the lowest price ending in .99 that is not below (Shopify price + FBA fee).
  - The FBA fee comes from `fba_fee_tiers.csv` by the **Sage** weight: the first tier whose `max_weight_kg` is greater than or equal to the weight.
- **Amazon multipack of n:** price = the higher of charm(n × gross × 0.90) and the lowest .99 price not below n × MAP.
  - Round n × gross × 0.90 to the penny (half up) before charm rounding.
  - The pack's MAP is n × the item's MAP.
- **Amazon minimum price** (`minimum-seller-allowed-price`) = the listing's MAP (n × MAP for packs). If the item has no MAP, use the listing price.
- **Amazon maximum price** = listing price × 1.5, rounded to the penny (half up).

## 6. Weights
Sage weights (kg) are correct. Compare Shopify weights after converting units (g ÷ 1000). A difference over 0.01 kg is a weight mismatch. Report it; do not change Shopify weights.

## 7. Amazon feed
- Use the Feeds API with feed type `POST_FLAT_FILE_PRICEANDQUANTITYONLY_UPDATE_DATA`.
- The feed is a tab-separated text file, UTF-8, with this exact header row and one row per Amazon listing, in the order of the All Listings report:

```
sku	price	minimum-seller-allowed-price	maximum-seller-allowed-price	quantity	handling-time	fulfillment-channel
```

- Prices are written with two decimals and no currency sign.
- FBM rows: `handling-time` 2, `fulfillment-channel` `DEFAULT`.
- FBA rows: `quantity` and `handling-time` blank, `fulfillment-channel` `AMAZON_EU`.
- Orphan listings keep their current price, minimum and maximum, with quantity 0.

## 8. Shopify updates
- Change only what differs from the target (SKU, price, barcode, inventory, product status).
- Inventory is set through the inventory levels endpoint at the client's single location.
