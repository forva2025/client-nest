from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import SocialAccount, PostAnalytics
from .serializers import SocialAccountSerializer, PostAnalyticsSerializer
from .instagram_service import InstagramService
from rest_framework.views import APIView
from .x_service import XService
from rest_framework_simplejwt.authentication import JWTAuthentication
from .facebook_service import FacebookService
import requests

# Create your views here.

class SocialAccountViewSet(viewsets.ModelViewSet):
    serializer_class = SocialAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return SocialAccount.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        account = self.get_object()
        if account.platform == 'instagram':
            try:
                instagram_service = InstagramService(account)
                instagram_service.refresh_token()
                return Response({'status': 'Token refreshed successfully'})
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'error': 'Token refresh not supported for this platform'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        account = self.get_object()
        account.is_active = False
        account.save()
        return Response({'status': 'Account disconnected'})

    @action(detail=True, methods=['get'])
    def account_info(self, request, pk=None):
        account = self.get_object()
        if account.platform == 'instagram':
            try:
                instagram_service = InstagramService(account)
                info = instagram_service.get_account_info()
                return Response(info)
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'error': 'Account info not supported for this platform'},
            status=status.HTTP_400_BAD_REQUEST
        )

class PostAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = PostAnalyticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get_queryset(self):
        return PostAnalytics.objects.filter(
            post__user=self.request.user
        ).select_related('social_account')

    @action(detail=True, methods=['post'])
    def refresh_analytics(self, request, pk=None):
        analytics = self.get_object()
        if analytics.social_account.platform == 'instagram':
            try:
                instagram_service = InstagramService(analytics.social_account)
                instagram_service.update_post_analytics(analytics.post.id)
                return Response({'status': 'Analytics refreshed successfully'})
            except Exception as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(
            {'error': 'Analytics refresh not supported for this platform'},
            status=status.HTTP_400_BAD_REQUEST
        )

class XConnectionTestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def get(self, request):
        """Test X connection and return account info"""
        try:
            # Get the user's X account
            x_account = SocialAccount.objects.filter(
                user=request.user,
                platform='x',
                is_active=True
            ).first()
            
            if not x_account:
                return Response({
                    'status': 'error',
                    'message': 'No active X account found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Initialize X service with both tokens
            x_service = XService(
                access_token=x_account.access_token,
                access_token_secret=x_account.access_token_secret
            )
            
            # Get account info
            account_info = x_service.get_account_info()
            
            return Response({
                'status': 'success',
                'message': 'X account is connected',
                'account_info': account_info
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class XPostTestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    
    def post(self, request):
        """Test posting to X"""
        try:
            # Get the user's X account
            x_account = SocialAccount.objects.filter(
                user=request.user,
                platform='x',
                is_active=True
            ).first()
            
            if not x_account:
                return Response({
                    'status': 'error',
                    'message': 'No active X account found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Get the content from the request
            content = request.data.get('content')
            if not content:
                return Response({
                    'status': 'error',
                    'message': 'No content provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Initialize X service with both tokens
            x_service = XService(
                access_token=x_account.access_token,
                access_token_secret=x_account.access_token_secret
            )
            
            # Post the content
            result = x_service.post_content(content)
            
            return Response({
                'status': 'success',
                'message': 'Tweet posted successfully',
                'tweet_id': result.get('id'),
                'text': result.get('text'),
                'created_at': result.get('created_at')
            })
            
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FacebookConnectionTestView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        """Test Facebook connection and return account info"""
        try:
            # Get the user's Facebook account
            fb_account = SocialAccount.objects.filter(
                user=request.user,
                platform='facebook',
                is_active=True
            ).first()

            if not fb_account:
                return Response({
                    'status': 'error',
                    'message': 'No active Facebook account found'
                }, status=status.HTTP_404_NOT_FOUND)

            # Initialize Facebook service
            fb_service = FacebookService(fb_account.access_token)
            account_info = fb_service.get_account_info()

            return Response({
                'status': 'success',
                'message': 'Facebook account is connected',
                'account_info': account_info
            })
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class FacebookPostView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        content = request.data.get('content')
        if not content:
            return Response({'error': 'No content provided'}, status=400)

        fb_account = SocialAccount.objects.filter(
            user=request.user,
            platform='facebook',
            is_active=True
        ).first()

        if not fb_account:
            return Response({'error': 'No active Facebook account found'}, status=404)

        access_token = fb_account.access_token
        url = "https://graph.facebook.com/me/feed"
        data = {
            'message': content,
            'access_token': access_token
        }
        response = requests.post(url, data=data)
        if response.status_code == 200:
            return Response({'status': 'success', 'response': response.json()})
        else:
            return Response({'status': 'error', 'response': response.json()}, status=response.status_code)
