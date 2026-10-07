"""Northfield channel rules (channel_rules.md) as pure functions.

All money is handled as Decimal and rounded half-up to the penny.
"""
import csv
import re
from decimal import Decimal, ROUND_HALF_UP, ROUND_FLOOR

PENNY = Decimal("0.01")
VAT_RATES = {"T0": Decimal("0"), "T1": Decimal("0.20"), "T5": Decimal("0.05")}
KIT_CODE = "NHG-1030"
KIT_COMPONENTS = {"NHG-1001": 1, "NHG-1011": 1, "NHG-1020": 1, "NHG-1021": 1, "NHG-1022": 1}
STOCK_CODE_RE = re.compile(r"^NHG-\d{4}$")


def D(x):
    return x if isinstance(x, Decimal) else Decimal(str(x))


def money(x):
    """Round to the penny, half-pennies up."""
    return D(x).quantize(PENNY, rounding=ROUND_HALF_UP)


def fmt(x):
    return f"{money(x):.2f}"


# ---------- SKUs ----------
def normalise_sku(sku):
    s = (sku or "").upper().replace(" ", "")
    s = re.sub(r"\s+", "", s)
    if re.fullmatch(r"NHG\d{4}", s):
        s = "NHG-" + s[3:]
    return s


def split_amazon_sku(sku):
    """Return (base, kind, pack_n): kind is 'FBM', 'FBA' or 'PACK'."""
    m = re.fullmatch(r"(.*)-FBA", sku)
    if m:
        return m.group(1), "FBA", 1
    m = re.fullmatch(r"(.*)-X(\d+)", sku)
    if m:
        return m.group(1), "PACK", int(m.group(2))
    return sku, "FBM", 1


# ---------- Barcodes ----------
def ean13_check_digit(first12):
    if not (len(first12) == 12 and first12.isdigit()):
        raise ValueError("need 12 digits")
    total = sum(int(c) * (1 if i % 2 == 0 else 3) for i, c in enumerate(first12))
    return (10 - total % 10) % 10


def is_valid_ean13(code):
    code = (code or "").strip()
    return len(code) == 13 and code.isdigit() and ean13_check_digit(code[:12]) == int(code[12])


def repair_excel_barcode(raw):
    """Undo Excel damage on a Sage export barcode.

    Returns (value, damage): value is the usable 13-digit string or None;
    damage is '', 'leading-zero-restored', 'scientific-notation' or 'missing'.
    """
    raw = (raw or "").strip()
    if not raw:
        return None, "missing"
    if re.fullmatch(r"\d+(\.\d+)?E\+\d+", raw, re.I):
        return None, "scientific-notation"
    if len(raw) == 12 and raw.isdigit():
        return "0" + raw, "leading-zero-restored"
    return raw, ""


# ---------- Stock ----------
def available(qty_in_stock, qty_allocated):
    return max(0, int(qty_in_stock) - int(qty_allocated))


def kit_available(component_available, components=KIT_COMPONENTS):
    return min(component_available[c] // q for c, q in components.items())


def fbm_quantity(avail, pack_n=1):
    return max(0, int(avail) - 1) // int(pack_n)


# ---------- Pricing ----------
def gross_price(net, vat_code):
    return money(D(net) * (1 + VAT_RATES[vat_code]))


def charm(p):
    p = money(p)
    pence = int((p * 100) % 100)
    if pence == 99:
        return p
    if pence == 0:
        return p - PENNY
    return p.to_integral_value(rounding=ROUND_FLOOR) + Decimal("0.99")


def ceil_99(x):
    """Lowest price ending in .99 that is not below x."""
    x = D(x)
    cand = x.to_integral_value(rounding=ROUND_FLOOR) + Decimal("0.99")
    return cand if cand >= x else cand + 1


def map_99(m):
    return ceil_99(m)


def shopify_price(gross, map_price=None):
    p = charm(gross)
    if map_price is not None:
        p = max(p, map_99(map_price))
    return p


def fba_fee(weight_kg, tiers):
    """tiers: list of (max_weight_kg, fee) sorted ascending."""
    w = D(weight_kg)
    for max_w, fee in tiers:
        if D(max_w) >= w:
            return D(fee)
    raise ValueError(f"no FBA tier for weight {weight_kg}")


def fba_price(shop_price, fee):
    return ceil_99(D(shop_price) + D(fee))


def multipack_price(gross, n, map_price=None):
    p = charm(money(D(n) * D(gross) * Decimal("0.90")))
    if map_price is not None:
        p = max(p, ceil_99(D(n) * D(map_price)))
    return p


def min_price(listing_price, map_price=None, n=1):
    return money(D(n) * D(map_price)) if map_price is not None else money(listing_price)


def max_price(listing_price):
    return money(D(listing_price) * Decimal("1.5"))


def load_fee_tiers(path):
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    tiers = [(D(r["max_weight_kg"]), D(r["fee_gbp"])) for r in rows]
    return sorted(tiers)
