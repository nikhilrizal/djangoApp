from django.contrib import admin

from .models import (
    Profile,
    UserFile,
)

admin.site.site_header = "Text To Interface Admin"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "phone")
    search_fields = ("user__email", "phone")
    list_filter = ("phone",)


@admin.register(UserFile)
class UserFileAdmin(admin.ModelAdmin):
    list_display = ["user", "status", "document_type"]
    search_fields = ["user__username", "user__email", "status", "document_type"]
    list_filter = ["status", "document_type"]