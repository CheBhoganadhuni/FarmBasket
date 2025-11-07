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


def order_detail_view(request, order_id):
    """Order detail page"""
    return render(request, 'orders/order_detail.html', {'order_id': order_id})
