from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserInvitation


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'full_name', 'tenant', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'is_verified', 'tenant']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    readonly_fields = ['id', 'created_at', 'updated_at', 'last_login']
    
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar', 'bio')}),
        ('Organization', {'fields': ('tenant', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at')}),
        ('Settings', {'fields': ('preferences',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2', 'tenant', 'role'),
        }),
    )


@admin.register(UserInvitation)
class UserInvitationAdmin(admin.ModelAdmin):
    list_display = ['email', 'tenant', 'role', 'invited_by', 'is_accepted', 'is_expired', 'created_at']
    list_filter = ['role', 'tenant']
    search_fields = ['email', 'tenant__name']
    readonly_fields = ['id', 'token', 'created_at', 'updated_at']
