from django.contrib import admin
from .models import SocialAccount, PostAnalytics

@admin.register(SocialAccount)
class SocialAccountAdmin(admin.ModelAdmin):
    list_display = ('user', 'platform', 'account_id', 'is_active', 'created_at')
    list_filter = ('platform', 'is_active', 'created_at')
    search_fields = ('user__username', 'account_id')
    date_hierarchy = 'created_at'

@admin.register(PostAnalytics)
class PostAnalyticsAdmin(admin.ModelAdmin):
    list_display = ('post_id', 'social_account', 'likes', 'comments', 'shares', 'reach')
    list_filter = ('social_account__platform', 'created_at')
    search_fields = ('post_id', 'social_account__account_id')
    date_hierarchy = 'created_at'
