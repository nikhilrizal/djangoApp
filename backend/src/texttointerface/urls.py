from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi



schema_view = get_schema_view(
    openapi.Info(
        title="Text to Interface API",
        default_version="v1",
        description="Text to Interface API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="zuraiz@bluebrick.ai"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("core.urls")),
    path("api/figma/", include("figma.urls")),
     path(
        "swagger<format>/", schema_view.without_ui(cache_timeout=0), name="schema-json"
    ),
    path(
        "swagger/",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    path("redoc/", schema_view.with_ui("redoc", cache_timeout=0), name="schema-redoc"),
]+static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)