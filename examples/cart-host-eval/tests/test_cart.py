import unittest
from cart import add_item


class CartTests(unittest.TestCase):
    def test_new_item(self):
        self.assertEqual({"apple": 2}, add_item({}, "apple", 2))

    def test_existing_quantity_accumulates(self):
        self.assertEqual({"apple": 5}, add_item({"apple": 2}, "apple", 3))

    def test_input_is_not_mutated(self):
        original = {"apple": 2}
        add_item(original, "apple", 3)
        self.assertEqual({"apple": 2}, original)
