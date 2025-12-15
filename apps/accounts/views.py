from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib import messages


from apps.catalog.models import Product
from apps.accounts.models import User
# Try importing Order, handle if missing
try:
    from apps.orders.models import Order
except ImportError:
    Order = None

def home_view(request):
    """Homepage"""
    product_count = Product.objects.filter(is_active=True).count()
    user_count = User.objects.count()
    order_count = Order.objects.count() if Order else 0
    
    context = {
        'product_count': product_count,
        'user_count': user_count,
        'order_count': order_count
    }
    return render(request, 'home.html', context)

def register_view(request):
    """User registration page"""
    return render(request, 'auth/register.html')


def login_view(request):
    """User login page"""
    return render(request, 'auth/login.html')


def logout_view(request):
    """Logout user"""
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('accounts:login')


def profile_view(request):
    """User profile page - JWT auth handled by JavaScript"""
    return render(request, 'auth/profile.html')


def profile_edit_view(request):
    """Edit profile page - JWT auth handled by JavaScript"""
    return render(request, 'auth/profile_edit.html')


def password_reset_request_view(request):
    """Password reset request page"""
    return render(request, 'auth/password_reset_request.html')


def password_reset_confirm_view(request):
    """Password reset confirmation page"""
    token = request.GET.get('token')
    return render(request, 'auth/password_reset_confirm.html', {'token': token})


def addresses_view(request):
    """Address management page - JWT auth handled by JavaScript"""
    return render(request, 'auth/addresses.html')


def terms_of_service(request):
    """Terms of Service page"""
    return render(request, 'legal/terms.html')


def privacy_policy(request):
    """Privacy Policy page"""
    return render(request, 'legal/privacy.html')

def wishlist_view(request):
    """Wishlist page"""
    return render(request, 'accounts/wishlist.html')

def contact_view(request):
    """contact page"""
    return render(request, 'legal/contact.html')

def google_success_view(request):
    """Intermediate page for Google Auth token exchange"""
    return render(request, 'auth/google_success.html')
    