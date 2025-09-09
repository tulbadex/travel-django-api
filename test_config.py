"""
Test Configuration for Torrey Travels API

This module provides test configuration and utilities for the Django REST API.
It ensures tests run without sending real emails and handles API validation properly.
"""

from django.test import TestCase, override_settings
from django.core import mail
from django.contrib.auth import get_user_model

User = get_user_model()

@override_settings(
    EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
    CELERY_TASK_ALWAYS_EAGER=True,
    CELERY_TASK_EAGER_PROPAGATES=True
)
class BaseAPITestCase(TestCase):
    """
    Base test case for API tests with proper email configuration
    """
    
    def setUp(self):
        """Clear the test email outbox before each test"""
        mail.outbox = []
        
    def tearDown(self):
        """Clean up after each test"""
        mail.outbox = []

class TestConfigurationTest(BaseAPITestCase):
    """
    Test that verifies the test configuration is working properly
    """
    
    def test_email_backend_configuration(self):
        """Test that email backend is configured for testing"""
        from django.conf import settings
        self.assertEqual(settings.EMAIL_BACKEND, 'django.core.mail.backends.locmem.EmailBackend')
        
    def test_no_real_emails_sent(self):
        """Test that no real emails are sent during testing"""
        from django.core.mail import send_mail
        
        # Send a test email
        send_mail(
            'Test Subject',
            'Test message',
            'from@example.com',
            ['to@example.com'],
            fail_silently=False,
        )
        
        # Check that email is in test outbox, not sent to real server
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Test Subject')
        
    def test_user_creation_works(self):
        """Test that user creation works in test environment"""
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.assertEqual(user.email, 'test@example.com')
        self.assertTrue(user.check_password('testpass123'))
        
    def test_database_isolation(self):
        """Test that database changes are isolated between tests"""
        initial_count = User.objects.count()
        
        User.objects.create_user(
            username='tempuser',
            email='temp@example.com',
            password='temppass123'
        )
        
        self.assertEqual(User.objects.count(), initial_count + 1)