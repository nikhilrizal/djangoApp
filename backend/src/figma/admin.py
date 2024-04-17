from django.contrib import admin
from .models import UserApiInteractionHistory, Service

@admin.register(UserApiInteractionHistory)
class HistoryAdmin(admin.ModelAdmin):
    list_display = ["user", "user_prompt", "api_service"]
    search_fields = ["user__email"]
    list_filter = ["api_service"]
    fieldsets = (
        ('Prompt', {'fields': ('user_prompt',)}),
        ('Response', {'fields': ('api_output',)}),
        ('Service Name', {'fields': ('api_service',)}),
         ('Service used by', {'fields': ('user',)}),
    )

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ["user", "service_name", "is_service_active"]
    search_fields = ["service_name"]
    list_filter = ["is_service_active"]
    fieldsets = (
        ('Name of the service', {'fields': ('service_name',)}),
        ('Current Status', {'fields': ('is_service_active',)}),
        ('Saved By', {'fields': ('user',)}),
    )
