from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging
import sys

logger = logging.getLogger(__name__)

class EmailService:
    """Service for handling email operations"""
    
    @staticmethod
    def get_base_url(request):
        """Extract base URL from request referrer, origin, or fallback to API host"""
        if request:
            # Check for referrer header (frontend URL)
            referrer = request.META.get('HTTP_REFERER')
            if referrer:
                from urllib.parse import urlparse
                parsed = urlparse(referrer)
                return f"{parsed.scheme}://{parsed.netloc}"
            
            # Check for origin header (CORS requests)
            origin = request.META.get('HTTP_ORIGIN')
            if origin:
                return origin
            
            # Fallback to request host (API URL)
            protocol = 'https' if request.is_secure() else 'http'
            host = request.get_host()
            return f"{protocol}://{host}"
        
        return "http://localhost:9888"  # Development fallback
    
    @staticmethod
    def send_registration_email(user, request=None):
        """Send welcome email after registration"""
        try:
            if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
                return True
            
            base_url = EmailService.get_base_url(request)
            
            context = {
                'user': user,
                'base_url': base_url,
                'site_name': 'Torrey Travels'
            }
            
            html_message = render_to_string('emails/registration_welcome.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Welcome to Torrey Travels!',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_token, request=None):
        """Send password reset email"""
        try:
            if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
                return True
            
            base_url = EmailService.get_base_url(request)
            reset_url = f"{base_url}/reset-password?token={reset_token}"
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'base_url': base_url,
                'site_name': 'Torrey Travels'
            }
            
            html_message = render_to_string('emails/password_reset.html', context)
            plain_message = strip_tags(html_message)
            
            send_mail(
                subject='Reset Your Password - Torrey Travels',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            return True
            
        except Exception as e:
            return False