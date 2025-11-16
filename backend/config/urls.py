"""
URL configuration for Modular Platform project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    # Root - redirect to API docs (useful during development)
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    # Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    
    # API Endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/modules/', include('apps.modules.urls')),
    path('api/billing/', include('apps.billing.urls')),
    path('api/cv-analysis/', include('apps.cv_analysis.urls')),
    path('api/interviews/', include('apps.interviews.urls')),
    path('api/integrations/', include('apps.integrations.urls')),
]

# Static and Media files (Development only)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
