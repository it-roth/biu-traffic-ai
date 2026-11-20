"""
Root URL configuration for BIU Traffic AI.
"""
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.http import JsonResponse

def root_status(request):
    return JsonResponse({
        'system': 'BIU Traffic AI — BELTEI International University',
        'status': 'OPERATIONAL',
        'version': '2.0.0',
        'enforcement': 'Cambodia Sub-Decree No. 39 Articles 8 & 44',
        'endpoints': {
            'admin': '/admin/',
            'auth_login': '/api/auth/login/',
            'auth_refresh': '/api/auth/token/refresh/',
            'scan_image': '/api/scan/image/',
            'scan_video': '/api/scan/video/',
            'violations': '/api/violations/',
            'live_stats': '/api/traffic/stats/',
            'live_stream': '/api/traffic/stream/',
        }
    })

urlpatterns = [
    path('', root_status, name='root-status'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')), 
    path('api/auth/', include('accounts.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
