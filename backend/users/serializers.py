from rest_framework import serializers
from .models import User, UserProfile, SocialMediaAccount

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'bio', 'profile_picture', 'created_at', 'updated_at')

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'phone_number', 'address', 'social_links', 'preferences', 'created_at', 'updated_at')

class SocialMediaAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialMediaAccount
        fields = ('id', 'user', 'platform', 'account_id', 'access_token', 'created_at', 'updated_at') 