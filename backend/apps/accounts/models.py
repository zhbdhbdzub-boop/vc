"""
User model and authentication.
"""
import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from apps.core.models import Tenant, TimestampedModel


class User(AbstractUser, TimestampedModel):
    """
    Custom user model with tenant relationship.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    
    # Tenant relationship
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )
    
    # Profile fields
    phone = models.CharField(max_length=50, blank=True)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True)
    bio = models.TextField(blank=True)
    
    # Role within tenant
    role = models.CharField(
        max_length=50,
        choices=[
            ('owner', 'Owner'),
            ('admin', 'Admin'),
            ('member', 'Member'),
            ('viewer', 'Viewer'),
        ],
        default='member'
    )
    
    # Settings
    preferences = models.JSONField(default=dict, blank=True)
    
    # Status
    is_verified = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        """Return full name or email."""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.email
    
    def has_module_access(self, module_code):
        """Check if user has access to a specific module."""
        if not self.tenant:
            return False
        return self.tenant.licenses.filter(
            module__code=module_code,
            is_active=True
        ).exists()


class UserInvitation(TimestampedModel):
    """
    Model for inviting users to a tenant.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    role = models.CharField(max_length=50, default='member')
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_invitations')
    token = models.CharField(max_length=255, unique=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        db_table = 'user_invitations'
        unique_together = ['tenant', 'email']
    
    def __str__(self):
        return f"Invitation for {self.email} to {self.tenant.name}"
    
    @property
    def is_expired(self):
        """Check if invitation has expired."""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    @property
    def is_accepted(self):
        """Check if invitation was accepted."""
        return self.accepted_at is not None
