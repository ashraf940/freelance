from django.contrib import admin
from .models import User, EmailVerificationToken, PasswordResetToken

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['email', 'role', 'email_verified', 'is_active', 'level']
    list_filter = ['role', 'email_verified', 'is_active']
    search_fields = ['email', 'username']
    
@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at']

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'created_at', 'is_used']