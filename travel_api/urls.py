from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def api_root(request):
    return Response({
        'message': 'Torrey Travels API',
        'version': 'v1',
        'endpoints': {
            'auth': '/api/auth/',
            'flights': '/api/flights/',
            'hotels': '/api/hotels/',
            'packages': '/api/packages/',
            'docs': '/swagger/',
        }
    })

schema_view = get_schema_view(
   openapi.Info(
      title="Torrey Travels API",
      default_version='v1',
      description="Complete Travel Booking Platform API",
      contact=openapi.Contact(email="support@torreytravels.com"),
      license=openapi.License(name="MIT License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api_root, name='api-root'),
    path('api/auth/', include('accounts.urls')),
    path('api/flights/', include('flights.urls')),
    path('api/hotels/', include('hotels.urls')),
    path('api/packages/', include('packages.urls')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)