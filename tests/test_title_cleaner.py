import tempfile
import unittest
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

from core.title_cleaner import clean_product_title
from core.title_workbook import process_title_cleaner


class TitleCleanerTextTests(unittest.TestCase):
    def test_pack_counts_and_features_leave_name_flavor_and_size(self):
        title = "Mrs. Meyer's Multi-Surface Cleaner, Peppermint, 16 OZ (Pack of 6), Vegan"
        self.assertEqual(
            "Mrs. Meyer's Multi-Surface Cleaner, Peppermint, 16 oz",
            clean_product_title(title, "Mrs. MEYER'S"),
        )

    def test_brand_is_preserved_and_tea_bag_label_is_removed(self):
        self.assertEqual(
            "Organic India, Chamomile, 12 fl oz",
            clean_product_title("Organic India, Organic Chamomile Tea Bags, 32 Tea Bags, 12 FZ", "ORGANIC INDIA"),
        )

    def test_brand_is_not_added_when_absent_from_title(self):
        self.assertEqual("Vanilla Syrup, 12 fl oz", clean_product_title("Sugar Free Vanilla Syrup 12 fl oz (6-pack)", "Acme"))

    def test_flavor_after_long_description_survives(self):
        title = "JONESBAR Organic Plant Based Protein Bars | Fruit & Nut Bar, Kosher, Gluten Free, Breakfast Bars, School Snacks, Vegan Snack & Healthy Snacks for Adults and Kids (1 Bar) (1 Count (Pack of 1), Dark Chocolate Almond)"
        self.assertEqual("JONESBAR Protein Bars, Fruit & Nut Bar, Dark Chocolate Almond", clean_product_title(title, "JONESBAR"))

    def test_parenthesized_pack_count_and_leading_claim(self):
        self.assertEqual(
            "Stirrings Pure Cane Simple Syrup Cocktail Mixer, 12 oz bottle",
            clean_product_title("Stirrings Pure Cane Simple Syrup Cocktail Mixer, 12 ounce bottle | Pack of (1) |", "Stirrings"),
        )
        self.assertEqual("Ground Tumeric Root", clean_product_title("Organic Fair Trade Ground Tumeric Root", "Frontier Herb"))

    def test_blank_title_stays_blank(self):
        self.assertEqual("", clean_product_title("", "Acme"))

    def test_no_identity_and_short_brand_value_do_not_keep_pack_counts(self):
        self.assertEqual("", clean_product_title("(Pack of 6)", "Nature's Earthly Choice"))
        self.assertEqual(
            "San Ignacio Dulce de Leche, 400 g",
            clean_product_title("San Ignacio Dulce de Leche 400 g (4 Pack)", "P"),
        )

    def test_employee_feedback_packaging_and_measurement_cases(self):
        cases = [
            ("One With Nature Dead Sea Lemon Verbena Bar Soap, 7 Ounce - 2 per case.", "One With Nature", "One With Nature Dead Sea Lemon Verbena Bar Soap, 7 oz"),
            ("Green Mountain Fire Roasted Garlic Salsa (12x16 OZ) (Value Bulk Multi-pack)60", "", "Green Mountain Fire Roasted Garlic Salsa, 16 oz"),
            ("Arrowhead Mills Pearled Barley 28-Ounce (Pack of 24)24", "Arrowhead Mills", "Arrowhead Mills Pearled Barley, 28 oz"),
            ("Kitchens of India Pindi Chana – Chick Peas Curry, (Pack of 6)10 Ounces", "Kitchens of India", "Kitchens of India Pindi Chana, Chick Peas Curry, 10 oz"),
            ("Drizzilicious S'Mores Crisp With Chocolate 10 Individual, .74 Oz. Pk Of 6.", "Drizzilicious", "Drizzilicious S'Mores Crisp With Chocolate, 0.74 oz"),
            ("Stash Double Bergamot Earl Grey Black Tea, Tea bags, 18 ct", "Stash", "Stash Double Bergamot Earl Grey Black Tea"),
        ]
        for title, brand, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(expected, clean_product_title(title, brand))

    def test_employee_feedback_preserves_distinctive_variants(self):
        cases = [
            ("Algae Cooking Club Shiitake Mushroom Oil – Savory Umami Depth with Red Miso, Black Garlic & Urfa Chili – Seed-Free Oil", "Algae Cooking Club", "Algae Cooking Club Shiitake Mushroom Oil, Red Miso, Black Garlic & Urfa Chili"),
            ("Wellness Complete Health Pate Adult Canned Wet Cat Food, Natural, Protein Rich, Grain Free, Beef and Chicken Dinner Recipe, 5.5 oz, Pack of 24 Cans", "Wellness", "Wellness Complete Health Pate Adult Canned Wet Cat Food, Beef and Chicken Dinner Recipe, 5.5 oz"),
            ("Miraculous Mushrooms Instant Cacao+5 Coffee Alternative by Teeccino – Reishi, Lion’s Mane, Chaga, Turkey Tail, Cordyceps – Caffeine Free, Prebiotic – 4.7 ounces", "Teeccino", "Teeccino Miraculous Mushrooms Cacao+5, Reishi, Lion’s Mane, Chaga, Turkey Tail, Cordyceps, 4.7 oz"),
        ]
        for title, brand, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(expected, clean_product_title(title, brand))

    def test_crystal_deodorants_keep_only_identity_scent_and_size(self):
        prefix = (
            "Crystal Magnesium Solid Stick Natural Deodorant, "
            "Non-Irritating Aluminum Free Deodorant for Men or Women, "
            "Safely and Effectively Fights Odor, "
        )
        variants = [
            ("Charcoal & Tea Tree", True),
            ("Coconut + Vanilla", True),
            ("Cucumber + Mint", True),
            ("Sea Salt + Sage", True),
            ("Lavender + Rosemary", False),
        ]
        for scent, has_baking_soda_claim in variants:
            title = prefix + ("Baking Soda Free, " if has_baking_soda_claim else "") + scent + ", 2.5 oz"
            expected = f"Crystal Magnesium Solid Stick Natural Deodorant, {scent}, 2.5 oz"
            with self.subTest(scent=scent):
                self.assertEqual(expected, clean_product_title(title, "Crystal Essence"))

    def test_long_search_titles_drop_uses_and_sales_copy(self):
        cases = [
            (
                "Le Sauce & Co. 4 serving Savory Mushroom Gourmet Gravy (2-pack) - Real Food Ingredients, Steak Sauce, Chicken Sauce, Dressing, Meats Prepared Foods, Pre-made Fresh Condiment for Chicken or Fish, Shrimp, Garlic Butter, Mashed Potatoes, Pantry Staple, Gravy Mix, Pork Chops, Mushroom Seasoning",
                "Le Sauce & Co. Savory Mushroom Gourmet Gravy",
            ),
            (
                "Le Sauce & Co. 4 serving Beefy French Onion Gourmet Gravy - Steak Sauce, Chicken Sauce, Dressing, Meats Prepared Foods, Pre-made Sauce for Chicken or Fish, Steak, Shrimp, Garlic Butter Taste & Lemon Caper Peppercorn cream Sauce",
                "Le Sauce & Co. Beefy French Onion Gourmet Gravy",
            ),
            (
                "Mantova Sundried Tomatoes Bruschetta Topping 6 Oz. (Pack of 4) Sun-dried tomatoes are a great Italian tradition as a means of preserving the bright taste of summer for the colder months ahead. Perfect topping for traditional bruschetta or over pizza, pasta or as a condiment.",
                "Mantova Sundried Tomatoes Bruschetta Topping, 6 oz",
            ),
            (
                "Sillycow Farms Hot Chocolate Sea Salt & Caramel Mix | Rich Hot Cocoa Delight | Gluten-Free, Non-GMO, Dairy-Free | Indulgence with Pure Sweet Caramel Flavor | 16.9 Oz Reusable Glass Bottle - Pack of 2",
                "Sillycow Farms Hot Chocolate Sea Salt & Caramel Mix, 16.9 oz",
            ),
        ]
        for title, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(expected, clean_product_title(title))
                self.assertLessEqual(len(clean_product_title(title)), 100)

    def test_mojibake_separator_keeps_short_product_variant(self):
        title = (
            "Tiger Balm Pain Relieving Ointment, Sports Ultra, 50g \u00e2\u20ac\u201c Professional Size "
            "\u00e2\u20ac\u201c Sports Rub Ultra Strength \u00e2\u20ac\u201c Knee Inflammation Relief "
            "\u00e2\u20ac\u201c Relief for Hand Arthritis \u00e2\u20ac\u201c Tiger Balm Ultra"
        )
        self.assertEqual("Tiger Balm Pain Relieving Ointment, Sports Ultra, 50 g", clean_product_title(title))

    def test_formula_ingredients_survive_shortening_and_nutrition_claims_do_not(self):
        title = (
            "Miraculous Mushrooms Instant Adapt & Protect Herbal Latte By Teeccino – 16 servings - "
            "Creamy Oat & Coconut Latte with Microground Herbs plus Reishi, Lion’s Mane, Chaga, Turkey Tail, "
            "Cordyceps - Caffeine Free, Prebiotic – 7.9 ounces"
        )
        self.assertEqual(
            "Teeccino Miraculous Mushrooms Latte, Reishi, Lion’s Mane, Chaga, Turkey Tail, Cordyceps, 7.9 oz",
            clean_product_title(title, "Teeccino"),
        )
        self.assertEqual(
            "Manitoba Harvest Hemp Yeah Protein Powder, Vanilla, 16 oz, Hemp and Pea",
            clean_product_title(
                "Manitoba Harvest Hemp Yeah Organic Plant-Based Protein Powder, Vanilla, 16oz, "
                "20g Complete Plant Protein (Hemp and Pea), 4g of Fiber & 1.9g Omegas 3&6 Per Serving, "
                "Non-GMO, Vegan, Packaging May Vary",
                "Manitoba Harvest",
            ),
        )
        self.assertEqual(
            "Four Sigmatic Dark Roast Whole Bean Coffee, Lion's Mane, Chaga, 12 oz",
            clean_product_title(
                "Four Sigmatic Dark Roast Organic Whole Bean Coffee | Gourmet Nootropic Mushroom Coffee Beans "
                "with Lion's Mane & Chaga Mushrooms for Enhanced Brain Function and Immune Support | 12oz",
                "Four Sigmatic",
            ),
        )

    def test_free_claims_are_removed_without_erasing_brand_or_product(self):
        cases = [
            ("Caboo Tree Free Baby Wipes, 72 Wipes Per, 216 Total", "Caboo", "Caboo Baby Wipes"),
            ("Sky Organics Petroleum-Free Jelly, 2.5 oz", "Sky Organics", "Sky Organics Jelly, 2.5 oz"),
            ("The Honest Company Shampoo & Body Wash, Tear-Free, Lavender Calm, 10 fl oz", "The Honest Company", "The Honest Company Shampoo & Body Wash, Lavender Calm, 10 fl oz"),
            ("Serenity Kids Free Range Pork Roast with Bone Broth, 3.5 oz", "Serenity Kids", "Serenity Kids Pork Roast with Bone Broth, 3.5 oz"),
            ("Free AF Whiskey Ginger Cocktail, 8.4 oz Can", "Free AF", "Free AF Whiskey Ginger Cocktail, 8.4 oz Can"),
            ("Mom's Place Gluten-Free Cinnamon Swirl Bun Mix, 15.2 oz", "Mom's Place Gluten-Free", "Mom's Place Gluten-Free Cinnamon Swirl Bun Mix, 15.2 oz"),
        ]
        for title, brand, expected in cases:
            with self.subTest(title=title):
                self.assertEqual(expected, clean_product_title(title, brand))


class TitleCleanerWorkbookTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1])
        self.root = Path(self.temp_dir.name)

    def tearDown(self):
        self.temp_dir.cleanup()

    def _make_source(self):
        path = self.root / "products.xlsx"
        workbook = Workbook()
        sheet = workbook.active
        sheet.title = "Products"
        sheet.freeze_panes = "A2"
        sheet.column_dimensions["F"].width = 42
        sheet.append(["ASIN", "Favorite", "Product ID", "Brand", "Brand Restriction", "Title", "Package Quantity", "Amazon Link"])
        sheet["F1"].font = Font(bold=True, color="FF0000")
        sheet.append(["B123", None, "0001", "Acme", "False", "Acme Lemon Drink 12 fl oz (Pack of 6)", 6, '=HYPERLINK("https://example.com", "example")'])
        sheet.append(["B124", None, "0002", "Acme", "False", None, 1, None])
        workbook.save(path)
        workbook.close()
        return path

    def test_new_column_preserves_other_cells_formulas_and_layout(self):
        source = self._make_source()
        progress_messages = []
        result = process_title_cleaner(str(source), str(self.root), clean_product_title, progress_messages.append)
        self.assertEqual(2, result["rows"])
        self.assertEqual({"rows": 2, "changed": 1, "blank": 1, "no_identity": 0}, result["stats"])
        self.assertIn("Sütunlar doğrulandı: Title F, New Title G, Brand D.", progress_messages)
        self.assertTrue(any("Excel dosyası kaydediliyor" in message for message in progress_messages))
        self.assertNotEqual(source, Path(result["file_path"]))

        output = load_workbook(result["file_path"])
        try:
            sheet = output.active
            self.assertEqual("New Title", sheet["G1"].value)
            self.assertEqual("Acme Lemon Drink, 12 fl oz", sheet["G2"].value)
            self.assertEqual(6, sheet["H2"].value)
            self.assertEqual('=HYPERLINK("https://example.com", "example")', sheet["I2"].value)
            self.assertIsNone(sheet["G3"].value)
            self.assertEqual("A2", sheet.freeze_panes)
            self.assertEqual(42, sheet.column_dimensions["G"].width)
            self.assertTrue(sheet["G1"].font.bold)
            self.assertEqual(sheet["F1"].font.color.rgb, sheet["G1"].font.color.rgb)
        finally:
            output.close()

        original = load_workbook(source, read_only=True)
        try:
            self.assertEqual("Package Quantity", original.active["G1"].value)
        finally:
            original.close()

    def test_existing_new_title_is_updated_without_shifting_columns(self):
        source = self.root / "existing.xlsx"
        workbook = Workbook()
        workbook.active.append(["Title", "New Title", "Note"])
        workbook.active.append(["Acme Lemon Drink 12 fl oz (Pack of 6)", "Old result", "Remove pack"])
        workbook.save(source)
        workbook.close()
        result = process_title_cleaner(str(source), str(self.root), clean_product_title)
        output = load_workbook(result["file_path"], read_only=True)
        try:
            self.assertEqual("Acme Lemon Drink, 12 fl oz", output.active["B2"].value)
            self.assertEqual("Remove pack", output.active["C2"].value)
            self.assertEqual(3, output.active.max_column)
        finally:
            output.close()

    def test_new_title_must_be_adjacent(self):
        source = self.root / "misplaced.xlsx"
        workbook = Workbook()
        workbook.active.append(["Title", "Note", "New Title"])
        workbook.save(source)
        workbook.close()
        with self.assertRaisesRegex(ValueError, "hemen yanında"):
            process_title_cleaner(str(source), str(self.root), clean_product_title)

    def test_override_updates_source_without_requiring_destination(self):
        source = self._make_source()
        result = process_title_cleaner(str(source), None, clean_product_title, override_original=True)
        self.assertEqual(source, Path(result["file_path"]))
        self.assertEqual([source], list(self.root.glob("*.xlsx")))
        output = load_workbook(source, read_only=True)
        try:
            self.assertEqual("Acme Lemon Drink, 12 fl oz", output.active["G2"].value)
        finally:
            output.close()

    def test_cancellation_removes_partial_workbook(self):
        source = self.root / "many_products.xlsx"
        workbook = Workbook()
        workbook.active.append(["Title"])
        for _ in range(2001):
            workbook.active.append(["Acme Tea 12 oz (Pack of 2)"])
        workbook.save(source)
        workbook.close()

        def cancel_after_2000(message):
            if "2,000" in message:
                raise InterruptedError("Cancelled")

        with self.assertRaises(InterruptedError):
            process_title_cleaner(str(source), str(self.root), clean_product_title, cancel_after_2000)
        self.assertEqual([source], list(self.root.glob("*.xlsx")))

        original_bytes = source.read_bytes()
        with self.assertRaises(InterruptedError):
            process_title_cleaner(str(source), None, clean_product_title, cancel_after_2000, override_original=True)
        self.assertEqual(original_bytes, source.read_bytes())
        self.assertEqual([source], list(self.root.glob("*.xlsx")))

    def test_cell_reference_formulas_are_rejected(self):
        source = self.root / "formulas.xlsx"
        workbook = Workbook()
        workbook.active.append(["Title", "Value", "Calculated"])
        workbook.active.append(["Acme Tea", 5, "=B2*2"])
        workbook.save(source)
        workbook.close()
        with self.assertRaisesRegex(ValueError, "Hücre başvurulu formüller"):
            process_title_cleaner(str(source), str(self.root), clean_product_title)


if __name__ == "__main__":
    unittest.main()
