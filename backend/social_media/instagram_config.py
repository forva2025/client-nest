from django.conf import settings
import os

# Instagram Basic Display API Configuration
INSTAGRAM_CONFIG = {
    'CLIENT_ID': os.getenv('INSTAGRAM_CLIENT_ID', ''),
    'CLIENT_SECRET': os.getenv('INSTAGRAM_CLIENT_SECRET', ''),
    'REDIRECT_URI': os.getenv('INSTAGRAM_REDIRECT_URI', 'http://localhost:8000/api/social/instagram/callback/'),
    'SCOPE': [
        'user_profile',
        'user_media'
    ]
}

# Instagram API Endpoints
INSTAGRAM_ENDPOINTS = {
    'AUTH_URL': 'https://api.instagram.com/oauth/authorize',
    'TOKEN_URL': 'https://api.instagram.com/oauth/access_token',
    'GRAPH_URL': 'https://graph.instagram.com/me',
    'MEDIA_URL': 'https://graph.instagram.com/me/media'
}

# Proxy Configuration (if needed)
PROXY_CONFIG = {
    'USE_PROXY': True,
    'PROXY_URL': 'https://api.allorigins.win/raw?url=',  # Example proxy service
} 