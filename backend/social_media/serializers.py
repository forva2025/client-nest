from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Post, Comment, Engagement, Hashtag, MediaFile
import re

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """Minimal user serializer for nested relationships"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_picture']

class MediaFileSerializer(serializers.ModelSerializer):
    """Serializer for media files"""
    class Meta:
        model = MediaFile
        fields = ['id', 'file', 'file_type', 'file_name', 'file_size', 'mime_type', 
                 'width', 'height', 'duration', 'created_at']
        read_only_fields = ['id', 'file_name', 'file_size', 'mime_type', 'width', 'height', 'duration', 'created_at']

class CommentSerializer(serializers.ModelSerializer):
    """Serializer for comments with nested relationships"""
    author = UserSerializer(read_only=True)
    replies = serializers.SerializerMethodField()
    like_count = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = ['id', 'post', 'author', 'parent_comment', 'content', 'media_files',
                 'likes', 'like_count', 'mentions', 'is_edited', 'edited_at',
                 'replies', 'is_liked_by_user', 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'like_count', 'is_edited', 'edited_at', 'created_at', 'updated_at']

    def get_replies(self, obj):
        """Get nested replies for this comment"""
        replies = obj.replies.all()
        return CommentSerializer(replies, many=True, context=self.context).data

    def get_is_liked_by_user(self, obj):
        """Check if current user liked this comment"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

class CommentCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating comments"""
    class Meta:
        model = Comment
        fields = ['post', 'parent_comment', 'content', 'media_files']

    def validate_content(self, value):
        """Validate comment content"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Comment content cannot be empty")
        if len(value) > 1000:
            raise serializers.ValidationError("Comment content cannot exceed 1000 characters")
        return value

    def validate(self, data):
        """Validate comment data"""
        # Check if parent comment exists and belongs to the same post
        if data.get('parent_comment'):
            parent = data['parent_comment']
            if parent.post != data['post']:
                raise serializers.ValidationError("Parent comment must belong to the same post")
        return data

class PostSerializer(serializers.ModelSerializer):
    """Main serializer for posts with nested relationships"""
    author = UserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.ReadOnlyField()
    like_count = serializers.ReadOnlyField()
    share_count = serializers.ReadOnlyField()
    view_count = serializers.ReadOnlyField()
    is_liked_by_user = serializers.SerializerMethodField()
    is_shared_by_user = serializers.SerializerMethodField()
    is_bookmarked_by_user = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'author', 'content', 'post_type', 'visibility', 'media_files',
                 'link_url', 'link_title', 'link_description', 'link_image',
                 'likes', 'shares', 'bookmarks', 'view_count', 'share_count', 
                 'comment_count', 'like_count', 'hashtags', 'mentions',
                 'is_edited', 'edited_at', 'is_pinned', 'is_featured',
                 'comments', 'is_liked_by_user', 'is_shared_by_user', 'is_bookmarked_by_user',
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'author', 'view_count', 'share_count', 'comment_count', 
                           'like_count', 'is_edited', 'edited_at', 'created_at', 'updated_at']

    def get_is_liked_by_user(self, obj):
        """Check if current user liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False

    def get_is_shared_by_user(self, obj):
        """Check if current user shared this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.shares.filter(id=request.user.id).exists()
        return False

    def get_is_bookmarked_by_user(self, obj):
        """Check if current user bookmarked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(id=request.user.id).exists()
        return False

class PostCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating posts"""
    class Meta:
        model = Post
        fields = ['content', 'post_type', 'visibility', 'media_files', 'link_url', 
                 'link_title', 'link_description', 'link_image']

    def validate_content(self, value):
        """Validate post content"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Post content cannot be empty")
        if len(value) > 5000:
            raise serializers.ValidationError("Post content cannot exceed 5000 characters")
        return value

    def validate_post_type(self, value):
        """Validate post type based on content"""
        if value == 'link' and not self.initial_data.get('link_url'):
            raise serializers.ValidationError("Link URL is required for link posts")
        return value

    def validate_media_files(self, value):
        """Validate media files"""
        if value and len(value) > 10:
            raise serializers.ValidationError("Cannot attach more than 10 media files")
        return value

    def extract_hashtags_and_mentions(self, content):
        """Extract hashtags and mentions from content"""
        hashtags = re.findall(r'#(\w+)', content)
        mentions = re.findall(r'@(\w+)', content)
        return hashtags, mentions

    def create(self, validated_data):
        """Create post with hashtags and mentions extraction"""
        content = validated_data.get('content', '')
        hashtags, mentions = self.extract_hashtags_and_mentions(content)
        
        validated_data['hashtags'] = hashtags
        validated_data['mentions'] = mentions
        validated_data['author'] = self.context['request'].user
        
        return super().create(validated_data)

class PostUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating posts"""
    class Meta:
        model = Post
        fields = ['content', 'visibility', 'media_files', 'link_url', 
                 'link_title', 'link_description', 'link_image']

    def validate_content(self, value):
        """Validate post content"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Post content cannot be empty")
        if len(value) > 5000:
            raise serializers.ValidationError("Post content cannot exceed 5000 characters")
        return value

    def extract_hashtags_and_mentions(self, content):
        """Extract hashtags and mentions from content"""
        hashtags = re.findall(r'#(\w+)', content)
        mentions = re.findall(r'@(\w+)', content)
        return hashtags, mentions

    def update(self, instance, validated_data):
        """Update post with hashtags and mentions extraction"""
        content = validated_data.get('content', instance.content)
        hashtags, mentions = self.extract_hashtags_and_mentions(content)
        
        validated_data['hashtags'] = hashtags
        validated_data['mentions'] = mentions
        validated_data['is_edited'] = True
        
        return super().update(instance, validated_data)

class EngagementSerializer(serializers.ModelSerializer):
    """Serializer for engagement tracking"""
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Engagement
        fields = ['id', 'post', 'user', 'engagement_type', 'metadata', 
                 'ip_address', 'user_agent', 'created_at']
        read_only_fields = ['id', 'user', 'ip_address', 'user_agent', 'created_at']

    def validate_engagement_type(self, value):
        """Validate engagement type"""
        valid_types = [choice[0] for choice in Engagement.ENGAGEMENT_TYPE_CHOICES]
        if value not in valid_types:
            raise serializers.ValidationError(f"Invalid engagement type. Must be one of: {valid_types}")
        return value

    def create(self, validated_data):
        """Create engagement with user and request info"""
        validated_data['user'] = self.context['request'].user
        validated_data['ip_address'] = self.context['request'].META.get('REMOTE_ADDR')
        validated_data['user_agent'] = self.context['request'].META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)

class HashtagSerializer(serializers.ModelSerializer):
    """Serializer for hashtags"""
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'post_count', 'is_trending', 'trend_score', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'post_count', 'is_trending', 'trend_score', 
                           'created_at', 'updated_at']

class PostAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for post analytics"""
    engagement_breakdown = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = ['id', 'view_count', 'like_count', 'share_count', 'comment_count',
                 'engagement_breakdown', 'created_at']

    def get_engagement_breakdown(self, obj):
        """Get detailed engagement breakdown"""
        engagements = obj.engagements.values('engagement_type').annotate(
            count=serializers.Count('engagement_type')
        )
        return {item['engagement_type']: item['count'] for item in engagements}

class TrendingHashtagsSerializer(serializers.ModelSerializer):
    """Serializer for trending hashtags"""
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'post_count', 'trend_score', 'is_trending'] 