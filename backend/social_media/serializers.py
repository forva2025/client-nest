from rest_framework import serializers
from .models import SocialAccount, PostAnalytics

class SocialAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ['id', 'user', 'platform', 'account_id', 'is_active', 
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PostAnalyticsSerializer(serializers.ModelSerializer):
    social_account = SocialAccountSerializer(read_only=True)
    
    class Meta:
        model = PostAnalytics
        fields = ['id', 'post', 'social_account', 'likes', 'comments', 
                 'shares', 'reach', 'engagement_rate', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at'] 