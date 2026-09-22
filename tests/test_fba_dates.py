import unittest
from datetime import datetime

from core.fba_inventory import UniversalDateParser


class UniversalDateParserTests(unittest.TestCase):
    def assert_expiration(self, raw, expected, number_format=None):
        usa, tur, _ = UniversalDateParser.parse_exp_date(raw, number_format)
        self.assertEqual(expected, usa)
        month, day, year = expected.split("-")
        self.assertEqual(f"{day}.{month}.{year}", tur)

    def test_american_numeric_separators_and_two_digit_years(self):
        cases = {
            "12-31-2025": "12-31-2025",
            "12.31.25": "12-31-2025",
            "1/2/27": "01-02-2027",
            "02 - 29 - 24": "02-29-2024",
            "09-24-2024\t": "09-24-2024",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assert_expiration(raw, expected)

    def test_iso_month_names_and_time_suffixes(self):
        cases = {
            "2026-04-09": "04-09-2026",
            "12 Dec 2025,": "12-12-2025",
            "Dec 5, 26": "12-05-2026",
            "04/09/2027 10:57:34": "04-09-2027",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assert_expiration(raw, expected)

    def test_native_excel_date_uses_day_first_display_to_recover_us_input(self):
        # Excel stored 04-01-2024 as 4 January under a local DD/MM locale.
        self.assert_expiration(datetime(2024, 1, 4), "04-01-2024", "dd/mm/yyyy")

    def test_unambiguous_native_excel_date_is_not_swapped_to_invalid_date(self):
        self.assert_expiration(datetime(2025, 8, 22), "08-22-2025", "dd/mm/yyyy")

    def test_native_excel_date_with_month_first_format_is_kept(self):
        self.assert_expiration(datetime(2024, 4, 1), "04-01-2024", "mm-dd-yy")

    def test_invalid_and_blank_values_remain_blank(self):
        for raw in (None, "", "not a date", "02-30-2025"):
            with self.subTest(raw=raw):
                self.assertEqual(("", "", 0), UniversalDateParser.parse_exp_date(raw))


if __name__ == "__main__":
    unittest.main()
