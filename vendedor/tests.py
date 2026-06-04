from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase


class VendedorReportTests(TestCase):
    def test_most_sold_report_includes_product_and_quantity(self):
        session = self.client.session
        session["user_email"] = "vendedor@example.com"
        session.save()

        profile_response = SimpleNamespace(data=[{
            "id": 1,
            "email": "vendedor@example.com",
            "role": "vendedor",
        }])
        products = [{
            "product_id": 10,
            "name": "Pincel fino",
            "quantity": 5,
        }]

        with patch("vendedor.views.get_profile_by_email", return_value=profile_response):
            with patch("vendedor.views.get_top_selling_products", return_value=products):
                response = self.client.get("/vendedor/reportes/mas-vendidos/")

        content = response.content.decode("utf-8")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "text/plain; charset=utf-8")
        self.assertIn("CANTIDAD", content)
        self.assertIn("Pincel fino", content)
        self.assertNotIn("FACTURADO", content)
