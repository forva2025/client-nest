from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserViewSet, UserProfileViewSet, SocialMediaAccountViewSet, UserRegistrationView
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'profiles', UserProfileViewSet, basename='profile')
router.register(r'social-accounts', SocialMediaAccountViewSet, basename='social-account')

# URL patterns for the users app
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
    
    # Registration endpoint
    path('register/', UserRegistrationView.as_view(), name='user-registration'),
] 