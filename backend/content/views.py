from django.shortcuts import render
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from .models import Post, Schedule
from .serializers import PostSerializer, ScheduleSerializer

# Create your views here.

class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def schedule(self, request, pk=None):
        post = self.get_object()
        platform = request.data.get('platform')
        scheduled_time = request.data.get('scheduled_time')

        if not platform or not scheduled_time:
            return Response(
                {'error': 'Platform and scheduled_time are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        schedule = Schedule.objects.create(
            post=post,
            platform=platform,
            scheduled_time=scheduled_time
        )
        post.status = 'scheduled'
        post.save()

        return Response(ScheduleSerializer(schedule).data)

    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        post = self.get_object()
        if post.status != 'scheduled':
            return Response(
                {'error': 'Only scheduled posts can be published'},
                status=status.HTTP_400_BAD_REQUEST
            )

        post.status = 'published'
        post.published_at = timezone.now()
        post.save()

        return Response(PostSerializer(post).data)

class ScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = ScheduleSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Schedule.objects.filter(post__user=self.request.user)

    @action(detail=True, methods=['post'])
    def mark_as_published(self, request, pk=None):
        schedule = self.get_object()
        schedule.is_published = True
        schedule.save()
        return Response(ScheduleSerializer(schedule).data)
