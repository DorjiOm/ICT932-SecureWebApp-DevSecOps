"""
accounts/tests.py
=================
Unit tests for authentication and security features.

Security Note: Test passwords are stored in environment variables
in production. For development/testing purposes only.
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.cache import cache
from accounts.models import Profile
import os

# Security: Use environment variable for test password
# Falls back to test password if not set (development only)
TEST_PASSWORD = os.environ.get('TEST_USER_PASSWORD', 'TestPass@123')


class AuthenticationTests(TestCase):

    def setUp(self):
        """Set up test data and clear cache before each test"""
        self.client = Client()
        # Security: Clear cache before each test to reset login attempts
        cache.clear()
        self.user = User.objects.create_user(
            username='testuser',
            password=TEST_PASSWORD  # Using environment variable
        )

    def tearDown(self):
        """Clear cache after each test"""
        cache.clear()

    def test_register_page_loads(self):
        """Test registration page loads correctly"""
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_login_page_loads(self):
        """Test login page loads correctly"""
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_valid_login(self):
        """Test user can login with correct credentials"""
        cache.clear()
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': TEST_PASSWORD
        })
        self.assertEqual(response.status_code, 302)

    def test_invalid_login(self):
        """Test login fails with wrong password"""
        cache.clear()
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'attempts remaining')

    def test_profile_created_automatically(self):
        """Test Profile is automatically created for new user"""
        self.assertTrue(Profile.objects.filter(user=self.user).exists())

    def test_default_role_is_user(self):
        """Test new users get 'user' role by default"""
        self.assertEqual(self.user.profile.role, 'user')

    def test_admin_role(self):
        """Test admin role can be assigned"""
        self.user.profile.role = 'admin'
        self.user.profile.save()
        self.assertTrue(self.user.profile.is_admin())

    def test_task_list_requires_login(self):
        """Test task list redirects unauthenticated users"""
        response = self.client.get(reverse('task_list'))
        self.assertEqual(response.status_code, 302)

    def test_admin_dashboard_requires_login(self):
        """Test admin dashboard redirects unauthenticated users"""
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_brute_force_protection(self):
        """Test account locks after 5 failed attempts"""
        cache.clear()
        for i in range(5):
            self.client.post(reverse('login'), {
                'username': 'testuser',
                'password': 'wrongpassword'
            })
        # 6th attempt should show lockout message
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertContains(response, 'locked')