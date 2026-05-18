from django.contrib import admin
from .models import AdminLog, PlatformSettings, Announcement, WithdrawalRequest

@admin.register(AdminLog)
class AdminLogAdmin(admin.ModelAdmin):
    list_display = ['admin', 'action', 'model_name', 'object_name', 'created_at']
    list_filter = ['action', 'model_name', 'created_at']
    search_fields = ['admin__email', 'object_name']
    readonly_fields = ['id', 'created_at']

@admin.register(PlatformSettings)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ['site_name', 'commission_rate', 'min_withdrawal', 'maintenance_mode']

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'announcement_type', 'is_active', 'created_at']
    list_filter = ['announcement_type', 'is_active']

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'status', 'created_at']
    list_filter = ['status']