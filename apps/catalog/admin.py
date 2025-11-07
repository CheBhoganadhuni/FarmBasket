from django.contrib import admin
from django.utils.html import format_html
from .models import Category, Product, ProductImage, Review, Wishlist


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['icon_display', 'name', 'slug', 'is_active', 'display_order', 'product_count']
    list_editable = ['is_active', 'display_order']
    list_filter = ['is_active']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    
    def icon_display(self, obj):
        return format_html('<span style="font-size: 24px;">{}</span>', obj.icon)
    icon_display.short_description = 'Icon'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'alt_text', 'display_order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'category', 'display_price_formatted', 'stock_status', 
        'is_featured', 'is_organic_certified', 'average_rating', 'created_at'
    ]
    list_filter = ['category', 'is_active', 'is_featured', 'is_organic_certified', 'in_stock']
    search_fields = ['name', 'description', 'farm_story']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['is_featured']
    readonly_fields = ['views_count', 'orders_count', 'average_rating', 'review_count']
    
    inlines = [ProductImageInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'slug', 'description', 'farm_story')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'unit', 'unit_value')
        }),
        ('Stock Management', {
            'fields': ('stock_quantity', 'low_stock_threshold', 'in_stock')
        }),
        ('Display Settings', {
            'fields': ('featured_image', 'is_active', 'is_featured', 'is_organic_certified')
        }),
        ('Statistics', {
            'fields': ('views_count', 'orders_count', 'average_rating', 'review_count'),
            'classes': ('collapse',)
        }),
    )
    
    def display_price_formatted(self, obj):
        if obj.discount_price:
            return format_html(
                '<span style="text-decoration: line-through;">₹{}</span> <strong style="color: green;">₹{}</strong>',
                obj.price, obj.discount_price
            )
        return f'₹{obj.price}'
    display_price_formatted.short_description = 'Price'
    
    def stock_status(self, obj):
        if not obj.in_stock:
            return format_html('<span style="color: red;">Out of Stock</span>')
        elif obj.is_low_stock:
            return format_html('<span style="color: orange;">Low Stock ({})</span>', obj.stock_quantity)
        return format_html('<span style="color: green;">In Stock ({})</span>', obj.stock_quantity)
    stock_status.short_description = 'Stock'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'rating_display', 'is_approved', 'created_at']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__email', 'product__name', 'comment']
    list_editable = ['is_approved']
    
    def rating_display(self, obj):
        stars = '⭐' * obj.rating
        return format_html('<span>{}</span>', stars)
    rating_display.short_description = 'Rating'


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']
