from django.contrib import admin
from .models import Post, Schedule

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'status', 'created_at', 'published_at')
    list_filter = ('status', 'created_at')
    search_fields = ('title', 'content')
    date_hierarchy = 'created_at'

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ('post', 'platform', 'scheduled_time', 'is_published')
    list_filter = ('platform', 'is_published', 'scheduled_time')
    search_fields = ('post__title',)
    date_hierarchy = 'scheduled_time'
