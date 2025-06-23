from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.core.validators import FileExtensionValidator
import uuid

class Post(models.Model):
    """
    Enhanced model for social media posts with media support and engagement tracking
    """
    POST_TYPE_CHOICES = (
        ('text', 'Text'),
        ('image', 'Image'),
        ('video', 'Video'),
        ('link', 'Link'),
        ('poll', 'Poll'),
    )
    
    VISIBILITY_CHOICES = (
        ('public', 'Public'),
        ('private', 'Private'),
        ('followers', 'Followers Only'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    post_type = models.CharField(max_length=10, choices=POST_TYPE_CHOICES, default='text')
    visibility = models.CharField(max_length=10, choices=VISIBILITY_CHOICES, default='public')
    
    # Media fields
    media_files = models.JSONField(default=list, blank=True)  # Store file URLs/paths
    link_url = models.URLField(blank=True, null=True)
    link_title = models.CharField(max_length=255, blank=True)
    link_description = models.TextField(blank=True)
    link_image = models.URLField(blank=True, null=True)
    
    # Engagement fields
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)
    shares = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='shared_posts', blank=True)
    bookmarks = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='bookmarked_posts', blank=True)
    
    # Analytics fields
    view_count = models.PositiveIntegerField(default=0)
    share_count = models.PositiveIntegerField(default=0)
    comment_count = models.PositiveIntegerField(default=0)
    like_count = models.PositiveIntegerField(default=0)
    
    # Content analysis
    hashtags = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    mentions = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    # Metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    is_pinned = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['post_type', '-created_at']),
            models.Index(fields=['visibility', '-created_at']),
            models.Index(fields=['hashtags']),
        ]

    def __str__(self):
        return f"{self.author.username}'s {self.post_type} post at {self.created_at}"

    def update_engagement_counts(self):
        """Update engagement counts from related models"""
        self.like_count = self.likes.count()
        self.share_count = self.shares.count()
        self.comment_count = self.comments.count()
        self.save(update_fields=['like_count', 'share_count', 'comment_count'])

class Comment(models.Model):
    """
    Enhanced model for comments on posts with threading support
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies')
    
    content = models.TextField()
    media_files = models.JSONField(default=list, blank=True)  # Store file URLs/paths
    
    # Engagement
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_comments', blank=True)
    like_count = models.PositiveIntegerField(default=0)
    
    # Content analysis
    mentions = ArrayField(models.CharField(max_length=50), blank=True, default=list)
    
    # Metadata
    is_edited = models.BooleanField(default=False)
    edited_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['post', 'created_at']),
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent_comment', 'created_at']),
        ]

    def __str__(self):
        return f"{self.author.username}'s comment on {self.post}"

    def update_like_count(self):
        """Update like count"""
        self.like_count = self.likes.count()
        self.save(update_fields=['like_count'])

class Engagement(models.Model):
    """
    Enhanced model for tracking detailed engagement metrics on posts
    """
    ENGAGEMENT_TYPE_CHOICES = (
        ('view', 'View'),
        ('like', 'Like'),
        ('share', 'Share'),
        ('bookmark', 'Bookmark'),
        ('comment', 'Comment'),
        ('click', 'Click'),
        ('impression', 'Impression'),
        ('reach', 'Reach'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='engagements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='engagements')
    engagement_type = models.CharField(max_length=20, choices=ENGAGEMENT_TYPE_CHOICES)
    
    # Additional engagement data
    metadata = models.JSONField(default=dict, blank=True)  # Store additional engagement data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['post', 'engagement_type', '-created_at']),
            models.Index(fields=['user', 'engagement_type', '-created_at']),
            models.Index(fields=['engagement_type', '-created_at']),
        ]
        unique_together = ['post', 'user', 'engagement_type']  # Prevent duplicate engagements

    def __str__(self):
        return f"{self.user.username} {self.engagement_type} on {self.post}"

class Hashtag(models.Model):
    """
    Model for hashtag tracking and trending
    """
    name = models.CharField(max_length=50, unique=True)
    post_count = models.PositiveIntegerField(default=0)
    is_trending = models.BooleanField(default=False)
    trend_score = models.FloatField(default=0.0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-trend_score', '-post_count']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['is_trending', '-trend_score']),
        ]

    def __str__(self):
        return f"#{self.name} ({self.post_count} posts)"

class MediaFile(models.Model):
    """
    Model for managing media files attached to posts and comments
    """
    MEDIA_TYPE_CHOICES = (
        ('image', 'Image'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('document', 'Document'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    file = models.FileField(upload_to='social_media/')
    file_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    file_name = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField()  # Size in bytes
    mime_type = models.CharField(max_length=100)
    
    # Metadata
    width = models.PositiveIntegerField(null=True, blank=True)  # For images/videos
    height = models.PositiveIntegerField(null=True, blank=True)  # For images/videos
    duration = models.FloatField(null=True, blank=True)  # For videos/audio in seconds
    
    # Usage tracking
    post = models.ForeignKey(Post, on_delete=models.CASCADE, null=True, blank=True, related_name='media_files_rel')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, null=True, blank=True, related_name='media_files_rel')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['file_type', '-created_at']),
            models.Index(fields=['post', '-created_at']),
        ]

    def __str__(self):
        return f"{self.file_name} ({self.file_type})"
