from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

def send_welcome_email(user):
    """Send welcome email to new user (Synchronous)"""
    try:
        # Check preference
        if not user.email_notifications:
            print(f"🔕 Welcome email skipped (User preference): {user.email}")
            return

        subject = '🧺 Welcome to FarmBasket!'
        
        # Render HTML template
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'site_url': 'http://127.0.0.1:8000'  # Change in production
        })
        
        # Create email
        email = EmailMultiAlternatives(
            subject=subject,
            body='Welcome to FarmBasket!',  # Plain text fallback
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Welcome email sent to {user.email}")
        
    except Exception as e:
        print(f"❌ Failed to send welcome email: {e}")


def send_order_confirmation_email(order):
    """Send order confirmation email (Synchronous)"""
    try:
        # Check preference
        if not order.user.email_notifications:
            print(f"🔕 Order confirmation skipped (User preference): {order.user.email}")
            return

        subject = f'📦 Order Confirmed - #{order.order_number}'
        
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'site_url': 'http://127.0.0.1:8000'
        })
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f'Your order #{order.order_number} has been confirmed!',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Order confirmation email sent to {order.user.email}")
        
    except Exception as e:
        print(f"❌ Failed to send order confirmation: {e}")

def send_password_reset_email(user, reset_url):
    """Send password reset email (Synchronous)"""
    try:
        subject = '🔐 FarmBasket Password Reset'
        
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url
        })
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f'Reset your password: {reset_url}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Password reset email sent to {user.email}")
        
    except Exception as e:
        print(f"❌ Failed to send password reset email: {e}")

def send_order_status_email(order):
    """Send order status update email (Synchronous)"""
    try:
        # Check preference
        if not order.user.email_notifications:
            print(f"🔕 Order status update skipped (User preference): {order.user.email}")
            return

        status_messages = {
            'CONFIRMED': '✅ Order Confirmed',
            'PROCESSING': '📦 Order Processing',
            'SHIPPED': '🚚 Order Shipped',
            'DELIVERED': '🎉 Order Delivered',
        }
        
        subject = f"{status_messages.get(order.status, 'Order Update')} - #{order.order_number}"
        
        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'site_url': 'http://127.0.0.1:8000'
        })
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f'Your order #{order.order_number} status: {order.get_status_display()}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email]
        )
        email.attach_alternative(html_message, "text/html")
        email.send(fail_silently=False)
        print(f"✅ Order status email sent to {order.user.email}")
        
    except Exception as e:
        print(f"❌ Failed to send status update email: {e}")

def send_payment_status_email(order):
    """Send payment status update email (Synchronous)"""
    try:
        subject = f'💳 Payment Update for Order #{order.order_number}'
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f'Payment status for order #{order.order_number} is now {order.get_payment_status_display()}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email]
        )
        email.send(fail_silently=False)
        print(f"✅ Payment status email sent to {order.user.email}")
        
    except Exception as e:
        print(f"❌ Failed to send payment status email: {e}")
