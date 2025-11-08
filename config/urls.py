from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .api import api 

urlpatterns = [
    # Django builtin admin interface
    path('django-admin/', admin.site.urls),

    # Your custom admin panel URLs
    path('admin/', include('apps.products.urls')),  # or whatever app you put your admin views in
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
