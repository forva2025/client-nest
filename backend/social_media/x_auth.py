from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
import requests
from .x_config import X_CONFIG, X_ENDPOINTS
from .models import SocialAccount
from requests_oauthlib import OAuth1Session
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

class XAuthView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Initiate X OAuth 1.0a flow"""
        # Create OAuth1Session for request token
        oauth = OAuth1Session(
            X_CONFIG['API_KEY'],
            client_secret=X_CONFIG['API_SECRET'],
            callback_uri=X_CONFIG['REDIRECT_URI']
        )
        
        try:
            # Get request token
            fetch_response = oauth.fetch_request_token(X_ENDPOINTS['REQUEST_TOKEN_URL'])
            request_token = fetch_response.get('oauth_token')
            request_token_secret = fetch_response.get('oauth_token_secret')
            
            # Store tokens in session
            request.session['x_request_token'] = request_token
            request.session['x_request_token_secret'] = request_token_secret
            
            # Get authorization URL
            auth_url = oauth.authorization_url(X_ENDPOINTS['AUTH_URL'])
            
            return redirect(auth_url)
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

class XCallbackView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Handle X OAuth 1.0a callback"""
        oauth_token = request.GET.get('oauth_token')
        oauth_verifier = request.GET.get('oauth_verifier')
        
        if not oauth_token or not oauth_verifier:
            return JsonResponse({'error': 'Missing OAuth parameters'}, status=400)
        
        # Get stored request tokens
        request_token = request.session.get('x_request_token')
        request_token_secret = request.session.get('x_request_token_secret')
        
        if not request_token or not request_token_secret:
            return JsonResponse({'error': 'No request tokens found'}, status=400)
        
        # Create OAuth1Session for access token
        oauth = OAuth1Session(
            X_CONFIG['API_KEY'],
            client_secret=X_CONFIG['API_SECRET'],
            resource_owner_key=request_token,
            resource_owner_secret=request_token_secret,
            verifier=oauth_verifier
        )
        
        try:
            # Get access token
            oauth_tokens = oauth.fetch_access_token(X_ENDPOINTS['ACCESS_TOKEN_URL'])
            access_token = oauth_tokens.get('oauth_token')
            access_token_secret = oauth_tokens.get('oauth_token_secret')
            
            # Get user info
            oauth = OAuth1Session(
                X_CONFIG['API_KEY'],
                client_secret=X_CONFIG['API_SECRET'],
                resource_owner_key=access_token,
                resource_owner_secret=access_token_secret
            )
            
            user_info = oauth.get(f"{X_ENDPOINTS['API_URL']}/users/me").json()
            
            # Create or update social account
            social_account, created = SocialAccount.objects.update_or_create(
                user=request.user,
                platform='x',
                account_id=user_info['data']['id'],
                defaults={
                    'access_token': access_token,
                    'access_token_secret': access_token_secret,
                    'is_active': True
                }
            )
            
            # Clear session data
            if 'x_request_token' in request.session:
                del request.session['x_request_token']
            if 'x_request_token_secret' in request.session:
                del request.session['x_request_token_secret']
            
            return JsonResponse({
                'status': 'success',
                'message': 'X account connected successfully',
                'account_id': social_account.id
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400) 