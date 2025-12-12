from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static
from config.api import api

urlpatterns = [
    # Django builtin admin interface
    path('django-admin/', admin.site.urls),

    # Your custom admin panel URLs
    path('admin/', include('apps.products.urls')),
    
    # Ninja API
    path('api/', api.urls),
    
    # Template views
    path('', include('apps.accounts.urls')),
    path('', include('apps.catalog.urls')),
    path('', include('apps.cart.urls')),
    path('', include('apps.orders.urls')),
    path('contact/', TemplateView.as_view(template_name='legal/contact.html'), name='contact'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
