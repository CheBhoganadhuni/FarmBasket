from django.db import models

# Create your models here.
from django.db import models
from django.core.validators import MinValueValidator
from apps.accounts.models import User
from apps.catalog.models import Product
import uuid


class Cart(models.Model):
    """Shopping cart for each user"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'carts'
    
    def __str__(self):
        return f"Cart for {self.user.email}"
    
    @property
    def items_count(self):
        """Total number of items in cart"""
        return self.items.aggregate(total=models.Sum('quantity'))['total'] or 0
    
    @property
    def subtotal(self):
        """Calculate cart subtotal"""
        total = 0
        for item in self.items.all():
            total += item.total_price
        return total
    
    @property
    def total(self):
        """Calculate cart total (subtotal + any fees)"""
        # For now, same as subtotal. Later add delivery charges, taxes, etc.
        return self.subtotal


class CartItem(models.Model):
    """Individual items in the cart"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1, validators=[MinValueValidator(1)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'product']  # One product can only appear once per cart
    
    def __str__(self):
        return f"{self.quantity}x {self.product.name}"
    
    @property
    def unit_price(self):
        """Get the current price of the product"""
        return self.product.display_price
    
    @property
    def total_price(self):
        """Calculate total price for this item"""
        return self.unit_price * self.quantity
    
    def save(self, *args, **kwargs):
        # Validate stock availability
        if self.quantity > self.product.stock_quantity:
            raise ValueError(f"Only {self.product.stock_quantity} items available")
        super().save(*args, **kwargs)
