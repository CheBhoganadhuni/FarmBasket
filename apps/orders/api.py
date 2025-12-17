from typing import List
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.utils import timezone
from ninja import Router
import razorpay
import hmac
import hashlib

from decimal import Decimal


from .models import Order, OrderItem
from apps.cart.models import Cart
from apps.accounts.models import Address
from .schemas import (
    CreateOrderSchema, OrderSchema, OrderSummarySchema,
    RazorpayOrderSchema, VerifyPaymentSchema, MessageSchema
)




from apps.accounts.auth import AuthBearer

router = Router(tags=['Orders'])
auth = AuthBearer()

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)


from apps.notifications.email import send_order_confirmation_email

@router.post("/checkout/create", response=dict, auth=auth)
def create_order(request, data: CreateOrderSchema):
    """Create order from cart"""
    user = request.auth
    
    # Get user's cart
    try:
        cart = Cart.objects.get(user=user)
    except Cart.DoesNotExist:
        return {"success": False, "message": "Cart is empty"}
    
    if cart.items.count() == 0:
        return {"success": False, "message": "Cart is empty"}
    
    # ✅ Filter items based on persistent selection
    items = cart.items.filter(is_selected=True)
    
    if items.count() == 0:
        return {"success": False, "message": "No items selected for checkout"}

    # Validate stock for all items
    for cart_item in items:
        if not cart_item.product.in_stock:
            return {
                "success": False,
                "message": f"{cart_item.product.name} is out of stock"
            }
        if cart_item.quantity > cart_item.product.stock_quantity:
            return {
                "success": False,
                "message": f"Only {cart_item.product.stock_quantity} units of {cart_item.product.name} available"
            }
    
    # Calculate pricing manually for partial checkout
    subtotal = sum(item.total_price for item in items)
    delivery_charge = 0 if subtotal >= 500 else 40  # Free delivery above ₹500
    grand_total = subtotal + delivery_charge
    
    wallet_amount = Decimal('0')
    payable_amount = grand_total
    
    # Wallet Logic
    if data.use_wallet and user.wallet_balance > 0:
        if user.wallet_balance >= grand_total:
             # Full payment via wallet
             wallet_amount = grand_total - 1 
             if wallet_amount < 0: wallet_amount = 0
             payable_amount = payload_adj = 1 # Keep 1 for razorpay tests if needed
             # IF COD + Wallet -> payable might be 0. 
             # Logic below handles payable_amount for Razorpay.
             # For now, keeping logic consistent with existing block:
             payable_amount = 1
        else:
             wallet_amount = user.wallet_balance
             payable_amount = grand_total - wallet_amount
    
    total = grand_total # Save the TRUE total
    
    # Create order
    order = Order.objects.create(
        user=user,
        status='PENDING',
        delivery_name=data.delivery_address.name,
        delivery_phone=data.delivery_address.phone,
        delivery_address=data.delivery_address.address,
        delivery_city=data.delivery_address.city,
        delivery_state=data.delivery_address.state,
        delivery_postal_code=data.delivery_address.postal_code,
        delivery_landmark=data.delivery_address.landmark,
        subtotal=subtotal,
        delivery_charge=delivery_charge,
        discount=0, 
        wallet_amount=wallet_amount, 
        total=total, 
        payment_method=data.payment_method,
        order_notes=data.order_notes
    )
    
    # Create order items from filtered items
    for cart_item in items:
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            product_name=cart_item.product.name,
            product_image=cart_item.product.featured_image.url if cart_item.product.featured_image else '',
            unit_price=cart_item.unit_price,
            quantity=cart_item.quantity
        )
    
    # If Razorpay payment, create Razorpay order
    if data.payment_method == 'RAZORPAY':
        try:
            # Amount in paise (₹1 = 100 paise)
            # Use calculated payable_amount (which is grand_total - wallet_amount)
            # Use local variable 'payable_amount' from above
            amount_in_paise = int(payable_amount * 100)
            
            razorpay_order = razorpay_client.order.create({
                'amount': amount_in_paise,
                'currency': 'INR',
                'receipt': order.order_number,
                'notes': {
                    'order_id': str(order.id),
                    'user_email': user.email,
                    'use_wallet': str(data.use_wallet),
                    'subtotal': str(subtotal),
                    'delivery_charge': str(delivery_charge)
                }
            })
            
            order.razorpay_order_id = razorpay_order['id']
            # order.save()
            
            
            
            return {
                "success": True,
                "message": "Order created successfully",
                "order_id": str(order.id),
                "payment_required": True,
                "razorpay_data": {
                    "razorpay_order_id": razorpay_order['id'],
                    "amount": amount_in_paise,
                    "currency": "INR",
                    "key_id": settings.RAZORPAY_KEY_ID,
                    "order_number": order.order_number,
                    "customer_name": data.delivery_address.name,
                    "customer_email": user.email,
                    "customer_phone": data.delivery_address.phone
                }
            }
            
        except Exception as e:
            order.delete()
            return {
                "success": False,
                "message": f"Payment gateway error: {str(e)}"
            }
    
    else:  # COD
        order.status = 'CONFIRMED'
        order.save()
        
        if data.use_wallet:
            # Check balance and deduct
            max_deductable = max(0, subtotal + delivery_charge + 1)
            wallet_deduction = min(user.wallet_balance, max_deductable)
            
            if wallet_deduction > 0:
                user.debit_wallet(wallet_deduction)
        
        # Clear selected items from cart
        items.delete()
        
        # Reduce stock
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity -= item.quantity
                item.product.orders_count += 1
                item.product.save()
        
        # ✅ Send order confirmation email
        try:
            if user.email_notifications:  # Check user preference
                send_order_confirmation_email(order)
        except Exception as e:
            print(f"Failed to send order confirmation email: {e}")
        
        return {
            "success": True,
            "message": "Order placed successfully",
            "order_id": str(order.id),
            "payment_required": False
        }

@router.post("/payment/verify", response=MessageSchema, auth=auth)
def verify_payment(request, data: VerifyPaymentSchema):
    """Verify Razorpay payment"""
    user = request.auth
    
    try:
        order = Order.objects.get(id=data.order_id, user=user)
    except Order.DoesNotExist:
        return MessageSchema(
            success=False,
            message="Order not found"
        )
    
    # Verify signature
    try:
        params_dict = {
            'razorpay_order_id': data.razorpay_order_id,
            'razorpay_payment_id': data.razorpay_payment_id,
            'razorpay_signature': data.razorpay_signature
        }
        
        razorpay_client.utility.verify_payment_signature(params_dict)
        
        # Fetch razorpay order details for notes
        razorpay_order_info = razorpay_client.order.fetch(data.razorpay_order_id)
        notes = razorpay_order_info.get('notes', {})
        use_wallet = notes.get('use_wallet', 'False') == 'True'
        subtotal = float(notes.get('subtotal', 0))
        delivery_charge = float(notes.get('delivery_charge', 0))
        
        # Payment verified!
        order.payment_status = 'PAID'
        order.status = 'CONFIRMED'
        order.razorpay_payment_id = data.razorpay_payment_id
        order.razorpay_signature = data.razorpay_signature
        order.paid_at = timezone.now()
        order.save()
        
        if use_wallet:
            # Check balance and deduct
            max_deductable = max(0, subtotal + delivery_charge + 1)
            wallet_deduction = min(user.wallet_balance, max_deductable)
            
            if wallet_deduction > 0:
                user.debit_wallet(wallet_deduction)
        
        # Remove purchased items from cart
        try:
            cart = Cart.objects.get(user=user)
            # Find and delete items that match the order items
            for order_item in order.items.all():
                if order_item.product:
                    cart.items.filter(product=order_item.product).delete()
        except Cart.DoesNotExist:
            pass
        
        # Reduce stock
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity -= item.quantity
                item.product.orders_count += 1
                item.product.save()
        
        # ✅ Send order confirmation email
        try:
            if user.email_notifications:  # Check user preference
                send_order_confirmation_email(order)
        except Exception as e:
            print(f"Failed to send order confirmation email: {e}")
        
        return MessageSchema(
            success=True,
            message="Payment verified successfully",
            order_id=str(order.id)
        )
        
    except razorpay.errors.SignatureVerificationError:
        order.payment_status = 'FAILED'
        # order.save()
        
        return MessageSchema(
            success=False,
            message="Payment verification failed"
        )

@router.get("/orders", response=List[OrderSummarySchema], auth=auth)
def get_user_orders(request):
    """Get all orders for logged-in user"""
    orders = Order.objects.filter(user=request.auth).prefetch_related('items')
    
    result = []
    for order in orders:
        result.append({
            'id': str(order.id),
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display(),
            'payment_status': order.payment_status,
            'total': order.total,
            'items_count': order.items.count(),
            'created_at': order.created_at
        })
    
    return result


@router.get("/orders/{order_id}", response=OrderSchema, auth=auth)
def get_order_detail(request, order_id: str):
    """Get order details"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items'),
        id=order_id,
        user=request.auth
    )
    
    # Build response
    items_data = []
    for item in order.items.all():
        items_data.append({
            'id': str(item.id),
            'product_id': str(item.product.id) if item.product else None,
            'product_slug': item.product.slug if item.product else None,
            'product_name': item.product_name,
            'product_image': item.product_image,
            'unit_price': item.unit_price,
            'quantity': item.quantity,
            'total_price': item.total_price
        })
    
    return {
        'id': str(order.id),
        'order_number': order.order_number,
        'status': order.status,
        'status_display': order.get_status_display(),
        'delivery_name': order.delivery_name,
        'delivery_phone': order.delivery_phone,
        'delivery_address': order.delivery_address,
        'delivery_city': order.delivery_city,
        'delivery_state': order.delivery_state,
        'delivery_postal_code': order.delivery_postal_code,
        'delivery_landmark': order.delivery_landmark,
        'subtotal': order.subtotal,
        'delivery_charge': order.delivery_charge,
        'discount': order.discount,
        'total': order.total,
        'payment_method': order.payment_method,
        'payment_status': order.payment_status,
        'payment_status_display': order.get_payment_status_display(),
        'order_notes': order.order_notes,
        'items': items_data,
        'created_at': order.created_at,
        'updated_at': order.updated_at
    }


from apps.notifications.email import send_admin_cancellation_email

@router.post("/orders/{order_id}/cancel", response=dict, auth=auth)
def cancel_order(request, order_id: str):
    """Cancel order if eligible"""
    order = get_object_or_404(Order, id=order_id, user=request.auth)
    
    # Check eligibility
    if order.status not in ['PENDING', 'PROCESSING', 'CONFIRMED']:
        return {
            "success": False,
            "message": "Order cannot be cancelled at this stage."
        }
    
    # Update Status
    order.status = 'CANCELLED'
    order.save()
    
    # Send Admin Email
    try:
        send_admin_cancellation_email(order, settings.SITE_URL)
        
        # ✅ Send Status Update Email to User
        from apps.notifications.email import send_order_status_email
        send_order_status_email(order)
        
    except Exception as e:
        print(f"Failed to send cancellation emails: {e}")
        
    return {
        "success": True,
        "message": "Order cancelled successfully. If paid, refund will be processed to source/wallet."
    }
