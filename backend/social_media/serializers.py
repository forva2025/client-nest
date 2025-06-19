from rest_framework import serializers
from .models import Post, Comment, Engagement

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ('id', 'author', 'content', 'created_at', 'updated_at', 'likes')

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'post', 'author', 'content', 'created_at', 'updated_at')

class EngagementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Engagement
        fields = ('id', 'post', 'user', 'engagement_type', 'created_at') 