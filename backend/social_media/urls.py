from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SocialAccountViewSet, PostAnalyticsViewSet, XConnectionTestView, XPostTestView, FacebookConnectionTestView, FacebookPostView
from .instagram_auth import InstagramAuthView, InstagramCallbackView
from .x_auth import XAuthView, XCallbackView
from .facebook_auth import FacebookAuthView, FacebookCallbackView

router = DefaultRouter()
router.register(r'accounts', SocialAccountViewSet, basename='social-account')
router.register(r'analytics', PostAnalyticsViewSet, basename='post-analytics')

urlpatterns = [
    path('', include(router.urls)),
    path('instagram/auth/', InstagramAuthView.as_view(), name='instagram_auth'),
    path('instagram/callback/', InstagramCallbackView.as_view(), name='instagram_callback'),
    path('x/auth/', XAuthView.as_view(), name='x_auth'),
    path('x/callback/', XCallbackView.as_view(), name='x_callback'),
    path('x/test-connection/', XConnectionTestView.as_view(), name='x_test_connection'),
    path('x/test-post/', XPostTestView.as_view(), name='x_test_post'),
    path('facebook/auth/', FacebookAuthView.as_view(), name='facebook_auth'),
    path('facebook/callback/', FacebookCallbackView.as_view(), name='facebook_callback'),
    path('facebook/test-connection/', FacebookConnectionTestView.as_view(), name='facebook_test_connection'),
    path('facebook/post/', FacebookPostView.as_view(), name='facebook_post'),
] 