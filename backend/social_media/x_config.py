"""
X (Twitter) API Configuration

Note: Access tokens are stored per-user in the database (SocialAccount model),
not in environment variables. Only API_KEY and API_SECRET are needed for OAuth flow.
"""

import os

X_CONFIG = {
    'API_KEY': os.getenv('X_API_KEY'),
    'API_SECRET': os.getenv('X_API_SECRET'),
    'REDIRECT_URI': os.getenv('X_REDIRECT_URI', 'http://localhost:8000/api/social/x/callback/'),
}

X_ENDPOINTS = {
    'REQUEST_TOKEN_URL': 'https://api.twitter.com/oauth/request_token',
    'AUTH_URL': 'https://api.twitter.com/oauth/authorize',
    'ACCESS_TOKEN_URL': 'https://api.twitter.com/oauth/access_token',
    'API_URL': 'https://api.twitter.com/2',
    'UPLOAD_URL': 'https://upload.twitter.com/1.1/media/upload.json',
}

X_SCOPES = [
    'tweet.read',
    'tweet.write',
    'users.read',
    'offline.access',
] 