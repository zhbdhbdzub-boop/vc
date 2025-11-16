"""
Module registry and licensing system.
"""
import uuid
from django.db import models
from apps.core.models import Tenant, TimestampedModel


class Module(TimestampedModel):
    """
    Represents a purchasable module in the marketplace.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='cube')
    
    # Pricing
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_annual = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_lifetime = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Trial
    trial_days = models.IntegerField(default=14)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Metadata
    version = models.CharField(max_length=50, default='1.0.0')
    category = models.CharField(max_length=100)
    tags = models.JSONField(default=list, blank=True)
    features = models.JSONField(default=list, blank=True)
    requirements = models.JSONField(default=list, blank=True)
    
    # Documentation
    documentation_url = models.URLField(blank=True)
    demo_url = models.URLField(blank=True)
    
    class Meta:
        db_table = 'modules'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class ModuleLicense(TimestampedModel):
    """
    Tracks which modules a tenant has access to.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='licenses')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='licenses')
    
    # License type
    license_type = models.CharField(
        max_length=50,
        choices=[
            ('trial', 'Trial'),
            ('monthly', 'Monthly Subscription'),
            ('annual', 'Annual Subscription'),
            ('lifetime', 'Lifetime'),
        ]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    activated_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Limits
    usage_limit = models.IntegerField(null=True, blank=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'module_licenses'
        unique_together = ['tenant', 'module']
    
    def __str__(self):
        return f"{self.tenant.name} - {self.module.name}"
    
    @property
    def is_expired(self):
        """Check if license has expired."""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_trial(self):
        """Check if this is a trial license."""
        return self.license_type == 'trial'
