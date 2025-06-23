from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from .models import User, UserProfile, SocialMediaAccount
from .serializers import UserSerializer, UserProfileSerializer, SocialMediaAccountSerializer, UserRegistrationSerializer
from rest_framework.throttling import AnonRateThrottle
from .utils import send_welcome_email
import logging

logger = logging.getLogger(__name__)

class RegistrationRateThrottle(AnonRateThrottle):
    rate = '3/hour'  # 3 registrations per hour per IP

# Create your views here.

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer

class SocialMediaAccountViewSet(viewsets.ModelViewSet):
    queryset = SocialMediaAccount.objects.all()
    serializer_class = SocialMediaAccountSerializer

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RegistrationRateThrottle]  # Add rate limiting

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
        
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
