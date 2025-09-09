from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta
import uuid
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import User, PasswordResetToken
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserProfileSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer
)
from .services import EmailService

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={201: UserProfileSerializer, 400: 'Validation errors'}
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        # Send welcome email
        EmailService.send_registration_email(user, request)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Registration successful'
        }, status=status.HTTP_201_CREATED)

@swagger_auto_schema(
    method='post',
    request_body=UserLoginSerializer,
    responses={200: UserProfileSerializer, 400: 'Invalid credentials'}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def login_view(request):
    serializer = UserLoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'user': UserProfileSerializer(user).data,
            'token': token.key,
            'message': 'Login successful'
        })
    
    return Response({
        'error': 'Invalid email or password. Please check your credentials and try again.'
    }, status=status.HTTP_400_BAD_REQUEST)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(type=openapi.TYPE_OBJECT, properties={}),
    responses={200: 'Logout successful'}
)
@api_view(['POST'])
def logout_view(request):
    try:
        request.user.auth_token.delete()
        return Response({'message': 'Logout successful'})
    except:
        return Response({'error': 'Error logging out'}, status=status.HTTP_400_BAD_REQUEST)

class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetRequestSerializer,
    responses={200: 'Password reset email sent', 400: 'Invalid email'}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def password_reset_request(request):
    try:
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                # Return success message even if user doesn't exist (security)
                return Response({
                    'message': 'If an account with this email exists, password reset instructions have been sent.'
                }, status=status.HTTP_200_OK)
            
            # Create reset token
            token = str(uuid.uuid4())
            expires_at = timezone.now() + timedelta(hours=24)
            
            reset_token_obj = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=expires_at
            )
            
            # Send password reset email
            email_sent = EmailService.send_password_reset_email(user, token, request)
            
            return Response({
                'message': 'Password reset instructions have been sent to your email address.',
                'success': True
            }, status=status.HTTP_200_OK)
        
        return Response({
            'error': 'Please provide a valid email address.',
            'success': False
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        return Response({
            'error': 'An error occurred while processing your request. Please try again.',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    request_body=PasswordResetSerializer,
    responses={200: 'Password reset successful', 400: 'Invalid token or passwords'}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def password_reset_validate(request):
    try:
        token = request.data.get('token')
        if not token:
            return Response({
                'error': 'Token is required.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            return Response({
                'message': 'Token is valid.',
                'success': True
            }, status=status.HTTP_200_OK)
        
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Invalid or expired reset token.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        print(f"Token validation error: {str(e)}")
        return Response({
            'error': 'An error occurred while validating the token.',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['token', 'password', 'password_confirm'],
        properties={
            'token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token from email'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='New password'),
            'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password'),
        }
    ),
    responses={200: 'Password reset successful', 400: 'Invalid data'}
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
@csrf_exempt
def password_reset_confirm(request):
    try:
        token = request.data.get('token')
        password = request.data.get('password')
        password_confirm = request.data.get('password_confirm')
        
        if not all([token, password, password_confirm]):
            return Response({
                'error': 'Token, password, and password confirmation are required.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password != password_confirm:
            return Response({
                'error': 'Passwords do not match.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            reset_token = PasswordResetToken.objects.get(
                token=token,
                is_used=False,
                expires_at__gt=timezone.now()
            )
        except PasswordResetToken.DoesNotExist:
            return Response({
                'error': 'Invalid or expired reset token.',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Update password
        user = reset_token.user
        user.set_password(password)
        user.save()
        
        # Mark token as used
        reset_token.is_used = True
        reset_token.save()
        
        return Response({
            'message': 'Password reset successful.',
            'success': True
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Password reset error: {str(e)}")
        return Response({
            'error': 'An error occurred while resetting your password.',
            'success': False
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)