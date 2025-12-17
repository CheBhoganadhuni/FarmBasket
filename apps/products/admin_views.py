from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import timedelta
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt

from apps.catalog.models import Product, Category
from apps.orders.models import Order
from apps.accounts.models import User
from .serializers import ProductSerializer, CategorySerializer, OrderStatusUpdateSerializer

# Import Email Utilities
from apps.notifications.email import send_order_status_email, send_payment_status_email, send_account_status_email, send_account_deletion_email

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
    
    # Last 7 days data for charts
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
def admin_products_list(request, data = None):    
    """
    List all products or create new product
    """
    if request.method == 'GET':
        search = request.GET.get('search', '')
        category = request.GET.get('category', '')
        stock_filter = request.GET.get('stock', '')
        
        products = Product.objects.all()
        
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
        serializer = ProductSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Product created successfully',
                'product': serializer.data
            }, status=status.HTTP_201_CREATED)
        return Response({
            'success': False,
            'message': f"Validation Error: {serializer.errors}",
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

def admin_product_detail(request, pk, data=None):
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
        update_data = data if data is not None else request.data
        serializer = ProductSerializer(product, data=update_data, partial=True)
        try:
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Product updated successfully',
                    'product': serializer.data
                })
            return Response({
                'success': False,
                'message': f"Validation Error: {serializer.errors}",
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            return Response({
                'success': False,
                'message': f'Server Error: {str(e)}',
                'trace': traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
    status_filter = request.GET.get('status', '')
    search = request.GET.get('search', '')

    orders = Order.objects.select_related('user').prefetch_related('items')

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

    orders_data = [{
        'id': str(order.id),
        'order_number': order.order_number,
        'user': {
            'id': str(order.user.id),
            'name': order.user.get_full_name() or order.user.email,
            'email': order.user.email
        },
        'items_count': order.items.count(),
        'items': [
            {
                'id': str(item.id),
                'product_name': item.product_name,
                'quantity': item.quantity,
                'unit_price': float(item.unit_price)
            }
            for item in order.items.all()
        ],
        'total': float(order.total),
        'wallet_amount': float(order.wallet_amount) if hasattr(order, 'wallet_amount') and order.wallet_amount else 0,
        'status': order.status,
        'payment_status': order.payment_status,
        'payment_method': order.payment_method,
        'delivery_name': order.delivery_name,
        'delivery_address': order.delivery_address,
        'delivery_city': order.delivery_city,
        'delivery_state': order.delivery_state,
        'delivery_postal_code': order.delivery_postal_code,
        'delivery_phone': order.delivery_phone,
        'admin_notes': order.admin_notes,
        'created_at': order.created_at.isoformat(),
        'updated_at': order.updated_at.isoformat()
    } for order in orders]

    return Response({
        'orders': orders_data,
        'count': len(orders_data)
    })


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_order_update_status(request, pk, data=None):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found'}, status=404)
    
    status_val = data.get('status') if data else request.data.get('status')
    if not status_val:
        return Response({'success': False, 'message': 'Status required'}, status=400)

    # validate status
    valid_statuses = [choice[0] for choice in Order.STATUS_CHOICES]
    if status_val not in valid_statuses:
        return Response({'success': False, 'message': 'Invalid status'}, status=400)

    prev_status = order.status
    order.status = status_val
    order.save()

    if prev_status != 'CANCELLED' and status_val == 'CANCELLED':
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.orders_count = max(0, item.product.orders_count - 1)
                item.product.save()
    
    # Send Email Notification for Status Change
    try:
        send_order_status_email(order)
    except Exception as e:
        print(f"Failed to send status update email: {e}")

    return Response({'success': True, 'message': f'Order status updated to {order.get_status_display()}'})


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
    
    users = users.exclude(email='bhoganadhunichetan@gmail.com').exclude(id=request.user.id).order_by('-date_joined')
    
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

@csrf_exempt
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def admin_delete_user(request, pk):
    try:
        user = User.objects.get(pk=pk)
        if user.is_superuser:
             return Response({'success': False, 'message': 'Cannot delete superuser'}, status=status.HTTP_403_FORBIDDEN)
        
        # Send Goodbye Email
        try:
            send_account_deletion_email(user)
        except Exception as e:
            print(f"Error sending deletion email: {e}")

        user.delete()
        return Response({'success': True, 'message': 'User deleted successfully'})
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

@csrf_exempt
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_toggle_user_active(request, pk):
    try:
        user = User.objects.get(pk=pk)
        
        # Prevent modifying superusers
        if user.is_superuser:
            return Response({'success': False, 'message': 'Cannot modify superuser accounts'}, status=status.HTTP_403_FORBIDDEN)
            
        new_status = not user.is_active
        user.is_active = new_status
        user.save()
        
        # Send Status Change Email
        try:
            send_account_status_email(user, new_status)
        except Exception as e:
            print(f"Error sending status email: {e}")
        
        status_text = "Active" if new_status else "Inactive"
        return Response({'success': True, 'message': f'User marked as {status_text}'})
    except User.DoesNotExist:
        return Response({'success': False, 'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAdminUser])
def admin_payment_update_status(request, pk, data = None):
    try:
        order = Order.objects.get(pk=pk)
    except Order.DoesNotExist:
        return Response({'success': False, 'message': 'Order not found'}, status=status.HTTP_404_NOT_FOUND)

    new_payment_status = data.get('payment_status') if data else request.data.get('payment_status')
    valid_statuses = ['PENDING', 'PAID', 'FAILED', 'REFUNDED']

    if new_payment_status not in valid_statuses:
        return Response({'success': False, 'message': 'Invalid payment status'}, status=status.HTTP_400_BAD_REQUEST)

    # Status Sync Logic
    if new_payment_status == 'REFUNDED':
        refund_amount = Decimal('0')
        
        if order.payment_status == 'PAID':
            refund_amount = order.total
        else:
             if hasattr(order, 'wallet_amount'):
                 refund_amount = order.wallet_amount
             else:
                 refund_amount = Decimal('0')

        if refund_amount > 0:
            order.user.credit_wallet(refund_amount)
            
        order.status = 'CANCELLED'
        
        # Restore stock
        for item in order.items.all():
            if item.product:
                item.product.stock_quantity += item.quantity
                item.product.orders_count = max(0, item.product.orders_count - 1)
                item.product.save()

    elif new_payment_status == 'FAILED':
         order.status = 'CANCELLED'

    order.payment_status = new_payment_status
    order.save()
    
    # Send Email Notification
    try:
        if order.user.email_notifications:
             send_payment_status_email(order)
    except Exception as e:
        print(f"Failed to send email: {e}")

    return Response({'success': True, 'message': f'Payment status updated to {new_payment_status}'})
