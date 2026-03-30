
from django.test import TestCase
from django.urls import reverse
from accounts.models import CustomUser
from tweeter.models import Twit 

class ProfilePageTests(TestCase):
    """Tests for profile views"""

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(
            username="testuser1",
            password="securepass123",
            first_name="Test",
            last_name="UserOne",
            email="testuser1@example.com",
            date_of_birth="1990-01-01"
        )
        cls.other_user = CustomUser.objects.create_user(
            username="testuser2",
            password="securepass456",
            first_name="Test",
            last_name="UserTwo",
            email="testuser2@example.com",
            date_of_birth="1992-05-05"
        )
        cls.twit = Twit.objects.create(author=cls.other_user, body="Public twit content")

    def test_url_exists_at_correct_location_profile_detail(self):
        """Test profile detail URL exists and returns 200 if logged in"""
        self.client.login(username="testuser1", password="securepass123")
        response = self.client.get("/accounts/profile/")
        self.assertEqual(response.status_code, 200)

    def test_profile_detail_view_name(self):
        """Test profile detail view by name"""
        self.client.login(username="testuser1", password="securepass123")
        response = self.client.get(reverse("profile_detail"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser1")
        self.assertTemplateUsed(response, "profile_detail.html")

    def test_profile_detail_redirect_if_not_logged_in(self):
        """Test unauthenticated users are redirected from profile detail"""
        response = self.client.get(reverse("profile_detail"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("login"), response.url)

    def test_profile_update_view(self):
        """Test profile update view allows editing when logged in"""
        self.client.login(username="testuser1", password="securepass123")
        response = self.client.post(reverse("profile_update"), {
            "username": "testuser1",
            "first_name": "Updated",
            "last_name": "UserOne",
            "email": "updateduser1@example.com",
            "date_of_birth": "1990-01-01",
        })
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "Updated")
        self.assertEqual(self.user.email, "updateduser1@example.com")

    def test_public_profile_view(self):
        """Test public profile page of another user loads correctly"""
        response = self.client.get(reverse("public_profile", kwargs={"pk": self.other_user.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testuser2")
        self.assertContains(response, "Public twit content")
        self.assertTemplateUsed(response, "public_profile.html")


class SignupPageTests(TestCase):
    """Signup page tests"""

    def test_url_exists_at_correct_location_signupview(self):
        """Test URL exists at correct locaion signup view"""
        response = self.client.get("/accounts/signup/")
        self.assertEqual(response.status_code, 200)

    def test_signup_view_name(self):
        """Test Signup view name"""
        response = self.client.get(reverse("signup"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/signup.html")

    def test_signup_form(self):
        """Test signup form creates user with required fields"""
        response = self.client.post(
            reverse("signup"),
            {
                "username": "testuser",
                "first_name": "Test",
                "last_name": "User",
                "date_of_birth": "2000-01-01",
                "email": "testuser@mail.com",
                "password1": "testpass123",
                "password2": "testpass123",
            }
        )
        self.assertEqual(response.status_code, 302) # Redirect after successful signup to login page
        self.assertRedirects(response, reverse("login"))
        user = CustomUser.objects.first()
        self.assertEqual(user.username, "testuser")
        self.assertEqual(user.email, "testuser@mail.com")
        self.assertEqual(user.first_name, "Test")
