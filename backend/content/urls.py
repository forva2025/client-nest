from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PostViewSet, ScheduleViewSet

router = DefaultRouter()
router.register(r'posts', PostViewSet, basename='post')
router.register(r'schedules', ScheduleViewSet, basename='schedule')

urlpatterns = [
    path('', include(router.urls)),
] 