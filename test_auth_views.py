from types import SimpleNamespace
from unittest.mock import patch

from django.test import TestCase


class AuthViewsTests(TestCase):
    def test_register_rejects_invalid_email(self):
        with patch("metodologia.views.create_confirmed_user") as create_user_mock:
            response = self.client.post("/register/", data={
                "first_name": "Carlos",
                "last_name": "Perez",
                "email": "correo-invalido",
                "password": "Test1234!",
                "tel": "1234567890",
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Por favor ingresa un email valido")
        create_user_mock.assert_not_called()

    def test_register_accepts_valid_email(self):
        user = SimpleNamespace(email="carlos@example.com")
        session = SimpleNamespace(access_token="token")

        with patch("metodologia.views.create_confirmed_user", return_value=SimpleNamespace(user=user)):
            with patch("metodologia.views.create_profile") as create_profile_mock:
                with patch(
                    "metodologia.views.login_user",
                    return_value=SimpleNamespace(user=user, session=session),
                ):
                    response = self.client.post("/register/", data={
                        "first_name": "Carlos",
                        "last_name": "Perez",
                        "email": "carlos@example.com",
                        "password": "Test1234!",
                        "tel": "1234567890",
                    })

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/")
        create_profile_mock.assert_called_once()

    def test_login_rejects_invalid_email(self):
        with patch("metodologia.views.login_user") as login_mock:
            response = self.client.post("/login/", data={
                "email": "correo-invalido",
                "password": "Test1234!",
            })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Por favor ingresa un email valido")
        login_mock.assert_not_called()
