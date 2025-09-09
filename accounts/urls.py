from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('password-reset/', views.password_reset_request, name='password_reset_request'),
    path('password-reset/validate/', views.password_reset_validate, name='password_reset_validate'),
    path('password-reset/confirm/', views.password_reset_confirm, name='password_reset_confirm'),
]