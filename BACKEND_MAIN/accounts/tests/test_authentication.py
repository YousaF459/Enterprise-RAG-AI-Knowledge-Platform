from django.test import TestCase
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from django.urls import reverse


User = get_user_model()


class AuthenticationTests(TestCase):

    def setUp(self):

        self.client=APIClient()

        self.user=User.objects.create_user(email="john@gmail.com",password="john098@123",username="john1",first_name="john")


    def test_login_returns_jwt_token(self):

        url=reverse("token_obtain_pair")
        response=self.client.post(
            url,
            {
                "email":"john@gmail.com",
                "password":"john098@123",
            },
            format="json"
        )

        access = response.data["access"]
        refresh = response.data["refresh"]

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        self.assertEqual(response.status_code,200)
        self.assertIn("access",response.data)
        self.assertIn("refresh",response.data)

        

    def test_login_with_invalid_password(self):

        url=reverse("token_obtain_pair")
        response=self.client.post(
            url,
            {
                "email":"john@gmail.com",
                "password":"john09823",
            },
            format="json"
        )

        self.assertEqual(response.status_code,200)
        self.assertIn("access",response.data)
        self.assertIn("refresh",response.data)

    def test_login_with_invalid_email(self):
    
        url=reverse("token_obtain_pair")
        response=self.client.post(
            url,
            {
                "password":"john098@123",
            },
            format="json"
        )

        print(response.data)

        self.assertEqual(response.status_code,200)
        self.assertIn("access",response.data)
        self.assertIn("refresh",response.data)


    def test_token_refresh_view(self):

        # Step 1: Login to obtain tokens
        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "john@gmail.com",
                "password": "john098@123",
            },
            format="json",
        )

        # Step 2: Extract the refresh token
        refresh = login_response.data["refresh"]

        # Step 3: Call the refresh endpoint
        response = self.client.post(
            reverse("token_refresh_pair"),
            {
                "refresh": refresh,
            },
            format="json",
        )

        # Step 4: Verify the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)


    def test_logout(self):

        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "john@gmail.com",
                "password": "john098@123",
            },
            format="json",
        )

        # Step 2: Extract the refresh token
        refresh = login_response.data["refresh"]

        url=reverse("logout")

        response = self.client.post(
                    url,
                    {
                        "refresh": refresh,
                    },
                    format="json",
                )

        self.assertEqual(response.status_code,200)

        self.assertEqual(response.data["message"], "Logged out Successfully")


    def test_profile(self):

        url=reverse("profile")
        login_response = self.client.post(
            reverse("token_obtain_pair"),
            {
                "email": "john@gmail.com",
                "password": "john098@123",
            },
            format="json",
        )

        # Step 2: Extract the refresh token
        access = login_response.data["access"]
        self.client.credentials(
        HTTP_AUTHORIZATION=f"Bearer {access}"
        )

        response=self.client.get(
            url,
            format="json"

        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["email"], "john@gmail.com")