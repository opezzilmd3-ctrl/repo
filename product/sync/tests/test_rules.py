import os
import sys
import unittest
from decimal import Decimal as D

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
import rules as R  # noqa: E402

TIERS = [(D("0.15"), D("2.42")), (D("0.40"), D("2.89")), (D("0.90"), D("3.38")),
         (D("1.50"), D("4.27")), (D("3.00"), D("5.05")), (D("5.00"), D("6.12"))]


class CheckDigit(unittest.TestCase):
    def test_valid_codes(self):
        for code in ("5060213450011", "5060213450615", "0841234509064", "5060213450912"):
            self.assertTrue(R.is_valid_ean13(code), code)

    def test_wrong_check_digit(self):
        self.assertFalse(R.is_valid_ean13("5060213450616"))  # Sage NHG-1061, should end 5
        self.assertFalse(R.is_valid_ean13("5060213450913"))  # Shopify NHG-1091, should end 2
        self.assertEqual(R.ean13_check_digit("506021345061"), 5)
        self.assertEqual(R.ean13_check_digit("506021345091"), 2)

    def test_check_digit_zero_case(self):
        # sum mod 10 == 0 must give 0, not 10
        self.assertEqual(R.ean13_check_digit("000000000000"), 0)
        self.assertTrue(R.is_valid_ean13("0000000000000"))

    def test_wrong_length_or_chars(self):
        for bad in ("", "841234509064", "50602134500111", "5.06021E+12", "50602134500a1"):
            self.assertFalse(R.is_valid_ean13(bad), bad)

    def test_excel_repair(self):
        self.assertEqual(R.repair_excel_barcode("841234509064"), ("0841234509064", "leading-zero-restored"))
        self.assertEqual(R.repair_excel_barcode("5.06021E+12"), (None, "scientific-notation"))
        self.assertEqual(R.repair_excel_barcode(""), (None, "missing"))
        self.assertEqual(R.repair_excel_barcode("5060213450011"), ("5060213450011", ""))


class Rounding(unittest.TestCase):
    def test_gross_half_penny_up(self):
        self.assertEqual(R.gross_price("18.33", "T1"), D("22.00"))   # 21.996
        self.assertEqual(R.gross_price("4.58", "T1"), D("5.50"))     # 5.496
        self.assertEqual(R.gross_price("1.65", "T0"), D("1.65"))
        self.assertEqual(R.gross_price("10.10", "T5"), D("10.61"))   # 10.605 -> half up
        self.assertEqual(R.money("0.125"), D("0.13"))

    def test_charm_x00(self):
        self.assertEqual(R.charm(D("20.00")), D("19.99"))
        self.assertEqual(R.charm(D("9.00")), D("8.99"))

    def test_charm_x99(self):
        self.assertEqual(R.charm(D("14.99")), D("14.99"))
        self.assertEqual(R.charm(D("1.99")), D("1.99"))

    def test_charm_other(self):
        self.assertEqual(R.charm(D("13.50")), D("13.99"))
        self.assertEqual(R.charm(D("5.01")), D("5.99"))
        self.assertEqual(R.charm(D("7.98")), D("7.99"))

    def test_charm_x995_rounds_first(self):
        # 12.995 rounds (half up) to 13.00 first, so charm gives 12.99, not 12.99 via .995
        self.assertEqual(R.charm(D("12.995")), D("12.99"))
        # 12.994 rounds to 12.99 and is kept
        self.assertEqual(R.charm(D("12.994")), D("12.99"))
        # gross 10.83 * 1.2 = 12.996 -> 13.00 -> 12.99
        self.assertEqual(R.charm(R.gross_price("10.83", "T1")), D("12.99"))
        # 23.995 -> 24.00 -> 23.99
        self.assertEqual(R.charm(D("23.995")), D("23.99"))

    def test_map_99(self):
        self.assertEqual(R.map_99(D("20.00")), D("20.99"))
        self.assertEqual(R.map_99(D("9.49")), D("9.99"))
        self.assertEqual(R.map_99(D("8.99")), D("8.99"))
        self.assertEqual(R.ceil_99(D("28.47")), D("28.99"))
        self.assertEqual(R.ceil_99(D("9.95")), D("9.99"))

    def test_shopify_price_map_floor(self):
        self.assertEqual(R.shopify_price(D("7.50"), D("9.49")), D("9.99"))   # MAP raises
        self.assertEqual(R.shopify_price(D("22.00"), D("24.99")), D("24.99"))
        self.assertEqual(R.shopify_price(D("39.00"), D("34.99")), D("38.99"))  # MAP below
        self.assertEqual(R.shopify_price(D("23.00"), None), D("22.99"))       # kit, no MAP

    def test_min_max(self):
        self.assertEqual(R.max_price(D("13.99")), D("20.99"))   # 20.985 half up
        self.assertEqual(R.max_price(D("8.99")), D("13.49"))    # 13.485
        self.assertEqual(R.min_price(D("22.99"), None), D("22.99"))
        self.assertEqual(R.min_price(D("28.99"), D("9.49"), 3), D("28.47"))


class ChannelPricing(unittest.TestCase):
    def test_multipack_map_wins(self):
        # trowel x3: 3*7.50*0.9 = 20.25 -> 20.99 ; 3*9.49 = 28.47 -> 28.99
        self.assertEqual(R.multipack_price(D("7.50"), 3, D("9.49")), D("28.99"))

    def test_multipack_rounds_before_charm(self):
        # seeds x5: 5*1.65*0.9 = 7.425 -> 7.43 -> 7.99 ; 5*1.99=9.95 -> 9.99
        self.assertEqual(R.multipack_price(D("1.65"), 5, D("1.99")), D("9.99"))
        # without MAP the discount price stands
        self.assertEqual(R.multipack_price(D("1.65"), 5, None), D("7.99"))
        # discount price wins when above the MAP floor
        self.assertEqual(R.multipack_price(D("20.00"), 2, D("10.00")), D("35.99"))  # 36.00 -> 35.99 vs 20.99

    def test_fba_fee_tiers_boundaries(self):
        self.assertEqual(R.fba_fee(D("0.45"), TIERS), D("3.38"))
        self.assertEqual(R.fba_fee(D("0.90"), TIERS), D("3.38"))   # equal to max -> same tier
        self.assertEqual(R.fba_fee(D("0.91"), TIERS), D("4.27"))
        self.assertEqual(R.fba_fee(D("1.1"), TIERS), D("4.27"))
        self.assertEqual(R.fba_fee(D("0.02"), TIERS), D("2.42"))
        with self.assertRaises(ValueError):
            R.fba_fee(D("6"), TIERS)

    def test_fba_price(self):
        self.assertEqual(R.fba_price(D("9.99"), D("3.38")), D("13.99"))    # 13.37
        self.assertEqual(R.fba_price(D("38.99"), D("4.27")), D("43.99"))   # 43.26
        self.assertEqual(R.fba_price(D("16.62"), D("3.38")), D("20.99"))   # 20.00 -> 20.99 (not 19.99)
        self.assertEqual(R.fba_price(D("10.61"), D("3.38")), D("13.99"))   # exactly 13.99


class Stock(unittest.TestCase):
    def test_available_never_negative(self):
        self.assertEqual(R.available(40, 5), 35)
        self.assertEqual(R.available(-4, 0), 0)
        self.assertEqual(R.available(20, 22), 0)

    def test_kit(self):
        comp = {"NHG-1001": 35, "NHG-1011": 55, "NHG-1020": 200, "NHG-1021": 176, "NHG-1022": 5}
        self.assertEqual(R.kit_available(comp), 5)
        comp["NHG-1022"] = 0
        self.assertEqual(R.kit_available(comp), 0)
        self.assertEqual(R.kit_available({"A": 7, "B": 9}, {"A": 2, "B": 3}), 3)

    def test_fbm_quantity(self):
        self.assertEqual(R.fbm_quantity(35), 34)
        self.assertEqual(R.fbm_quantity(0), 0)
        self.assertEqual(R.fbm_quantity(1), 0)
        self.assertEqual(R.fbm_quantity(55, 3), 18)
        self.assertEqual(R.fbm_quantity(200, 5), 39)
        self.assertEqual(R.fbm_quantity(3, 3), 0)


class Skus(unittest.TestCase):
    def test_normalise(self):
        for s in ("nhg1011", "NHG1011 ", "nhg-1011", " NHG-1011", "NHG 1011"):
            self.assertEqual(R.normalise_sku(s), "NHG-1011", s)
        self.assertEqual(R.normalise_sku("2J-W8KQ-7ZPA"), "2J-W8KQ-7ZPA")

    def test_split(self):
        self.assertEqual(R.split_amazon_sku("NHG-1040-FBA"), ("NHG-1040", "FBA", 1))
        self.assertEqual(R.split_amazon_sku("NHG-1011-X3"), ("NHG-1011", "PACK", 3))
        self.assertEqual(R.split_amazon_sku("2J-W8KQ-7ZPA"), ("2J-W8KQ-7ZPA", "FBM", 1))


if __name__ == "__main__":
    unittest.main()
