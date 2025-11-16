from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InterviewSimulatorViewSet, InterviewViewSet

app_name = 'interviews'

router = DefaultRouter()
router.register(r'simulator', InterviewSimulatorViewSet, basename='simulator')
router.register(r'templates', InterviewViewSet, basename='templates')

urlpatterns = [
    path('', include(router.urls)),
]

