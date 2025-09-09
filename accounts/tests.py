from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.utils import timezone
from datetime import timedelta
from .models import PasswordResetToken

User = get_user_model()

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        self.assertFalse(user.is_staff)
        self.assertFalse(user.is_superuser)

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            email='admin@example.com',
            password='adminpass123'
        )
        self.assertEqual(user.email, 'admin@example.com')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

class AuthenticationAPITest(APITestCase):
    def setUp(self):
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }

    def test_user_registration(self):
        response = self.client.post(self.register_url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
        self.assertEqual(response.data['user']['email'], 'test@example.com')

    def test_user_login(self):
        User.objects.create_user(**self.user_data)
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)

    def test_invalid_login(self):
        login_data = {
            'email': 'wrong@example.com',
            'password': 'wrongpass'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_user_logout(self):
        user = User.objects.create_user(**self.user_data)
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class PasswordResetTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        self.reset_request_url = reverse('password_reset_request')
        self.reset_confirm_url = reverse('password_reset_confirm')

    def test_password_reset_request(self):
        data = {'email': 'test@example.com'}
        response = self.client.post(self.reset_request_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(PasswordResetToken.objects.filter(user=self.user).exists())

    def test_password_reset_confirm(self):
        # Create reset token
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='test-token-123',
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        data = {
            'token': 'test-token-123',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(self.reset_confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify password changed
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('newpass123'))

    def test_expired_token(self):
        # Create expired token
        token = PasswordResetToken.objects.create(
            user=self.user,
            token='expired-token',
            expires_at=timezone.now() - timedelta(hours=1)
        )
        
        data = {
            'token': 'expired-token',
            'password': 'newpass123',
            'password_confirm': 'newpass123'
        }
        response = self.client.post(self.reset_confirm_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)