from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase

from pedidos.services import get_top_selling_products


class FakeSupabaseQuery:
    def __init__(self, rows):
        self.rows = rows
        self.statuses = None
        self.limit_value = None

    def table(self, table_name):
        self.table_name = table_name
        return self

    def select(self, fields):
        self.fields = fields
        return self

    def in_(self, field, values):
        self.statuses = set(values)
        return self

    def limit(self, limit):
        self.limit_value = limit
        return self

    def execute(self):
        rows = self.rows
        if self.statuses is not None:
            rows = [row for row in rows if row.get("status") in self.statuses]
        if self.limit_value is not None:
            rows = rows[:self.limit_value]
        return SimpleNamespace(data=rows)


class TopSellingProductsTests(TestCase):
    def test_groups_products_by_quantity(self):
        rows = [
            {
                "product_id": 1,
                "amount": 2,
                "status": "paid",
                "products": {"name": "Pincel fino"},
            },
            {
                "product_id": 1,
                "amount": 3,
                "status": "delivered",
                "products": {"name": "Pincel fino"},
            },
            {
                "product_id": 2,
                "amount": 4,
                "status": "paid",
                "products": {"name": "Acrilico"},
            },
            {
                "product_id": 3,
                "amount": 20,
                "status": "cancelled",
                "products": {"name": "Cancelado"},
            },
        ]

        with patch("pedidos.services.supabase", FakeSupabaseQuery(rows)):
            result = get_top_selling_products(10)

        self.assertEqual(result[0]["product_id"], 1)
        self.assertEqual(result[0]["quantity"], 5)
        self.assertEqual(result[1]["product_id"], 2)
        self.assertEqual(result[1]["quantity"], 4)
        self.assertEqual(len(result), 2)

    def test_limits_top_products(self):
        rows = [
            {
                "product_id": product_id,
                "amount": product_id,
                "status": "paid",
                "products": {"name": f"Producto {product_id}"},
            }
            for product_id in range(1, 13)
        ]

        with patch("pedidos.services.supabase", FakeSupabaseQuery(rows)):
            result = get_top_selling_products(10)

        self.assertEqual(len(result), 10)
        self.assertEqual(result[0]["product_id"], 12)
        self.assertEqual(result[-1]["product_id"], 3)
