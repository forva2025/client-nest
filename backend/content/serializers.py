from rest_framework import serializers
from .models import Post, Schedule

class ScheduleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Schedule
        fields = ['id', 'post', 'scheduled_time', 'platform', 'is_published', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class PostSerializer(serializers.ModelSerializer):
    schedules = ScheduleSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'title', 'content', 'media_url', 'status', 
                 'created_at', 'updated_at', 'published_at', 'schedules']
        read_only_fields = ['created_at', 'updated_at', 'published_at'] 