from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from .models import User, UserProfile, SocialMediaAccount
from .serializers import (
    UserSerializer, UserDetailSerializer, UserUpdateSerializer, UserRegistrationSerializer,
    UserProfileSerializer, UserProfileUpdateSerializer, SocialMediaAccountSerializer,
    PasswordChangeSerializer
)
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from .utils import send_welcome_email
import logging

logger = logging.getLogger(__name__)

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '3/hour'  # 3 registrations per hour per IP

class UserRateThrottle(UserRateThrottle):
    rate = '100/hour'  # 100 requests per hour per user

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj == request.user or obj.user == request.user

class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for User CRUD operations.
    
    list: Get all users (admin only)
    create: Register a new user (public)
    retrieve: Get user details (owner or admin)
    update: Update user (owner only)
    partial_update: Partially update user (owner only)
    destroy: Delete user (owner or admin)
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'email', 'date_joined', 'last_login']
    ordering = ['-date_joined']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'create':
            return UserRegistrationSerializer
        return UserSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action == 'create':
            permission_classes = [permissions.AllowAny]
        elif self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        elif self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset based on user permissions"""
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(id=self.request.user.id)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user's profile"""
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_profile(self, request):
        """Update current user's profile"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Change user password"""
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password changed successfully'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def deactivate_account(self, request):
        """Deactivate user account"""
        user = request.user
        user.is_active = False
        user.save()
        return Response({'message': 'Account deactivated successfully'})

class UserProfileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for UserProfile CRUD operations.
    
    list: Get all profiles (admin only)
    create: Create profile (owner only)
    retrieve: Get profile details (owner or admin)
    update: Update profile (owner only)
    partial_update: Partially update profile (owner only)
    destroy: Delete profile (owner or admin)
    """
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    search_fields = ['user__username', 'user__email', 'phone_number']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action in ['update', 'partial_update']:
            return UserProfileUpdateSerializer
        return UserProfileSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action == 'list':
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset based on user permissions"""
        if self.request.user.is_staff:
            return UserProfile.objects.all()
        return UserProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_profile(self, request):
        """Get current user's profile"""
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = self.get_serializer(profile)
        return Response(serializer.data)

    @action(detail=False, methods=['put', 'patch'], permission_classes=[permissions.IsAuthenticated])
    def update_my_profile(self, request):
        """Update current user's profile"""
        profile = get_object_or_404(UserProfile, user=request.user)
        serializer = UserProfileUpdateSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SocialMediaAccount CRUD operations.
    
    list: Get all social accounts (owner or admin)
    create: Link social media account (owner only)
    retrieve: Get account details (owner or admin)
    update: Update account (owner only)
    partial_update: Partially update account (owner only)
    destroy: Unlink account (owner only)
    """
    queryset = SocialMediaAccount.objects.all()
    serializer_class = SocialMediaAccountSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    throttle_classes = [UserRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['platform']
    search_fields = ['account_id', 'platform']

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action == 'list':
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset based on user permissions"""
        if self.request.user.is_staff:
            return SocialMediaAccount.objects.all()
        return SocialMediaAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Set the user when creating a social media account"""
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_accounts(self, request):
        """Get current user's social media accounts"""
        accounts = SocialMediaAccount.objects.filter(user=request.user)
        serializer = self.get_serializer(accounts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def platforms(self, request):
        """Get available social media platforms"""
        platforms = [{'value': choice[0], 'label': choice[1]} 
                    for choice in SocialMediaAccount.PLATFORM_CHOICES]
        return Response(platforms)

class UserRegistrationView(generics.CreateAPIView):
    """
    User registration endpoint.
    
    POST: Register a new user account
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationRateThrottle]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Send welcome email
        try:
            send_welcome_email(user)
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
            # Don't fail registration if email fails
        
        # Return user data without sensitive information
        response_serializer = UserSerializer(user)
        headers = self.get_success_headers(serializer.data)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
