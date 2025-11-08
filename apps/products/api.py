from ninja import Router
from uuid import UUID
from django.shortcuts import get_object_or_404

from .admin_views import (
    admin_dashboard_stats,
    admin_products_list,
    admin_product_detail,
    admin_orders_list,
    admin_order_update_status,
    admin_users_list,
    admin_categories_list,
    admin_delete_user,
)
from .serializers import ProductSerializer
from apps.catalog.models import Product

router = Router(tags=['Admin'])

# Dashboard stats
@router.get('/dashboard/stats')
def dashboard_stats(request):
    return admin_dashboard_stats(request)

# Products
@router.get('/products')
def products_list(request):
    return admin_products_list(request)

@router.post('/products')
def products_create(request, data: dict):
    return admin_products_list(request)  # For POST in admin_products_list

@router.get('/products/{pk}')
def product_detail(request, pk: UUID):
    return admin_product_detail(request, pk)

@router.put('/products/{pk}')
def product_update(request, pk: UUID, data: dict):
    return admin_product_detail(request, pk)  # For PUT in admin_product_detail

@router.delete('/products/{pk}')
def product_delete(request, pk: UUID):
    return admin_product_detail(request, pk)  # For DELETE in admin_product_detail

# Orders
@router.get('/orders')
def orders_list(request):
    return admin_orders_list(request)

@router.put('/orders/{pk}/status')
def order_update_status(request, pk: UUID, data: dict):
    return admin_order_update_status(request, pk)

# Users
@router.get('/users')
def users_list(request):
    return admin_users_list(request)

# Categories
@router.get('/categories')
def categories_list(request):
    return admin_categories_list(request)

from uuid import UUID

@router.delete('/users/{pk}')
def delete_user(request, pk: UUID):
    return admin_delete_user(request, pk)
