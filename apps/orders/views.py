from django.shortcuts import render


def checkout_view(request):
    """Checkout page"""
    return render(request, 'orders/checkout.html')


def order_success_view(request, order_id):
    """Order success page"""
    return render(request, 'orders/order_success.html', {'order_id': order_id})


def order_history_view(request):
    """Order history page"""
    return render(request, 'orders/order_history.html')


from .models import Order

def order_detail_view(request, order_id):
    """Order detail page"""
    return render(request, 'orders/order_detail.html', {'order_id': order_id})


def track_order_view(request):
    """Public track order page"""
    order_id = request.GET.get('order_id')
    context = {}
    
    if order_id:
        try:
            order = Order.objects.get(order_number=order_id)
            context['order'] = order
            
            # Serialize for AlpineJS
            items = []
            for item in order.items.all():
                # Robust Image URL Logic
                image_url = None
                if item.product.featured_image:
                    try:
                        if hasattr(item.product.featured_image, 'url') and item.product.featured_image.url.startswith('http'):
                             image_url = item.product.featured_image.url
                        else:
                            raw_id = item.product.featured_image.name if hasattr(item.product.featured_image, 'name') else str(item.product.featured_image)
                            clean_id = raw_id.replace('/media/', '').lstrip('/')
                            import cloudinary.utils
                            image_url = cloudinary.utils.cloudinary_url(clean_id, secure=True, format="jpg")[0]
                    except Exception:
                        image_url = ''

                items.append({
                    'product_name': item.product.name,
                    'product_image': image_url,
                    'quantity': item.quantity,
                    'unit_price': str(item.unit_price),
                    'total_price': str(item.total_price),
                })
            
            context['order_json'] = {
                'order_number': order.order_number,
                'status': order.status,
                'status_display': order.get_status_display(),
                'payment_status': order.payment_status,
                'payment_status_display': order.get_payment_status_display(),
                'created_at': order.created_at.isoformat(),
                'total': str(order.total),
                'subtotal': str(order.subtotal),
                'delivery_charge': str(order.delivery_charge),
                'discount': str(order.discount),
                'delivery_name': order.delivery_name,
                'delivery_phone': order.delivery_phone,
                'delivery_address': order.delivery_address,
                'delivery_city': order.delivery_city,
                'delivery_state': order.delivery_state,
                'delivery_postal_code': order.delivery_postal_code,
                'delivery_landmark': order.delivery_landmark,
                'order_notes': order.order_notes,
                'items': items
            }
            
        except Order.DoesNotExist:
            context['error'] = f"Order #{order_id} not found. Please check your Order ID."
            
    return render(request, 'orders/track_order.html', context)
