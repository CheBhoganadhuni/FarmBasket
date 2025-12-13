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
    path('privacy-policy/', TemplateView.as_view(template_name='legal/privacy.html'), name='privacy_policy'),
    path('terms-conditions/', TemplateView.as_view(template_name='legal/terms.html'), name='terms_conditions'),
    path('shipping-policy/', TemplateView.as_view(template_name='legal/shipping_policy.html'), name='shipping_policy'),
    path('cancellation-refund/', TemplateView.as_view(template_name='legal/cancellation_refund.html'), name='cancellation_refund'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
