from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

import threading

def _send_email_thread(email_obj):
    """Execution logic for background thread"""
    try:
        email_obj.send(fail_silently=False)
        print(f"✅ Email sent to {email_obj.to}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def send_welcome_email(user):
    """Send welcome email to new user (Async)"""
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
        
        # Send in background thread to avoid 502/Timeout
        threading.Thread(target=_send_email_thread, args=(email,)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate welcome email: {e}")


def send_order_confirmation_email(order):
    """Send order confirmation email (Async)"""
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
        threading.Thread(target=_send_email_thread, args=(email,)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate order confirmation: {e}")

def send_password_reset_email(user, reset_url):
    """Send password reset email (Async)"""
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
        threading.Thread(target=_send_email_thread, args=(email,)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate password reset email: {e}")

def send_order_status_email(order):
    """Send order status update email (Async)"""
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
        threading.Thread(target=_send_email_thread, args=(email,)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate status update email: {e}")

def send_payment_status_email(order):
    """Send payment status update email (Async)"""
    try:
        subject = f'💳 Payment Update for Order #{order.order_number}'
        
        email = EmailMultiAlternatives(
            subject=subject,
            body=f'Payment status for order #{order.order_number} is now {order.get_payment_status_display()}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[order.user.email]
        )
        threading.Thread(target=_send_email_thread, args=(email,)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate payment status email: {e}")
