"""
URL configuration for accounts app.
"""
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LoginView
from . import views

app_name = 'accounts'

urlpatterns = [
    # JWT Authentication
    # Use custom LoginView so the response includes user data + tokens
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', views.logout_view, name='logout'),
    
    # Registration
    path('register/', views.RegisterView.as_view(), name='register'),
    
    # User Profile
    path('profile/', views.UserProfileView.as_view(), name='profile'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    
    # Dashboard
    path('dashboard/', views.user_dashboard_view, name='dashboard'),
]
