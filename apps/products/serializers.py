from rest_framework import serializers
from apps.catalog.models import Product, Category, ProductImage
from apps.orders.models import Order

class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'product_count']

class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'display_order']

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, required=False)
    
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ['in_stock', 'views_count', 'orders_count', 'created_at', 'updated_at']

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        product = Product.objects.create(**validated_data)
        for image_data in images_data:
            ProductImage.objects.create(product=product, **image_data)
        return product

    def to_internal_value(self, data):
        # Fix for Admin: If image is a string (URL), remove it so it's not validated as file
        # Handle QueryDict (mutable copy needed)
        if hasattr(data, 'copy'):
             data = data.copy()

        if 'featured_image' in data and isinstance(data['featured_image'], str):
             # Remove string URLs (like "http://...") to prevent validation error
             # But if it's empty string, allow it (might mean clear?) - No, blank=True means omit it.
             del data['featured_image']
        
        # Handle Nested Images logic (if needed in future)
        # Simplified: If 'images' provided as list, filter them.
        if 'images' in data and isinstance(data['images'], list):
             new_images = []
             for img in data['images']:
                 if isinstance(img, dict) and 'image' in img and not isinstance(img['image'], str):
                     new_images.append(img)
                 elif isinstance(img, dict) and 'image' not in img:
                     new_images.append(img) 
             data['images'] = new_images

        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        
        # Update Product instance
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Handle nested images if provided
        if images_data is not None:
             # Basic implementation: Create new images.
             # In a real app, you might want to handle deletion/ordering.
             for image_data in images_data:
                 ProductImage.objects.create(product=instance, **image_data)
                 
        return instance

class OrderStatusUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(choices=Order.STATUS_CHOICES)