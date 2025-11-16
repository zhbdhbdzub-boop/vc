"""
Serializers for modules.
"""
from rest_framework import serializers
from .models import Module, ModuleLicense


class ModuleSerializer(serializers.ModelSerializer):
    """Serializer for Module model."""
    
    has_access = serializers.SerializerMethodField()
    
    class Meta:
        model = Module
        fields = [
            'id', 'code', 'name', 'description', 'icon',
            'price_monthly', 'price_annual', 'price_lifetime',
            'trial_days', 'is_active', 'is_featured',
            'version', 'category', 'tags', 'features', 'requirements',
            'documentation_url', 'demo_url', 'created_at', 'has_access'
        ]
    
    def get_has_access(self, obj):
        """Check if current user has access to this module"""
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return False
        return request.user.has_module_access(obj.code)


class ModuleLicenseSerializer(serializers.ModelSerializer):
    """Serializer for Module License."""
    module = ModuleSerializer(read_only=True)
    days_remaining = serializers.SerializerMethodField()
    
    class Meta:
        model = ModuleLicense
        fields = [
            'id', 'module', 'license_type', 'is_active',
            'activated_at', 'expires_at', 'usage_limit',
            'usage_count', 'is_expired', 'is_trial', 'days_remaining'
        ]
    
    def get_days_remaining(self, obj):
        """Calculate days remaining until expiration"""
        if not obj.expires_at:
            return None
        
        from django.utils import timezone
        delta = obj.expires_at - timezone.now()
        return max(0, delta.days)


class ModulePurchaseSerializer(serializers.Serializer):
    """Serializer for module purchase requests"""
    
    license_type = serializers.ChoiceField(
        choices=['trial', 'monthly', 'annual', 'lifetime']
    )
    payment_method_id = serializers.CharField(required=False, allow_blank=True)
    
    def validate(self, data):
        """Validate purchase request"""
        # If not trial, payment method is required
        if data['license_type'] != 'trial':
            if not data.get('payment_method_id'):
                raise serializers.ValidationError({
                    'payment_method_id': 'Payment method is required for paid licenses'
                })
        
        return data
