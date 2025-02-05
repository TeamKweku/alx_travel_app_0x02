from django.contrib import admin
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# Schema view configuration for Swagger
schema_view = get_schema_view(
    openapi.Info(
        title="ALX Travel App API",
        default_version='v1',
        description="API for managing property listings, bookings, and payments",
        terms_of_service="https://www.alxtravelapp.com/terms/",
        contact=openapi.Contact(email="contact@alxtravelapp.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('alx_travel_app.listings.urls')),
    path('api-auth/', include('rest_framework.urls')),
    
    # Swagger URLs
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
