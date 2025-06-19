from django.db import models
from django.conf import settings

class Post(models.Model):
    """
    Model for social media posts
    """
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    likes = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True)

    def __str__(self):
        return f"{self.author.username}'s post at {self.created_at}"

class Comment(models.Model):
    """
    Model for comments on posts
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.author.username}'s comment on {self.post}"

class Engagement(models.Model):
    """
    Model for tracking engagement metrics on posts
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='engagements')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='engagements')
    engagement_type = models.CharField(max_length=50)  # e.g., 'view', 'share', 'bookmark'
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} {self.engagement_type} on {self.post}"
