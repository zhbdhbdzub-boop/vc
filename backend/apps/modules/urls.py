"""
URL configuration for modules app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'marketplace', views.ModuleViewSet, basename='marketplace')
router.register(r'my-modules', views.MyModulesViewSet, basename='my-modules')

app_name = 'modules'

urlpatterns = [
    path('', include(router.urls)),
]
