"""
Views for user authentication and management.
"""
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer,
    RegisterSerializer,
    ChangePasswordSerializer,
    UpdateProfileSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    API endpoint for user registration.
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    def create(self, request, *args, **kwargs):
        """Register a new user and return tokens."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        # Return user data with tokens
        user_serializer = UserSerializer(user)
        return Response({
            'user': user_serializer.data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for retrieving and updating user profile.
    """
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        """Return the current user."""
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        """Update user profile."""
        serializer = UpdateProfileSerializer(
            self.get_object(),
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full user data
        user_serializer = UserSerializer(self.get_object())
        return Response(user_serializer.data)


class ChangePasswordView(generics.UpdateAPIView):
    """
    API endpoint for changing user password.
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def update(self, request, *args, **kwargs):
        """Change user password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Change password
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response({
            'message': 'Password updated successfully.'
        }, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout by blacklisting the refresh token.
    """
    try:
        refresh_token = request.data.get('refresh_token')
        if not refresh_token:
            return Response(
                {'error': 'Refresh token is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({
            'message': 'Successfully logged out.'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_dashboard_view(request):
    """
    Get dashboard data for the current user.
    """
    user = request.user
    
    # Get tenant info
    tenant_data = None
    if user.tenant:
        from apps.core.models import Tenant
        tenant = user.tenant
        
        # Get statistics
        total_users = tenant.users.count()
        active_licenses = tenant.licenses.filter(is_active=True).count()
        
        tenant_data = {
            'id': str(tenant.id),
            'name': tenant.name,
            'subscription_plan': tenant.subscription_plan,
            'is_trial_active': tenant.is_trial_active,
            'total_users': total_users,
            'active_licenses': active_licenses,
        }
    
    return Response({
        'user': UserSerializer(user).data,
        'tenant': tenant_data,
    })


class LoginView(APIView):
    """
    Custom login view that returns user data along with JWT tokens.
    This aligns the login response shape with the register endpoint so the
    frontend can set auth state in a single response.
    """
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # Validate credentials and obtain tokens using the standard serializer
        serializer = TokenObtainPairSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        tokens = serializer.validated_data

        # Try to find the user by email (project uses email as USERNAME_FIELD)
        email = request.data.get('email') or request.data.get('username')
        user = None
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                user = None

        user_data = UserSerializer(user).data if user else None

        return Response({
            'user': user_data,
            'tokens': {
                'refresh': tokens.get('refresh'),
                'access': tokens.get('access'),
            }
        }, status=status.HTTP_200_OK)
