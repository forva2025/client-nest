from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class SocialAccount(models.Model):
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('instagram', 'Instagram'),
        ('x', 'X')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='social_media_accounts')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    account_id = models.CharField(max_length=100)
    access_token = models.TextField()
    access_token_secret = models.TextField(null=True, blank=True)
    refresh_token = models.TextField(null=True, blank=True)
    token_expires_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'platform', 'account_id']

    def __str__(self):
        return f"{self.user.username} - {self.platform}"

class PostAnalytics(models.Model):
    # post = models.ForeignKey('social_media.Post', on_delete=models.CASCADE, related_name='analytics')
    post_id = models.CharField(max_length=100)  # Placeholder for post reference
    social_account = models.ForeignKey(SocialAccount, on_delete=models.CASCADE)
    likes = models.IntegerField(default=0)
    comments = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    reach = models.IntegerField(default=0)
    engagement_rate = models.FloatField(default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'Post Analytics'

    def __str__(self):
        return f"Analytics for post {self.post_id} on {self.social_account.platform}"
