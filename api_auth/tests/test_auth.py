from rest_framework.test import APITestCase
from django.urls import reverse
from rest_framework import status

from api_auth.models import Organisation


class TestSetUp(APITestCase):
    def setUp(self):
        self.register_url = reverse("register")
        self.login_url = reverse("login")

        self.user_data = {
            "firstName": "Marjory",
            "lastName": "Purdy",
            "email": "Allen.Bogan67@gmail.com",
            "password": "qwertyuiop",
            "phone": "+2349079016973",
        }

        return super().setUp()

    def tearDown(self):
        return super().tearDown()


class TestAuthViews(TestSetUp):
    def test_successfull_registration_with_default_organisation(self):
        response = self.client.post(self.register_url, self.user_data, format="json")
        response_data = response.data["data"]["user"]
        organisation = Organisation.objects.first()
        self.assertEqual(
            organisation.name, f"{self.user_data["firstName"]}'s Organisation"
        )
        self.assertIn("accessToken", response.data["data"])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(self.user_data["firstName"], response_data["firstName"])
        self.assertEqual(self.user_data["lastName"], response_data["lastName"])
        self.assertEqual(self.user_data["email"], response_data["email"])
        self.assertEqual(self.user_data["phone"], response_data["phone"])

    def test_login_user_successfully(self):
        self.client.post(self.register_url, self.user_data, format="json")
        login_data = {
            "email": self.user_data["email"],
            "password": self.user_data["password"],
        }
        response = self.client.post(self.login_url, login_data, format="json")
        response_data = response.data["data"]["user"]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("accessToken", response.data["data"])
        self.assertEqual(self.user_data["firstName"], response_data["firstName"])
        self.assertEqual(self.user_data["lastName"], response_data["lastName"])
        self.assertEqual(self.user_data["email"], response_data["email"])
        self.assertEqual(self.user_data["phone"], response_data["phone"])

    def test_register_missing_required_fields(self):
        required_fields = ["firstName", "lastName", "email", "password"]
        for field in required_fields:
            data = self.user_data.copy()
            del data[field]
            response = self.client.post(self.register_url, data, format="json")
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertIn(field, response.data[0]["field"])
            self.assertEqual("This field is required.", response.data[0]["message"])

    def test_register_duplicate_email(self):
        self.client.post(self.register_url, self.user_data, format="json")
        response = self.client.post(self.register_url, self.user_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertIn("email", response.data[0]["field"])
        self.assertEqual(
            "user with this email already exists.", response.data[0]["message"]
        )
