# products/admin_views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal

from apps.catalog.models import Product, Category
from apps.orders.models import Order
from apps.accounts.models import User
from .serializers import ProductSerializer, CategorySerializer

@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_dashboard_stats(request):
    """
    Dashboard overview statistics
    """
    now = timezone.now()
    today = now.date()
    
    # Total counts
    total_products = Product.objects.count()
    total_users = User.objects.count()
    total_orders = Order.objects.count()
    
    # Revenue
    total_revenue = Order.objects.exclude(
        status='CANCELLED'
    ).aggregate(total=Sum('total'))['total'] or Decimal('0')
    
    # Today's stats
    orders_today = Order.objects.filter(created_at__date=today).count()
    revenue_today = Order.objects.filter(
        created_at__date=today
    ).exclude(status='CANCELLED').aggregate(
        total=Sum('total')
    )['total'] or Decimal('0')
    
    # Last 7 days data for charts - you can skip if not needed
    last_7_days = []
    for i in range(6, -1, -1):
        date = today - timedelta(days=i)
        day_orders = Order.objects.filter(created_at__date=date)
        day_revenue = day_orders.exclude(status='CANCELLED').aggregate(
            total=Sum('total')
        )['total'] or Decimal('0')
        
        last_7_days.append({
            'date': date.strftime('%b %d'),
            'orders': day_orders.count(),
            'revenue': float(day_revenue)
        })
    
    # Order status breakdown
    order_status_breakdown = []
    for status_code, status_label in Order.STATUS_CHOICES:
        count = Order.objects.filter(status=status_code).count()
        if count > 0:
            order_status_breakdown.append({
                'status': status_code,
                'label': status_label,
                'count': count
            })
    
    # Top selling products
    top_products = Product.objects.annotate(
        sales_count=Count('orderitem')
    ).filter(sales_count__gt=0).order_by('-sales_count')[:5]
    
    # Low stock products
    low_stock = Product.objects.filter(
        stock_quantity__lte=10,
        stock_quantity__gt=0
    ).order_by('stock_quantity')[:5]

    # Recent orders
    recent_orders = Order.objects.select_related('user').order_by('-created_at')[:5]
    recent_orders_data = [{
        'id': str(order.id),
        'order_number': order.order_number,
        'user_name': order.user.get_full_name() or order.user.email,
        'total': float(order.total),
        'status': order.status,
        'status_display': order.get_status_display(),
        'created_at': order.created_at.isoformat()
    } for order in recent_orders]
    
    return Response({
        'overview': {
            'total_products': total_products,
            'total_users': total_users,
            'total_orders': total_orders,
            'total_revenue': float(total_revenue),
            'orders_today': orders_today,
            'revenue_today': float(revenue_today)
        },
        'charts': {
            'last_7_days': last_7_days,
            'order_status': order_status_breakdown
        },
        'top_products': ProductSerializer(top_products, many=True).data,
        'low_stock': ProductSerializer(low_stock, many=True).data,
        'recent_orders': recent_orders_data
    })


@api_view(['GET', 'POST'])
@permission_classes([IsAdminUser])
def admin_products_list(request):
    """
    List all products or create new product
    """
    if request.method == 'GET':
        # Get query parameters
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        stock_filter = request.GET.get('stock', '')
        
        # Base queryset
        products = Product.objects.all()
        
        # Apply filters
        if search:
            products = products.filter(
                Q(name__icontains=search) | 
                Q(description__icontains=search)
            )
        
        if category:
            products = products.filter(category_id=category)
        
        if stock_filter == 'low':
            products = products.filter(stock_quantity__lte=10)
        elif stock_filter == 'out':
            products = products.filter(stock_quantity=0)

        
        products = products.select_related('category').order_by('-created_at')
        serializer = ProductSerializer(products, many=True)
        
        return Response({
            'products': serializer.data,
            'count': products.count()
        })
    
    elif request.method == 'POST':
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'product': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAdminUser])
def admin_product_detail(request, pk):
    """
    Get, update or delete a specific product
    """
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Product not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Product updated successfully',
                'product': serializer.data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        product_name = product.name
        product.delete()
        return Response({
            'success': True,
            'message': f'Product "{product_name}" deleted successfully'
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_orders_list(request):
    """
    List all orders with filters
    """
    # Get query parameters
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')
    
    # Base queryset
    orders = Order.objects.select_related('user').prefetch_related('items')
    
    # Apply filters
    if status_filter:
        orders = orders.filter(status=status_filter)
    
    if search:
        orders = orders.filter(
            Q(order_number__icontains=search) |
            Q(user__email__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search)
        )
    
    orders = orders.order_by('-created_at')
    
    # Serialize data
    orders_data = [{
        'id': str(order.id),
        'order_number': order.order_number,
        'user': {
            'id': str(order.user.id),
            'name': order.user.get_full_name() or order.user.email,
            'email': order.user.email
        },
        'total': float(order.total),
        'status': order.status,
        'status_display': order.get_status_display(),
        'payment_status': order.payment_status,
        'payment_method': order.payment_method,
        'items_count': order.items.count(),
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat()
    } for order in orders]
    
    return Response({
        'orders': orders_data,
        'count': len(orders_data)
    })


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_order_update_status(request, pk):
    """
    Update order status
    """
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Order not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    new_status = request.data.get('status')
    if not new_status:
        return Response({
            'success': False,
            'message': 'Status is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Validate status
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if new_status not in valid_statuses:
        return Response({
            'success': False,
            'message': 'Invalid status'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    order.status = new_status
    order.save()
    
    return Response({
        'success': True,
        'message': f'Order status updated to {order.get_status_display()}',
        'order': {
            'id': str(order.id),
            'order_number': order.order_number,
            'status': order.status,
            'status_display': order.get_status_display()
        }
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_users_list(request):
    """
    List all users with stats
    """
    search = request.GET.get('search', '')
    
    users = User.objects.all()
    
    if search:
        users = users.filter(
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    users = users.order_by('-date_joined')
    
    users_data = [{
        'id': str(user.id),
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'full_name': user.get_full_name() or user.email,
        'is_active': user.is_active,
        'is_staff': user.is_staff,
        'date_joined': user.date_joined.isoformat(),
        'last_login': user.last_login.isoformat() if user.last_login else None,
        'orders_count': user.orders.count(),
        'total_spent': float(
            user.orders.exclude(status='CANCELLED').aggregate(
                total=Sum('total')
            )['total'] or Decimal('0')
        ),
        'loyalty_tier': user.loyalty_tier,
        'xp_points': user.xp_points
    } for user in users]
    
    return Response({
        'users': users_data,
        'count': len(users_data)
    })


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_categories_list(request):
    """
    List all categories
    """
    categories = Category.objects.annotate(
        product_count=Count('products')
    ).order_by('name')
    
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_user(request, pk):
    try:
        print(f'User performing delete: {request.user.email}, is_staff: {request.user.is_staff}')
        user = User.objects.get(pk=pk)
        user.delete()
        return Response({'success': True, 'message': 'User deleted successfully'})
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
