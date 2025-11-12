from django.urls import path
from . import views
from django.shortcuts import redirect

urlpatterns = [
    path('', lambda request: redirect('admin_dashboard'), name='admin_root_redirect'),  # redirect /admin/ to dashboard

    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('products/', views.admin_products, name='admin_products'),
    path('orders/', views.admin_orders, name='admin_orders'),
    path('users/', views.admin_users, name='admin_users'),
    
]
