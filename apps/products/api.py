from ninja import Router, Schema, Body
from uuid import UUID
from .admin_views import (
    admin_dashboard_stats,
    admin_products_list,
    admin_product_detail,
    admin_orders_list,
    admin_order_update_status,
    admin_users_list,
    admin_categories_list,
    admin_delete_user,
    admin_payment_update_status
)

from apps.catalog.models import Product


from django.shortcuts import get_object_or_404

from .schemas import ProductCreateUpdateSchema, ProductCreateSchema, ProductUpdateSchema

class PaymentStatusSchema(Schema):
    payment_status: str

class OrderStatusUpdateSchema(Schema):
    status: str

# from ninja.security import HttpBearer
# from django.contrib.auth.models import User

# class AuthBearer(HttpBearer):
    # def authenticate(self, request, token):
        # from rest_framework_simplejwt.tokens import AccessToken
        # try:
            # validated = AccessToken(token)
            # user = User.objects.get(id=validated['user_id'])
            # if not user.is_superuser:  # restrict to admins
                # return None
            # request.user = user
            # return user
        # except Exception:
            # return None

# auth = AuthBearer()
# router = Router(tags=['Admin'], auth=auth)
router = Router(tags=['Admin'])

# Dashboard stats
@router.get('/dashboard/stats')
def dashboard_stats(request):
    return admin_dashboard_stats(request)

# Products
@router.get('/products')
def products_list(request):
    return admin_products_list(request)

@router.post('/products/create')
def admin_product_create(request, data: ProductCreateSchema = Body(...)):
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
        low_stock_threshold=data.low_stock_threshold if data.low_stock_threshold else 10,
        is_active=data.is_active if data.is_active is not None else True,
        is_featured=data.is_featured if data.is_featured is not None else False,
        is_organic_certified=data.is_organic_certified if data.is_organic_certified is not None else True,
        featured_image=data.featured_image
    )
    product.save()
    
    return {'success': True, 'message': 'Product created successfully', 'product_id': str(product.id)}




# @router.post('/products')
# def products_create(request, data: ProductCreateUpdateSchema = Body(...)):
    # drf_response = admin_products_list(request, data.dict())
    # # drf_response is DRF Response object. Extract .data and return dict to Ninja.
    # return drf_response.data

@router.get('/products/{pk}')
def product_detail(request, pk: UUID):
    return admin_product_detail(request, pk)

from apps.catalog.models import Category

@router.put('/products/update/{pk}')
def admin_product_update(request, pk: UUID, data: ProductUpdateSchema = Body(...)):
    import uuid
    from apps.catalog.models import Product

    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return {'success': False, 'message': 'Product not found'}
    
    data_dict = data.dict(exclude_unset=True)

    if 'category' in data_dict:
        category_id_str = data_dict.pop('category')
        try:
            category_obj = Category.objects.get(id=category_id_str)
            product.category = category_obj
        except Category.DoesNotExist:
            return {'success': False, 'message': 'Invalid category id'}
    
    # Assign other fields
    for attr, value in data_dict.items():
        setattr(product, attr, value)

    product.save()

    return {'success': True, 'message': 'Product updated successfully', 'product_id': str(product.id)}

# @router.put('/products/{pk}')
# def product_update(request, pk: UUID, data: ProductCreateUpdateSchema = Body(...)):
    # return admin_product_detail(request, pk, data.dict())

@router.delete('/products/{pk}')
def product_delete(request, pk: UUID):
    from apps.catalog.models import Product
    product = get_object_or_404(Product, pk=pk)
    product.delete()
    return {'success': True, 'message': 'Product deleted'}

# Orders
@router.get('/orders')
def orders_list(request):
    return admin_orders_list(request)

from ninja.responses import Response as NinjaResponse

@router.put('/orders/{pk}/status')
def order_update_status(request, pk: UUID, data: OrderStatusUpdateSchema = Body(...)):
    drf_response = admin_order_update_status(request, pk, data.dict())
    # Convert DRF Response -> Ninja compatible
    return NinjaResponse(drf_response.data, status=drf_response.status_code)


@router.put('/orders/{pk}/payment_status')
def order_update_payment_status(request, pk: UUID, data: PaymentStatusSchema = Body(...)):
    drf_response = admin_payment_update_status(request, pk, data.dict())
    return NinjaResponse(drf_response.data, status=drf_response.status_code)


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
