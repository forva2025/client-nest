import requests
from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .models import SocialAccount

class FacebookAuthView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        fb_auth_url = (
            f"https://www.facebook.com/v18.0/dialog/oauth?"
            f"client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}"
            f"&scope=email,public_profile"
            f"&response_type=code"
        )
        return redirect(fb_auth_url)

class FacebookCallbackView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = request.GET.get('code')
        if not code:
            return JsonResponse({'error': 'Missing code parameter'}, status=400)
        token_url = (
            f"https://graph.facebook.com/v18.0/oauth/access_token?"
            f"client_id={settings.FACEBOOK_APP_ID}"
            f"&redirect_uri={settings.FACEBOOK_REDIRECT_URI}"
            f"&client_secret={settings.FACEBOOK_APP_SECRET}"
            f"&code={code}"
        )
        token_response = requests.get(token_url)
        token_data = token_response.json()
        access_token = token_data.get('access_token')
        if not access_token:
            return JsonResponse({'error': 'Failed to obtain access token', 'details': token_data}, status=400)
        # Get user info
        user_info_url = f"https://graph.facebook.com/me?fields=id,name,email&access_token={access_token}"
        user_info_response = requests.get(user_info_url)
        user_info = user_info_response.json()
        account_id = user_info.get('id')
        if not account_id:
            return JsonResponse({'error': 'Failed to fetch Facebook user info', 'details': user_info}, status=400)
        # Create or update SocialAccount
        social_account, created = SocialAccount.objects.update_or_create(
            user=request.user,
            platform='facebook',
            account_id=account_id,
            defaults={
                'access_token': access_token,
                'is_active': True
            }
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Facebook account connected successfully',
            'account_id': social_account.id
        }) 