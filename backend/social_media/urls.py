from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostViewSet, CommentViewSet, EngagementViewSet, 
    HashtagViewSet, MediaFileViewSet
)

# Create router for ViewSets
router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'engagements', EngagementViewSet, basename='engagement')
router.register(r'hashtags', HashtagViewSet, basename='hashtag')
router.register(r'media', MediaFileViewSet, basename='media')

# URL patterns for the social media app
urlpatterns = [
    # Include router URLs
    path('', include(router.urls)),
] 