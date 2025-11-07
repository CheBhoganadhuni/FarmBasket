from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.accounts.models import User
import uuid


class Category(models.Model):
    """Product categories (Fruits, Vegetables, Dairy, Pantry)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=10, default='📦', help_text='Emoji icon')
    
    # Display settings
    is_active = models.BooleanField(default=True)
    display_order = models.IntegerField(default=0, help_text='Lower numbers appear first')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'categories'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['display_order', 'name']
    
    def __str__(self):
        return f"{self.icon} {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Product(models.Model):
    """Products available for purchase"""
    
    UNIT_CHOICES = [
        ('KG', 'Kilogram'),
        ('G', 'Gram'),
        ('L', 'Liter'),
        ('ML', 'Milliliter'),
        ('PC', 'Piece'),
        ('BOX', 'Box'),
        ('BUNCH', 'Bunch'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    
    # Basic info
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    
    # Farm story (unique feature!)
    farm_story = models.TextField(
        blank=True,
        help_text='Tell customers about the farm where this product comes from'
    )
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    discount_price = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        validators=[MinValueValidator(0)],
        help_text='Discounted price (optional)'
    )
    
    # Quantity
    unit = models.CharField(max_length=10, choices=UNIT_CHOICES, default='KG')
    unit_value = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=1,
        help_text='e.g., 500 for 500g, 1 for 1kg'
    )
    
    # Stock management
    stock_quantity = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    low_stock_threshold = models.IntegerField(default=10, help_text='Alert when stock falls below this')
    
    # Flags
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False, help_text='Show in featured products')
    is_organic_certified = models.BooleanField(default=True)
    in_stock = models.BooleanField(default=True)
    
    # SEO & Display
    featured_image = models.ImageField(
        upload_to='products/',
        blank=True,
        null=True,
        help_text='Main product image'
    )
    
    # Stats
    views_count = models.IntegerField(default=0)
    orders_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        verbose_name = 'Product'
        verbose_name_plural = 'Products'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['category', 'is_active']),
            models.Index(fields=['-created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.unit_value}{self.unit})"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        
        # Auto-update in_stock based on quantity
        self.in_stock = self.stock_quantity > 0
        
        super().save(*args, **kwargs)
    
    @property
    def display_price(self):
        """Get the price to display (discounted if available)"""
        return self.discount_price if self.discount_price else self.price
    
    @property
    def discount_percentage(self):
        """Calculate discount percentage"""
        if self.discount_price and self.discount_price < self.price:
            return int(((self.price - self.discount_price) / self.price) * 100)
        return 0
    
    @property
    def is_low_stock(self):
        """Check if stock is running low"""
        return self.stock_quantity <= self.low_stock_threshold
    
    @property
    def average_rating(self):
        """Get average rating from reviews"""
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(reviews.aggregate(models.Avg('rating'))['rating__avg'], 1)
        return 0
    
    @property
    def review_count(self):
        """Get total approved reviews"""
        return self.reviews.filter(is_approved=True).count()


class ProductImage(models.Model):
    """Additional product images (carousel)"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')
    alt_text = models.CharField(max_length=200, blank=True)
    display_order = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'product_images'
        ordering = ['display_order', 'created_at']
    
    def __str__(self):
        return f"Image for {self.product.name}"


class Review(models.Model):
    """Product reviews and ratings"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews')
    
    # Review content
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text='Rating from 1 to 5 stars'
    )
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Moderation
    is_approved = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'reviews'
        verbose_name = 'Review'
        verbose_name_plural = 'Reviews'
        ordering = ['-created_at']
        unique_together = ['product', 'user']  # One review per user per product
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name} ({self.rating}★)"


class Wishlist(models.Model):
    """User wishlist items"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='wishlisted_by')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'wishlist'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"
