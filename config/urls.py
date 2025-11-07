from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .api import api  # ✅ Import ONCE

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', api.urls),  # ✅ Use ONCE
    
    # Template views
    path('', include('apps.accounts.urls')),
    path('', include('apps.catalog.urls')),
    path('', include('apps.cart.urls')),
    path('', include('apps.orders.urls')),  # ✅ Add this

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
