
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def admin_dashboard(request):
    return render(request, 'admin/dashboard.html')

@staff_member_required
def admin_products(request):
    return render(request, 'admin/products.html')

@staff_member_required
def admin_orders(request):
    return render(request, 'admin/orders.html')

@staff_member_required
def admin_users(request):
    return render(request, 'admin/users.html')
