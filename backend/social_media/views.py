from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets, generics, permissions, status, filters
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, F
from django.utils import timezone
from datetime import timedelta
from .models import Post, Comment, Engagement, Hashtag, MediaFile
from .serializers import (
    PostSerializer, PostCreateSerializer, PostUpdateSerializer, PostAnalyticsSerializer,
    CommentSerializer, CommentCreateSerializer,
    EngagementSerializer, HashtagSerializer, TrendingHashtagsSerializer,
    MediaFileSerializer
)
from rest_framework.throttling import UserRateThrottle
from users.views import IsOwnerOrReadOnly
from users.models import SocialMediaAccount
import tweepy
import logging

logger = logging.getLogger(__name__)

class SocialMediaRateThrottle(UserRateThrottle):
    rate = '200/hour'  # 200 requests per hour per user

class PostViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Post CRUD operations with engagement tracking.
    
    list: Get all posts (filtered by visibility and permissions)
    create: Create a new post
    retrieve: Get post details with engagement info
    update: Update post (owner only)
    partial_update: Partially update post (owner only)
    destroy: Delete post (owner only)
    """
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SocialMediaRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['author__username', 'post_type', 'visibility', 'hashtags__name']
    search_fields = ['content', 'author__username', 'hashtags__name']
    ordering_fields = ['created_at', 'like_count', 'comment_count']
    ordering = ['-created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return PostCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return PostUpdateSerializer
        return PostSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset based on user permissions"""
        user = self.request.user
        
        # Base queryset
        queryset = Post.objects.select_related('author').prefetch_related(
            'likes', 'shares', 'bookmarks', 'comments', 'engagements'
        )
        
        # Filter by visibility
        if not user.is_staff:
            queryset = queryset.filter(
                Q(visibility='public') |
                Q(author=user) |
                Q(author__followers=user)  # Assuming you have a followers relationship
            )
        
        return queryset

    def perform_create(self, serializer):
        """
        Create a post and optionally publish it to X (Twitter).
        """
        post = serializer.save(author=self.request.user)
        
        # Check if the user wants to post to X
        post_to_x = self.request.data.get('post_to_x', False)

        if post_to_x:
            self.publish_to_x(post)
        
        # Track post creation as engagement
        Engagement.objects.create(
            post=post,
            user=self.request.user,
            engagement_type='impression'
        )

    def publish_to_x(self, post):
        """
        Publishes the given post to the user's linked X (Twitter) account.
        """
        try:
            # Get the user's X account credentials from the database
            x_account = SocialMediaAccount.objects.get(user=post.author, platform='twitter')
            
            if not all([x_account.api_key, x_account.api_secret, x_account.access_token, x_account.access_token_secret]):
                # Handle missing credentials gracefully in a real app
                print("X credentials are not fully configured.")
                return

            # Authenticate with the X API
            client = tweepy.Client(
                consumer_key=x_account.api_key,
                consumer_secret=x_account.api_secret,
                access_token=x_account.access_token,
                access_token_secret=x_account.access_token_secret
            )

            # Publish the tweet
            client.create_tweet(text=post.content)
            print(f"Successfully posted to X for user {post.author.username}")

        except SocialMediaAccount.DoesNotExist:
            print(f"User {post.author.username} has not linked an X account.")
        except tweepy.errors.TweepyException as e:
            print(f"Error posting to X: {e}")
        except Exception as e:
            print(f"An unexpected error occurred during X publication: {e}")

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Like or unlike a post"""
        post = self.get_object()
        user = request.user
        
        if post.likes.filter(id=user.id).exists():
            post.likes.remove(user)
            action = 'unliked'
        else:
            post.likes.add(user)
            action = 'liked'
        
        # Track engagement
        Engagement.objects.get_or_create(
            post=post,
            user=user,
            engagement_type='like',
            defaults={'metadata': {'action': action}}
        )
        
        post.update_engagement_counts()
        return Response({'action': action, 'like_count': post.like_count})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def share(self, request, pk=None):
        """Share a post"""
        post = self.get_object()
        user = request.user
        
        if post.shares.filter(id=user.id).exists():
            post.shares.remove(user)
            action = 'unshared'
        else:
            post.shares.add(user)
            action = 'shared'
        
        # Track engagement
        Engagement.objects.get_or_create(
            post=post,
            user=user,
            engagement_type='share',
            defaults={'metadata': {'action': action}}
        )
        
        post.update_engagement_counts()
        return Response({'action': action, 'share_count': post.share_count})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def bookmark(self, request, pk=None):
        """Bookmark or unbookmark a post"""
        post = self.get_object()
        user = request.user
        
        if post.bookmarks.filter(id=user.id).exists():
            post.bookmarks.remove(user)
            action = 'unbookmarked'
        else:
            post.bookmarks.add(user)
            action = 'bookmarked'
        
        # Track engagement
        Engagement.objects.get_or_create(
            post=post,
            user=user,
            engagement_type='bookmark',
            defaults={'metadata': {'action': action}}
        )
        
        return Response({'action': action})

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def view(self, request, pk=None):
        """Track post view"""
        post = self.get_object()
        user = request.user
        
        # Increment view count
        post.view_count = F('view_count') + 1
        post.save()
        post.refresh_from_db()
        
        # Track engagement
        Engagement.objects.get_or_create(
            post=post,
            user=user,
            engagement_type='view',
            defaults={'metadata': {'source': request.META.get('HTTP_REFERER', '')}}
        )
        
        return Response({'view_count': post.view_count})

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def analytics(self, request, pk=None):
        """Get post analytics"""
        post = self.get_object()
        serializer = PostAnalyticsSerializer(post)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_posts(self, request):
        """Get current user's posts"""
        posts = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def liked_posts(self, request):
        """Get posts liked by current user"""
        posts = self.get_queryset().filter(likes=request.user)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def bookmarked_posts(self, request):
        """Get posts bookmarked by current user"""
        posts = self.get_queryset().filter(bookmarks=request.user)
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(posts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def trending(self, request):
        """Get trending posts"""
        # Posts with high engagement in the last 24 hours
        yesterday = timezone.now() - timedelta(days=1)
        trending_posts = self.get_queryset().filter(
            created_at__gte=yesterday
        ).annotate(
            engagement_score=F('like_count') + F('comment_count') * 2 + F('share_count') * 3
        ).order_by('-engagement_score')[:20]
        
        serializer = self.get_serializer(trending_posts, many=True)
        return Response(serializer.data)

class CommentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Comment CRUD operations.
    
    list: Get comments for a post
    create: Create a new comment
    retrieve: Get comment details
    update: Update comment (owner only)
    partial_update: Partially update comment (owner only)
    destroy: Delete comment (owner only)
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SocialMediaRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'author', 'parent_comment']
    ordering_fields = ['created_at', 'like_count']
    ordering = ['created_at']

    def get_serializer_class(self):
        """Return appropriate serializer class based on action"""
        if self.action == 'create':
            return CommentCreateSerializer
        return CommentSerializer

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset"""
        return Comment.objects.select_related('author', 'post', 'parent_comment').prefetch_related(
            'likes', 'replies'
        )

    def perform_create(self, serializer):
        """Create comment and update post comment count"""
        comment = serializer.save(author=self.request.user)
        
        # Update post comment count
        comment.post.update_engagement_counts()
        
        # Track engagement
        Engagement.objects.create(
            post=comment.post,
            user=self.request.user,
            engagement_type='comment',
            metadata={'comment_id': str(comment.id)}
        )

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
        """Like or unlike a comment"""
        comment = self.get_object()
        user = request.user
        
        if comment.likes.filter(id=user.id).exists():
            comment.likes.remove(user)
            action = 'unliked'
        else:
            comment.likes.add(user)
            action = 'liked'
        
        comment.update_like_count()
        return Response({'action': action, 'like_count': comment.like_count})

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_comments(self, request):
        """Get current user's comments"""
        comments = self.get_queryset().filter(author=request.user)
        page = self.paginate_queryset(comments)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(comments, many=True)
        return Response(serializer.data)

class EngagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Engagement tracking.
    
    list: Get engagement data (admin only)
    create: Track new engagement
    retrieve: Get engagement details (admin only)
    """
    queryset = Engagement.objects.all()
    serializer_class = EngagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    throttle_classes = [SocialMediaRateThrottle]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['post', 'user', 'engagement_type']
    ordering_fields = ['created_at']
    ordering = ['-created_at']

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.IsAdminUser]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset based on permissions"""
        if self.request.user.is_staff:
            return Engagement.objects.select_related('post', 'user')
        return Engagement.objects.filter(user=self.request.user).select_related('post')

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def my_engagements(self, request):
        """Get current user's engagements"""
        engagements = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(engagements)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(engagements, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAdminUser])
    def analytics(self, request):
        """Get engagement analytics"""
        from django.db.models import Count
        from datetime import datetime, timedelta
        
        # Get date range from query params
        days = int(request.query_params.get('days', 7))
        start_date = timezone.now() - timedelta(days=days)
        
        # Engagement breakdown by type
        engagement_breakdown = Engagement.objects.filter(
            created_at__gte=start_date
        ).values('engagement_type').annotate(
            count=Count('engagement_type')
        ).order_by('-count')
        
        # Daily engagement trend
        daily_engagement = Engagement.objects.filter(
            created_at__gte=start_date
        ).extra(
            select={'date': 'DATE(created_at)'}
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
        
        return Response({
            'engagement_breakdown': list(engagement_breakdown),
            'daily_trend': list(daily_engagement),
            'total_engagements': Engagement.objects.filter(created_at__gte=start_date).count()
        })

class HashtagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Hashtag operations (read-only).
    
    list: Get all hashtags
    retrieve: Get hashtag details with related posts
    """
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_trending']
    search_fields = ['name']
    ordering_fields = ['post_count', 'trend_score', 'created_at']
    ordering = ['-trend_score', '-post_count']

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def trending(self, request):
        """Get trending hashtags"""
        trending_hashtags = Hashtag.objects.filter(
            is_trending=True
        ).order_by('-trend_score')[:20]
        
        serializer = TrendingHashtagsSerializer(trending_hashtags, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def posts(self, request, pk=None):
        """Get posts for a specific hashtag"""
        hashtag = self.get_object()
        posts = Post.objects.filter(hashtags__contains=[hashtag.name])
        
        # Apply visibility filters
        if not request.user.is_staff:
            posts = posts.filter(
                Q(visibility='public') |
                Q(author=request.user) |
                Q(author__followers=request.user)
            )
        
        page = self.paginate_queryset(posts)
        if page is not None:
            serializer = PostSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        serializer = PostSerializer(posts, many=True, context={'request': request})
        return Response(serializer.data)

class MediaFileViewSet(viewsets.ModelViewSet):
    """
    ViewSet for MediaFile operations.
    
    list: Get media files (owner only)
    create: Upload media file
    retrieve: Get media file details (owner only)
    destroy: Delete media file (owner only)
    """
    queryset = MediaFile.objects.all()
    serializer_class = MediaFileSerializer
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    throttle_classes = [SocialMediaRateThrottle]

    def get_permissions(self):
        """Return appropriate permissions based on action"""
        if self.action in ['update', 'partial_update', 'destroy']:
            permission_classes = [IsOwnerOrReadOnly]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """Return appropriate queryset based on permissions"""
        if self.request.user.is_staff:
            return MediaFile.objects.all()
        return MediaFile.objects.filter(
            Q(post__author=self.request.user) | Q(comment__author=self.request.user)
        )

    def perform_create(self, serializer):
        """Create media file with metadata"""
        media_file = serializer.save()
        
        # Extract metadata from file
        import os
        from PIL import Image
        
        file_path = media_file.file.path
        file_size = os.path.getsize(file_path)
        
        # Update file metadata
        media_file.file_size = file_size
        media_file.file_name = os.path.basename(file_path)
        
        # Extract image/video metadata
        if media_file.file_type in ['image', 'video']:
            try:
                with Image.open(file_path) as img:
                    media_file.width = img.width
                    media_file.height = img.height
            except Exception as e:
                logger.warning(f"Could not extract image metadata: {e}")
        
        media_file.save()
