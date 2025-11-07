from django.contrib import admin
from django.utils.html import format_html
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product_name', 'unit_price', 'quantity', 'total_price']
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status_badge', 'payment_status_badge',
        'payment_method', 'total', 'created_at'
    ]
    list_filter = ['status', 'payment_status', 'payment_method', 'created_at']
    search_fields = ['order_number', 'user__email', 'delivery_phone']
    readonly_fields = [
        'order_number', 'razorpay_order_id', 'razorpay_payment_id',
        'razorpay_signature', 'created_at', 'updated_at', 'paid_at'
    ]
    
    inlines = [OrderItemInline]
    
    fieldsets = (
        ('Order Information', {
            'fields': ('order_number', 'user', 'status', 'order_notes', 'admin_notes')
        }),
        ('Delivery Address', {
            'fields': (
                'delivery_name', 'delivery_phone', 'delivery_address',
                'delivery_city', 'delivery_state', 'delivery_postal_code', 'delivery_landmark'
            )
        }),
        ('Pricing', {
            'fields': ('subtotal', 'delivery_charge', 'discount', 'total')
        }),
        ('Payment', {
            'fields': (
                'payment_method', 'payment_status',
                'razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature'
            )
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'paid_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'PROCESSING': 'blue',
            'CONFIRMED': 'green',
            'SHIPPED': 'purple',
            'OUT_FOR_DELIVERY': 'teal',
            'DELIVERED': 'green',
            'CANCELLED': 'red',
            'REFUNDED': 'gray',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'gray'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def payment_status_badge(self, obj):
        colors = {
            'PENDING': 'orange',
            'PAID': 'green',
            'FAILED': 'red',
            'REFUNDED': 'gray',
        }
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 12px; border-radius: 12px;">{}</span>',
            colors.get(obj.payment_status, 'gray'),
            obj.get_payment_status_display()
        )
    payment_status_badge.short_description = 'Payment'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product_name', 'quantity', 'unit_price', 'total_price']
    list_filter = ['created_at']
    readonly_fields = ['total_price']
