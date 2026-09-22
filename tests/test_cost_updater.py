import csv
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from core.cost_updater import process_costupdater


class CostUpdaterTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.input_path = self.root / "input.csv"
        with self.input_path.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(
                handle,
                fieldnames=[
                    "sku", "cost", "additional_cost", "business_pricing",
                    "bp_strategy", "qd_strategy", "pkg_volume", "pkg_weight",
                ],
            )
            writer.writeheader()
            writer.writerows([
                {
                    "sku": "MD_842515006722_6PK_21.88",
                    "pkg_volume": "464.973696",
                    "pkg_weight": "4.06",
                },
                {"sku": "UNKNOWN_SKU", "pkg_volume": "", "pkg_weight": ""},
            ])

        self.columns = {
            "cost": ["cost"],
            "sku": ["sku"],
            "additional cost": ["additional_cost"],
            "business pricing": ["business_pricing"],
            "bp strategy": ["bp_strategy"],
            "qd strategy": ["qd_strategy"],
            "pkg volume": ["pkg_volume"],
            "pkg weight": ["pkg_weight"],
        }

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_v2_writes_numeric_cost_into_source_string_column(self):
        output_dir = self.root / "v2"
        settings = {
            "columns": self.columns,
            "warehouses": {
                "MD": {
                    "v2_additional_cost": 0,
                    "v2_equation": 1,
                    "v2_warehouse_fee": 0.70,
                }
            },
        }

        process_costupdater(str(self.input_path), str(output_dir), settings, version=2)
        result = pd.read_csv(output_dir / self.input_path.name, dtype=str, keep_default_na=False)

        self.assertAlmostEqual(22.95, float(result.loc[0, "cost"]))
        self.assertEqual("#YOK", result.loc[1, "cost"])
        self.assertEqual("on", result.loc[0, "business_pricing"])

    def test_v1_writes_numeric_cost_and_additional_cost(self):
        output_dir = self.root / "v1"
        settings = {
            "columns": self.columns,
            "warehouses": {"MD": 0.75},
        }

        process_costupdater(str(self.input_path), str(output_dir), settings, version=1)
        result = pd.read_csv(output_dir / self.input_path.name, dtype=str, keep_default_na=False)

        self.assertAlmostEqual(21.88, float(result.loc[0, "cost"]))
        self.assertAlmostEqual(0.75, float(result.loc[0, "additional_cost"]))
        self.assertEqual("#YOK", result.loc[1, "cost"])
        self.assertEqual("#YOK", result.loc[1, "additional_cost"])


if __name__ == "__main__":
    unittest.main()
