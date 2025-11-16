"""
Custom permissions for module-based access control.
"""
from rest_framework import permissions


class HasModuleAccess(permissions.BasePermission):
    """
    Permission class to check if user has access to a specific module.
    Usage: Add module_code as a class attribute to the view.
    """
    message = "You don't have access to this module. Please purchase it from the marketplace."
    
    def has_permission(self, request, view):
        """Check if user has module access."""
        if not request.user.is_authenticated:
            return False
        
        # Superusers have access to everything
        if request.user.is_superuser:
            return True
        
        # Get module code from view
        module_code = getattr(view, 'module_code', None)
        if not module_code:
            # If no module code specified, allow access
            return True
        
        # Check if user's tenant has an active license for this module
        if not request.user.tenant:
            return False
        
        return request.user.has_module_access(module_code)


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permission for tenant owners and admins only.
    """
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        
        return request.user.role in ['owner', 'admin']
