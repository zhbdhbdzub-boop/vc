"""
Tenant middleware to inject tenant context into requests.
"""
from django.utils.deprecation import MiddlewareMixin
from apps.core.models import Tenant


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware to set the current tenant on the request object.
    Tenant is determined from the user's profile.
    """
    
    def process_request(self, request):
        """Add tenant to request if user is authenticated."""
        request.tenant = None
        
        if request.user.is_authenticated:
            try:
                request.tenant = request.user.tenant
            except AttributeError:
                pass
        
        return None
