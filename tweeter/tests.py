
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Twit, Comment

# Get the custom user model
User = get_user_model()


class TwitTests(TestCase):
    """Tests for Twits and Comments"""

    @classmethod
    def setUpTestData(cls):
        """Set up test data for all tests"""
        cls.user = User.objects.create_user(username='user1', password='pass12345')
        cls.other_user = User.objects.create_user(username='user2', password='pass12345')
        cls.twit = Twit.objects.create(author=cls.user, body='Hello world!')

    def test_twit_model(self):
        """Test Twit model creation and string representation"""
        self.assertEqual(self.twit.body, 'Hello world!')
        self.assertEqual(self.twit.author.username, 'user1')
        self.assertEqual(str(self.twit), f"Twit by {self.user.username}")

    def test_comment_model(self):
        """Test Comment model creation"""
        comment = Comment.objects.create(
            twit=self.twit,
            author=self.user,
            body='Nice twit!',
        )
        self.assertEqual(comment.body, 'Nice twit!')
        self.assertEqual(comment.twit, self.twit)
        self.assertEqual(comment.author, self.user)

    def test_like_twit(self):
        """Test user can like a Twit"""
        self.twit.likes.add(self.user)
        self.assertIn(self.user, self.twit.likes.all())

    def test_unlike_twit(self):
        """Test user can unlike a Twit"""
        self.twit.likes.add(self.user)
        self.twit.likes.remove(self.user)
        self.assertNotIn(self.user, self.twit.likes.all())

    def test_twit_list_view(self):
        """Test Twit list view renders successfully and is in correct location"""
        self.client.login(username='user1', password='pass12345')
        response = self.client.get(reverse('twit_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.twit.body)

    def test_twit_detail_view(self):
        """Test Twit detail view renders successfully and is in correct location"""
        self.client.login(username='user1', password='pass12345')
        response = self.client.get(reverse('twit_detail', kwargs={'pk': self.twit.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.twit.body)

    def test_comment_post_view(self):
        """Test comment can be posted on a Twit"""
        self.client.login(username='user1', password='pass12345')
        response = self.client.post(
            reverse('twit_detail', kwargs={'pk': self.twit.pk}),
            {'body': 'Test comment'},
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test comment')
        self.assertEqual(Comment.objects.count(), 1)

    def test_update_permission_denied(self):
        """Test that a user cannot update another user's Twit"""
        self.client.login(username='user2', password='pass12345')
        response = self.client.get(reverse('twit_update', kwargs={'pk': self.twit.pk}))
        self.assertEqual(response.status_code, 403)

    def test_delete_permission_denied(self):
        """Test that a user cannot delete another user's Twit"""
        self.client.login(username='user2', password='pass12345')
        response = self.client.get(reverse('twit_delete', kwargs={'pk': self.twit.pk}))
        self.assertEqual(response.status_code, 403)
