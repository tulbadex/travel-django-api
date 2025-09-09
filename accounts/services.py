from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

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
        print(f"\n=== EMAIL DEBUG: Registration Email ===")
        print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
        print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'NOT SET')}")
        print(f"User email: {user.email}")
        
        try:
            if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
                print(f"Email not configured, skipping registration email for {user.email}")
                return True
            
            base_url = EmailService.get_base_url(request)
            print(f"Base URL: {base_url}")
            
            context = {
                'user': user,
                'base_url': base_url,
                'site_name': 'Torrey Travels'
            }
            
            html_message = render_to_string('emails/registration_welcome.html', context)
            plain_message = strip_tags(html_message)
            
            print(f"Sending email from: {settings.DEFAULT_FROM_EMAIL}")
            print(f"Sending email to: {user.email}")
            
            send_mail(
                subject='Welcome to Torrey Travels!',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            print(f"✅ Registration email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send registration email to {user.email}: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False
    
    @staticmethod
    def send_password_reset_email(user, reset_token, request=None):
        """Send password reset email"""
        print(f"\n=== EMAIL DEBUG: Password Reset Email ===")
        print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'NOT SET')}")
        print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'NOT SET')}")
        print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'NOT SET')}")
        print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'NOT SET')}")
        print(f"EMAIL_BACKEND: {getattr(settings, 'EMAIL_BACKEND', 'NOT SET')}")
        print(f"User email: {user.email}")
        print(f"Reset token: {reset_token}")
        
        try:
            if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
                print(f"Email not configured, skipping password reset email for {user.email}")
                return True
            
            # Debug URL resolution
            if request:
                referrer = request.META.get('HTTP_REFERER')
                origin = request.META.get('HTTP_ORIGIN')
                host = request.get_host()
                print(f"Request referrer: {referrer}")
                print(f"Request origin: {origin}")
                print(f"Request host: {host}")
            
            base_url = EmailService.get_base_url(request)
            reset_url = f"{base_url}/reset-password?token={reset_token}"
            print(f"Resolved base URL: {base_url}")
            print(f"Reset URL: {reset_url}")
            
            context = {
                'user': user,
                'reset_url': reset_url,
                'base_url': base_url,
                'site_name': 'Torrey Travels'
            }
            
            html_message = render_to_string('emails/password_reset.html', context)
            plain_message = strip_tags(html_message)
            
            print(f"Sending email from: {settings.DEFAULT_FROM_EMAIL}")
            print(f"Sending email to: {user.email}")
            print(f"Subject: Reset Your Password - Torrey Travels")
            
            send_mail(
                subject='Reset Your Password - Torrey Travels',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            print(f"✅ Password reset email sent successfully to {user.email}")
            return True
            
        except Exception as e:
            print(f"❌ Failed to send password reset email to {user.email}: {str(e)}")
            print(f"Exception type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            return False