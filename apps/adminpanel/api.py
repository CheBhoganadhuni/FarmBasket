from ninja import Router, Schema, Body
from uuid import UUID
from apps.catalog.models import Product
from apps.orders.models import Order
from apps.accounts.models import User
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser

router = Router(tags=['Admin'])
from .schemas import ProductCreateSchema, ProductUpdateSchema, OrderStatusSchema, PaymentStatusSchema

# Schemas are imported from schemas.py

# Products API
@router.get('/products')
def product_list(request):
    products = Product.objects.all()
    data = [ProductSerializer(product).data for product in products]
    return {'products': data}

@router.post('/products/create')
def product_create(request, data: ProductCreateSchema = Body(...)):
    import uuid
    try:
        category_id = uuid.UUID(data.category)
    except Exception:
        return {'success': False, 'message': 'Invalid category id'}

    product = Product(
        name=data.name,
        description=data.description,
        category_id=category_id,
        price=data.price,
        discount_price=data.discount_price,
        stock_quantity=data.stock_quantity,
        unit=data.unit,
        unit_value=data.unit_value,
        low_stock_threshold=data.low_stock_threshold or 10,
        is_active=data.is_active if data.is_active is not None else True,
        is_featured=data.is_featured if data.is_featured is not None else False,
        is_organic_certified=data.is_organic_certified if data.is_organic_certified is not None else True,
        featured_image=data.featured_image
    )
    product.save()
    return {'success': True, 'message': 'Product created', 'product_id': str(product.id)}

@router.put('/products/update/{pk}')
def product_update(request, pk: UUID, data: ProductUpdateSchema = Body(...)):
    product = get_object_or_404(Product, pk=pk)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(product, attr, value)
    product.save()
    return {'success': True, 'message': 'Product updated'}

@router.delete('/products/delete/{pk}')
def product_delete(request, pk: UUID):
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return {'success': True, 'message': 'Product deleted'}

# Orders API

@router.get('/orders')
def order_list(request):
    orders = Order.objects.all()
    order_data = []
    for order in orders:
        items = []
        for item in order.items.all():
            items.append({
                'id': str(item.id),
                'product_name': item.product_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price)
            })
        order_data.append({
            'id': str(order.id),
            'order_number': order.order_number,
            'user': {'name': order.user.name, 'email': order.user.email},
            'items_count': order.items.count(),
            'items': items,
            'total': float(order.total),
            'status': order.status,
            'payment_status': order.payment_status,
            'delivery_name': order.delivery_name,
            'delivery_address': order.delivery_address,
            'delivery_city': order.delivery_city,
            'delivery_state': order.delivery_state,
            'delivery_postal_code': order.delivery_postal_code,
            'delivery_phone': order.delivery_phone,
            'admin_notes': order.admin_notes,
            'created_at': order.created_at.isoformat(),
        })
    return {'orders': order_data}

# Order Status update
@router.put('/orders/{pk}/status')
def order_update_status(request, pk: UUID, data: OrderStatusSchema = Body(...)):
    order = get_object_or_404(Order, pk=pk)
    new_status = data.status
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return {'success': False, 'message': 'Invalid status'}
    if order.status == 'CANCELLED':
        return {'success': False, 'message': 'Cancelled orders cannot be changed'}
    order.status = new_status
    if new_status == 'CANCELLED':
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.orders_count = max(0, item.product.orders_count - 1)
                item.product.save()
        order.payment_status = 'REFUNDED'
    order.save()
    # email notification can be triggered here as before
    return {'success': True, 'message': f'Order status updated to {order.get_status_display()}'}

# Payment status update
@router.put('/orders/{pk}/payment_status')
def order_update_payment_status(request, pk: UUID, data: PaymentStatusSchema = Body(...)):
    order = get_object_or_404(Order, pk=pk)
    new_status = data.payment_status
    valid_payment_statuses = ['PENDING', 'PAID', 'FAILED', 'REFUNDED']
    if new_status not in valid_payment_statuses:
        return {'success': False, 'message': 'Invalid payment status'}
    if order.status == 'CANCELLED' and new_status != 'REFUNDED':
        return {'success': False, 'message': 'Payment status cannot be changed if order is cancelled'}
    order.payment_status = new_status
    order.save()
    return {'success': True, 'message': f'Payment status updated to {new_status}'}

# Users API

@router.get('/users')
def users_list(request):
    users = User.objects.all()
    users_data = [{'id': str(u.id), 'name': u.name, 'email': u.email} for u in users]
    return {'users': users_data}

@router.delete('/users/delete/{pk}')
def user_delete(request, pk: UUID):
    user = get_object_or_404(User, pk=pk)
    user.delete()
    return {'success': True, 'message': 'User deleted'}
