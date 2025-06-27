from datetime import datetime
from typing import Dict, Optional
import requests
from django.conf import settings
from .models import SocialAccount, PostAnalytics
from .instagram_config import INSTAGRAM_CONFIG, INSTAGRAM_ENDPOINTS, PROXY_CONFIG

class InstagramService:
    def __init__(self, social_account: SocialAccount):
        self.social_account = social_account
        self.access_token = social_account.access_token

    def _make_request(self, endpoint: str, method: str = 'GET', data: Optional[Dict] = None) -> Dict:
        """Make a request to the Instagram API with proxy support"""
        url = f"{INSTAGRAM_ENDPOINTS[endpoint]}"
        params = {'access_token': self.access_token}
        
        if PROXY_CONFIG['USE_PROXY']:
            url = f"{PROXY_CONFIG['PROXY_URL']}{url}"
        
        try:
            if method == 'GET':
                response = requests.get(url, params=params)
            else:
                response = requests.post(url, params=params, json=data)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Instagram API request failed: {str(e)}")

    def get_account_info(self) -> Dict:
        """Get Instagram account information"""
        return self._make_request('GRAPH_URL')

    def get_media(self) -> Dict:
        """Get user's media"""
        return self._make_request('MEDIA_URL')

    def publish_post(self, post_data: Dict) -> Dict:
        """Publish a post to Instagram"""
        # Note: Basic Display API doesn't support direct publishing
        # This is a placeholder for when we implement the Graph API
        raise NotImplementedError("Post publishing requires Instagram Graph API access")

    def get_post_analytics(self, post_id: str) -> Dict:
        """Get analytics for a specific post"""
        # Note: Basic Display API has limited analytics
        # This is a placeholder for when we implement the Graph API
        return {
            'id': post_id,
            'engagement': 0,
            'impressions': 0,
            'reach': 0
        }

    def update_post_analytics(self, post_id: str) -> None:
        """Update analytics for a post in our database"""
        analytics_data = self.get_post_analytics(post_id)
        
        PostAnalytics.objects.update_or_create(
            post_id=post_id,
            social_account=self.social_account,
            defaults={
                'likes': analytics_data.get('engagement', 0),
                'comments': 0,  # Basic Display API doesn't provide comment count
                'shares': 0,    # Basic Display API doesn't provide share count
                'reach': analytics_data.get('reach', 0),
                'engagement_rate': 0.0  # Basic Display API doesn't provide engagement rate
            }
        )

    def refresh_token(self) -> None:
        """Refresh the Instagram access token"""
        # Note: Basic Display API tokens are long-lived
        # This is a placeholder for when we implement the Graph API
        pass 