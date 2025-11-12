from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test

def superuser_required(view_func):
    return user_passes_test(lambda u: u.is_active and u.is_superuser)(view_func)

@superuser_required
def admin_dashboard(request):
    return render(request, 'admintemplates/dashboard.html')

@superuser_required
def admin_products(request):
    return render(request, 'admintemplates/products.html')

@superuser_required
def admin_orders(request):
    return render(request, 'admintemplates/orders.html')

@superuser_required
def admin_users(request):
    return render(request, 'admintemplates/users.html')
