import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory.manager import Inventory, InventoryError
from inventory.models import Product
from inventory import validators as v


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.path = os.path.join(self.dir.name, "inv.json")
        self.inv = Inventory(self.path)
        self.inv.add(Product("A1", "Widget", "Tools", 10, 2.5))

    def tearDown(self):
        self.dir.cleanup()

    def test_persistence(self):
        self.assertEqual(len(Inventory(self.path).products), 1)

    def test_duplicate_id(self):
        with self.assertRaises(InventoryError):
            self.inv.add(Product("A1", "Other", "Tools", 1, 1))

    def test_stock_out_too_much(self):
        with self.assertRaises(InventoryError):
            self.inv.stock_out("A1", 11)

    def test_stock_in_out(self):
        self.inv.stock_in("A1", 5)
        self.assertEqual(self.inv.stock_out("A1", 15).quantity, 0)

    def test_total_and_low_stock(self):
        self.assertEqual(self.inv.total_value(), 25.0)
        self.assertEqual(len(self.inv.low_stock(10)), 1)

    def test_delete_and_search(self):
        self.assertEqual(len(self.inv.search("widg")), 1)
        self.inv.delete("A1")
        self.assertEqual(self.inv.products, [])

    def test_validators(self):
        with self.assertRaises(ValueError):
            v.validate_quantity("-1")
        with self.assertRaises(ValueError):
            v.validate_quantity("abc")
        with self.assertRaises(ValueError):
            v.validate_price("-3")
        self.assertEqual(v.validate_product_id(" p1 "), "P1")


if __name__ == "__main__":
    unittest.main()
