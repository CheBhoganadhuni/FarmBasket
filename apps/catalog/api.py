from typing import List, Optional
from django.shortcuts import get_object_or_404
from django.db.models import Q, Avg, Count, F
from django.db.models.functions import Coalesce
from ninja import Router, Query
from ninja.pagination import paginate

from .models import Category, Product, Review, Wishlist
from .schemas import (
    CategorySchema, ProductListSchema, ProductDetailSchema,
    ReviewSchema, ReviewCreateSchema, MessageSchema
)
from apps.accounts.auth import AuthBearer

router = Router(tags=['Products'])
auth = AuthBearer()


# ===== CATEGORY ENDPOINTS =====

@router.get("/categories", response=List[CategorySchema])
def list_categories(request):
    """Get all active categories with product count"""
    categories = Category.objects.filter(is_active=True).prefetch_related('products')
    
    result = []
    for cat in categories:
        result.append({
            'id': str(cat.id),
            'name': cat.name,
            'slug': cat.slug,
            'description': cat.description,
            'icon': cat.icon,
            'is_active': cat.is_active,
            'product_count': cat.products.filter(is_active=True).count(),
        })
    
    return result


# ===== PRODUCT ENDPOINTS =====

@router.get("/products", response=List[ProductListSchema])
@paginate
def list_products(
    request,
    category: Optional[str] = None,
    search: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    in_stock: Optional[bool] = None,
    is_featured: Optional[bool] = None,
    sort_by: Optional[str] = 'newest'
):
    """Get paginated list of products with filters"""
    queryset = Product.objects.filter(is_active=True).select_related('category')
    
    # Filter by category
    if category:
        queryset = queryset.filter(category__slug=category)
    
    # Search
    if search:
        queryset = queryset.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(farm_story__icontains=search)
        )
    
    # Price range
    if min_price is not None:
        queryset = queryset.filter(price__gte=min_price)
    if max_price is not None:
        queryset = queryset.filter(price__lte=max_price)
    
    # Stock filter
    if in_stock is True:
        queryset = queryset.filter(in_stock=True)
    
    # Featured filter
    if is_featured is True:
        queryset = queryset.filter(is_featured=True)
    
    # Sorting
    if sort_by == 'price_low':
        queryset = queryset.order_by('price')
    elif sort_by == 'price_high':
        queryset = queryset.order_by('-price')
    elif sort_by == 'rating':
        queryset = queryset.annotate(
            avg_rating=Coalesce(Avg('reviews__rating', filter=Q(reviews__is_approved=True)), 0.0)
        ).order_by('-avg_rating')
    elif sort_by == 'popular':
        queryset = queryset.order_by('-orders_count', '-views_count')
    else:  # newest
        queryset = queryset.order_by('-created_at')
    
    # Convert to dictionary format
    products = []
    for product in queryset:
        products.append({
            'id': str(product.id),
            'name': product.name,
            'slug': product.slug,
            'category_name': product.category.name,
            'category_icon': product.category.icon,
            'price': product.price,
            'discount_price': product.discount_price,
            'display_price': product.display_price,
            'discount_percentage': product.discount_percentage,
            'unit': product.unit,
            'unit_value': product.unit_value,
            'featured_image': product.featured_image.url.replace('/media/http', 'http') if product.featured_image else None,
            'is_featured': product.is_featured,
            'is_organic_certified': product.is_organic_certified,
            'in_stock': product.in_stock,
            'is_low_stock': product.is_low_stock,
            'average_rating': product.average_rating,
            'review_count': product.review_count,
        })
    
    return products


@router.get("/products/{slug}", response=ProductDetailSchema)
def get_product(request, slug: str):
    """Get product details by slug"""
    product = get_object_or_404(
        Product.objects.select_related('category').prefetch_related('images'),
        slug=slug,
        is_active=True
    )
    
    # Increment view count
    product.views_count += 1
    product.save(update_fields=['views_count'])
    
    # Get reviews
    reviews = product.reviews.select_related('user').filter(is_approved=True).order_by('-created_at')

    # Get similar products
    similar_qs = Product.objects.filter(
        category=product.category, 
        is_active=True, 
        in_stock=True
    ).exclude(id=product.id).order_by('?')[:4]
    
    similar_products_data = []
    for p in similar_qs:
        similar_products_data.append({
            'id': str(p.id),
            'name': p.name,
            'slug': p.slug,
            'category_name': p.category.name,
            'category_icon': p.category.icon,
            'price': p.price,
            'discount_price': p.discount_price,
            'display_price': p.display_price,
            'discount_percentage': p.discount_percentage,
            'unit': p.unit,
            'unit_value': p.unit_value,
            'featured_image': p.featured_image.url.replace('/media/http', 'http') if p.featured_image else None,
            'is_featured': p.is_featured,
            'is_organic_certified': p.is_organic_certified,
            'in_stock': p.in_stock,
            'is_low_stock': p.is_low_stock,
            'average_rating': p.average_rating,
            'review_count': p.review_count,
        })
    
    # Build response as dictionary
    return {
        'id': str(product.id),
        'name': product.name,
        'slug': product.slug,
        'description': product.description,
        'farm_story': getattr(product, 'farm_story', None),
        'category': product.category,
        'price': product.price,
        'discount_price': product.discount_price,
        'display_price': product.display_price,
        'discount_percentage': product.discount_percentage,
        'unit': product.unit,
        'unit_value': product.unit_value,
        'stock_quantity': product.stock_quantity,
        'is_active': product.is_active,
        'is_featured': product.is_featured,
        'is_organic_certified': product.is_organic_certified,
        'in_stock': product.in_stock,
        'is_low_stock': product.is_low_stock,
        'featured_image': product.featured_image,
        'images': product.images.all(),
        'average_rating': product.average_rating,
        'review_count': product.review_count,
        'views_count': product.views_count,
        'created_at': product.created_at,
        'reviews': list(reviews), # Ninja handles model -> schema conversion automatically for lists of models if config is set
        'similar_products': similar_products_data
    }


@router.get("/products/{slug}/reviews", response=List[ReviewSchema])
def get_product_reviews(request, slug: str):
    """Get all approved reviews for a product"""
    product = get_object_or_404(Product, slug=slug)
    reviews = Review.objects.filter(
        product=product,
        is_approved=True
    ).select_related('user').order_by('-created_at')
    
    result = []
    for review in reviews:
        result.append({
            'id': str(review.id),
            'user_name': review.user.full_name,
            'rating': review.rating,
            'title': review.title,
            'comment': review.comment,
            'created_at': review.created_at,
        })
    
    return result


@router.post("/products/{slug}/reviews", response=ReviewSchema, auth=auth)
def create_review(request, slug: str, data: ReviewCreateSchema):
    """Create a review for a product"""
    product = get_object_or_404(Product, slug=slug)
    user = request.auth
    
    # Check if user already reviewed this product
    if Review.objects.filter(product=product, user=user).exists():
        raise Exception("You have already reviewed this product")
    
    review = Review.objects.create(
        product=product,
        user=user,
        rating=data.rating,
        title=data.title or '',
        comment=data.comment
    )
    
    return {
        'id': str(review.id),
        'user_name': user.full_name,
        'rating': review.rating,
        'title': review.title,
        'comment': review.comment,
        'created_at': review.created_at,
    }


# ===== WISHLIST ENDPOINTS =====

@router.get("/wishlist", response=List[ProductListSchema], auth=auth)
def get_wishlist(request):
    """Get user's wishlist"""
    wishlist_items = Wishlist.objects.filter(
        user=request.auth
    ).select_related('product__category')
    
    products = []
    for item in wishlist_items:
        product = item.product
        products.append({
            'id': str(product.id),
            'name': product.name,
            'slug': product.slug,
            'category_name': product.category.name,
            'category_icon': product.category.icon,
            'price': product.price,
            'discount_price': product.discount_price,
            'display_price': product.display_price,
            'discount_percentage': product.discount_percentage,
            'unit': product.unit,
            'unit_value': product.unit_value,
            'featured_image': product.featured_image.url if product.featured_image else None,
            'is_featured': product.is_featured,
            'is_organic_certified': product.is_organic_certified,
            'in_stock': product.in_stock,
            'is_low_stock': product.is_low_stock,
            'average_rating': product.average_rating,
            'review_count': product.review_count,
        })
    
    return products


@router.post("/wishlist/add/{product_id}", response=MessageSchema, auth=auth)
def add_to_wishlist(request, product_id: str):
    """Add product to wishlist"""
    product = get_object_or_404(Product, id=product_id)
    user = request.auth
    
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=user,
        product=product
    )
    
    if created:
        return {"message": "Added to wishlist", "success": True}
    return {"message": "Already in wishlist", "success": False}


@router.delete("/wishlist/remove/{product_id}", response=MessageSchema, auth=auth)
def remove_from_wishlist(request, product_id: str):
    """Remove product from wishlist"""
    product = get_object_or_404(Product, id=product_id)
    user = request.auth
    
    deleted_count, _ = Wishlist.objects.filter(user=user, product=product).delete()
    
    if deleted_count > 0:
        return {"message": "Removed from wishlist", "success": True}
    return {"message": "Not in wishlist", "success": False}


@router.get("/wishlist/check/{product_id}", response=dict, auth=auth)
def check_wishlist(request, product_id: str):
    """Check if product is in user's wishlist"""
    exists = Wishlist.objects.filter(
        user=request.auth,
        product_id=product_id
    ).exists()
    
    return {"in_wishlist": exists}
