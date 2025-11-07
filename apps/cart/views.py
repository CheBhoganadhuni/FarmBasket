from django.shortcuts import render


def cart_view(request):
    """Shopping cart page"""
    return render(request, 'cart/cart.html')
