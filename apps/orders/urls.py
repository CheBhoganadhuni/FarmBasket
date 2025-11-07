from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('order/success/<str:order_id>/', views.order_success_view, name='order_success'),
    path('orders/', views.order_history_view, name='order_history'),
    path('orders/<str:order_id>/', views.order_detail_view, name='order_detail'),
]
