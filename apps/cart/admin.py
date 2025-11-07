from django.contrib import admin
from .models import Cart, CartItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['unit_price', 'total_price']
    fields = ['product', 'quantity', 'unit_price', 'total_price']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'items_count', 'subtotal', 'updated_at']
    readonly_fields = ['created_at', 'updated_at', 'items_count', 'subtotal', 'total']
    inlines = [CartItemInline]
    
    def has_add_permission(self, request):
        # Carts are created automatically, not manually
        return False


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'quantity', 'unit_price', 'total_price', 'updated_at']
    list_filter = ['created_at']
    readonly_fields = ['unit_price', 'total_price']
