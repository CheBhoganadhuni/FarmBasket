from django.urls import path
from django.shortcuts import redirect

from .admin_views import (
    admin_dashboard_stats,
    admin_products_list,
    admin_product_detail,
    admin_orders_list,
    admin_order_update_status,
    admin_users_list,
    admin_categories_list,
    admin_payment_update_status,
)

from .views import (
    admin_dashboard,
    admin_products,
    admin_orders,
    admin_users,
)

from .api import admin_product_create, admin_product_update

urlpatterns = [
    # Redirect root 'admin/' to 'admin/dashboard/'
    path('', lambda request: redirect('admin_dashboard'), name='admin_root_redirect'),

    # Admin API Endpoints
    path('api/dashboard/stats', admin_dashboard_stats, name='admin_dashboard_stats'),
    path('api/products', admin_products_list, name='admin_products_list'),
    path('api/products/<uuid:pk>', admin_product_detail, name='admin_product_detail'),
    path('api/products/create', admin_product_create, name='admin_product_create'),
    path('api/products/update/<uuid:pk>', admin_product_update, name='admin_product_update'),


    path('api/orders', admin_orders_list, name='admin_orders_list'),
    path('api/orders/<uuid:pk>/status', admin_order_update_status, name='admin_order_update_status'),
    path('api/orders/<uuid:pk>/payment_status', admin_payment_update_status, name='admin_payment_update_status'),

    path('api/users', admin_users_list, name='admin_users_list'),
    path('api/categories', admin_categories_list, name='admin_categories_list'),

    # Admin Pages
    path('dashboard/', admin_dashboard, name='admin_dashboard'),
    path('products/', admin_products, name='admin_products'),
    path('orders/', admin_orders, name='admin_orders'),
    path('users/', admin_users, name='admin_users'),
]
