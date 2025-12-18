from typing import List
from django.shortcuts import get_object_or_404
from ninja import Router
from decimal import Decimal

from .models import Cart, CartItem
from apps.catalog.models import Product
from .schemas import (
    CartSchema, CartItemSchema, AddToCartSchema, 
    UpdateCartItemSchema, MessageSchema, SyncCartSchema
)
from apps.accounts.auth import AuthBearer

router = Router(tags=['Cart'])
auth = AuthBearer()


def get_or_create_cart(user):
    """Get or create cart for user"""
    cart, created = Cart.objects.get_or_create(user=user)
    return cart


@router.get("/", response=CartSchema, auth=auth)
def get_cart(request):
    """Get user's cart with all items"""
    cart = get_or_create_cart(request.auth)
    
    # Build response
    items_data = []
    subtotal = Decimal('0')
    
    for item in cart.items.select_related('product').all():
        if item.is_selected:
            subtotal += item.total_price
            
        items_data.append({
            'id': str(item.id),
            'product_id': str(item.product.id),
            'product_name': item.product.name,
            'product_slug': item.product.slug,
            'product_image': item.product.featured_image.url if item.product.featured_image else None,
            'unit_price': item.unit_price,
            'quantity': item.quantity,
            'total_price': item.total_price,
            'in_stock': item.product.in_stock,
            'available_quantity': item.product.stock_quantity,
            'is_selected': item.is_selected
        })
    
    return {
        'id': str(cart.id),
        'items': items_data,
        'items_count': cart.items_count,
        'subtotal': subtotal, # ✅ Only selected items
        'total': subtotal,
        'updated_at': cart.updated_at,
    }

@router.put("/select/{item_id}", response=MessageSchema, auth=auth)
def toggle_selection(request, item_id: str):
    """Toggle item selection"""
    cart = get_or_create_cart(request.auth)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    cart_item.is_selected = not cart_item.is_selected
    cart_item.save()
    
    # Recalculate subtotal for response context if needed, but client will likely refetch or calculate locally.
    return MessageSchema(message="Selection updated", success=True)

@router.put("/select-all", response=MessageSchema, auth=auth)
def select_all(request):
    """Select all items"""
    cart = get_or_create_cart(request.auth)
    cart.items.update(is_selected=True)
    return MessageSchema(message="All items selected", success=True)

@router.put("/deselect-all", response=MessageSchema, auth=auth)
def deselect_all(request):
    """Deselect all items"""
    cart = get_or_create_cart(request.auth)
    cart.items.update(is_selected=False)
    return MessageSchema(message="All items deselected", success=True)


@router.post("/add", response=MessageSchema, auth=auth)
def add_to_cart(request, data: AddToCartSchema):
    """Add item to cart or update quantity if already exists"""
    cart = get_or_create_cart(request.auth)
    product = get_object_or_404(Product, id=data.product_id, is_active=True)
    
    # Check stock
    if not product.in_stock:
        return MessageSchema(
            message=f"{product.name} is out of stock",
            success=False,
            cart_count=cart.items_count
        )
    
    # Get or create cart item
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'quantity': data.quantity}
    )
    
    if not created:
        # Item already in cart, update quantity
        new_quantity = cart_item.quantity + data.quantity
        if new_quantity > product.stock_quantity:
            return MessageSchema(
                message=f"Only {product.stock_quantity} items available",
                success=False,
                cart_count=cart.items_count
            )
        cart_item.quantity = new_quantity
        cart_item.save()
    
    return MessageSchema(
        message=f"Added {product.name} to cart",
        success=True,
        cart_count=cart.items_count
    )


@router.put("/update/{item_id}", response=MessageSchema, auth=auth)
def update_cart_item(request, item_id: str, data: UpdateCartItemSchema):
    """Update cart item quantity or remove if quantity is 0"""
    cart = get_or_create_cart(request.auth)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    if data.quantity == 0:
        # Remove item
        product_name = cart_item.product.name
        cart_item.delete()
        return MessageSchema(
            message=f"Removed {product_name} from cart",
            success=True,
            cart_count=cart.items_count
        )
    
    # Check stock
    if data.quantity > cart_item.product.stock_quantity:
        return MessageSchema(
            message=f"Only {cart_item.product.stock_quantity} items available",
            success=False,
            cart_count=cart.items_count
        )
    
    cart_item.quantity = data.quantity
    cart_item.save()
    
    return MessageSchema(
        message="Cart updated",
        success=True,
        cart_count=cart.items_count
    )


@router.delete("/remove/{item_id}", response=MessageSchema, auth=auth)
def remove_from_cart(request, item_id: str):
    """Remove item from cart"""
    cart = get_or_create_cart(request.auth)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    product_name = cart_item.product.name
    cart_item.delete()
    
    return MessageSchema(
        message=f"Removed {product_name} from cart",
        success=True,
        cart_count=cart.items_count
    )


@router.delete("/clear", response=MessageSchema, auth=auth)
def clear_cart(request):
    """Clear all items from cart"""
    cart = get_or_create_cart(request.auth)
    cart.items.all().delete()
    
    return MessageSchema(
        message="Cart cleared",
        success=True,
        cart_count=0
    )


@router.get("/count", response=dict, auth=auth)
def get_cart_count(request):
    """Get cart items count"""
    cart = get_or_create_cart(request.auth)
    return {"count": cart.items_count}


@router.post("/sync", response=MessageSchema, auth=auth)
def sync_cart(request, data: SyncCartSchema):
    """Sync guest cart with user cart"""
    cart = get_or_create_cart(request.auth)
    
    for item in data.items:
        try:
            product = Product.objects.get(id=item.product_id, is_active=True)
            if not product.in_stock:
                continue
                
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=product,
                defaults={'quantity': item.quantity, 'is_selected': item.is_selected}
            )
            
            if not created:
                # Add quantities
                new_qty = cart_item.quantity + item.quantity
                if new_qty > product.stock_quantity:
                    new_qty = product.stock_quantity
                
                cart_item.quantity = new_qty
                # Merge selection (guest state overrides if provided, otherwise OR)
                # But since we fixed frontend to send explicit state, we can trust item.is_selected
                cart_item.is_selected = item.is_selected
                cart_item.save()
                
        except Product.DoesNotExist:
            continue
            
    return MessageSchema(message="Cart synced", success=True, cart_count=cart.items_count)
