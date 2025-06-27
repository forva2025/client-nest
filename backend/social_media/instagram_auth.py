from django.shortcuts import redirect
from django.urls import reverse
from django.views import View
from django.http import JsonResponse
import requests
from .instagram_config import INSTAGRAM_CONFIG, INSTAGRAM_ENDPOINTS, PROXY_CONFIG
from .models import SocialAccount

class InstagramAuthView(View):
    def get(self, request):
        """Initiate Instagram OAuth flow"""
        auth_url = f"{INSTAGRAM_ENDPOINTS['AUTH_URL']}?client_id={INSTAGRAM_CONFIG['CLIENT_ID']}&redirect_uri={INSTAGRAM_CONFIG['REDIRECT_URI']}&scope={' '.join(INSTAGRAM_CONFIG['SCOPE'])}&response_type=code"
        return redirect(auth_url)

class InstagramCallbackView(View):
    def get(self, request):
        """Handle Instagram OAuth callback"""
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'No authorization code received'}, status=400)

        # Exchange code for access token
        token_data = {
            'client_id': INSTAGRAM_CONFIG['CLIENT_ID'],
            'client_secret': INSTAGRAM_CONFIG['CLIENT_SECRET'],
            'grant_type': 'authorization_code',
            'redirect_uri': INSTAGRAM_CONFIG['REDIRECT_URI'],
            'code': code
        }

        try:
            # Use proxy if configured
            url = INSTAGRAM_ENDPOINTS['TOKEN_URL']
            if PROXY_CONFIG['USE_PROXY']:
                url = f"{PROXY_CONFIG['PROXY_URL']}{url}"

            response = requests.post(url, data=token_data)
            response.raise_for_status()
            token_info = response.json()

            # Get Instagram account info
            account_info_url = INSTAGRAM_ENDPOINTS['GRAPH_URL']
            if PROXY_CONFIG['USE_PROXY']:
                account_info_url = f"{PROXY_CONFIG['PROXY_URL']}{account_info_url}"

            account_info = requests.get(
                account_info_url,
                params={'access_token': token_info['access_token']}
            ).json()

            # Create or update social account
            social_account, created = SocialAccount.objects.update_or_create(
                user=request.user,
                platform='instagram',
                account_id=account_info['id'],
                defaults={
                    'access_token': token_info['access_token'],
                    'is_active': True
                }
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Instagram account connected successfully',
                'account_id': social_account.id
            })

        except requests.exceptions.RequestException as e:
            return JsonResponse({'error': str(e)}, status=400) 