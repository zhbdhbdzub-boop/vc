from django.contrib import admin
from .models import Module, ModuleLicense


@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'category', 'is_active', 'is_featured', 'version']
    list_filter = ['is_active', 'is_featured', 'category']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']


@admin.register(ModuleLicense)
class ModuleLicenseAdmin(admin.ModelAdmin):
    list_display = ['tenant', 'module', 'license_type', 'is_active', 'activated_at', 'expires_at']
    list_filter = ['license_type', 'is_active']
    search_fields = ['tenant__name', 'module__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
