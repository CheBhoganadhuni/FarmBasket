import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.template.loader import render_to_string
from django.conf import settings
import logging
import threading

logger = logging.getLogger(__name__)

# ===== CORE SENDGRID HELPER =====

def send_sendgrid_email(subject, to_email, html_content, from_email=None):
    """
    Sends an email using SendGrid Web API.
    """
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        logger.error("SENDGRID_API_KEY not found in environment variables.")
        return False

    sender = from_email if from_email else settings.DEFAULT_FROM_EMAIL
    from_email = Email(sender)
    to_email = To(to_email)
    content = Content("text/html", html_content)
    
    mail = Mail(from_email, to_email, subject, content)

    try:
        sg = sendgrid.SendGridAPIClient(api_key=api_key)
        response = sg.client.mail.send.post(request_body=mail.get())
        
        if 200 <= response.status_code < 300:
            logger.info(f"Email sent successfully to {to_email.email}")
            return True
        else:
            logger.error(f"Failed to send email. Status Code: {response.status_code}")
            logger.error(f"Response Body: {response.body}")
            return False
            
    except Exception as e:
        logger.error(f"Exception sending email via SendGrid: {str(e)}")
        return False

def _send_email_thread(subject, to_email, html_content):
    """Background thread wrapper to prevent blocking"""
    try:
        success = send_sendgrid_email(subject, to_email, html_content)
        if success:
            print(f"✅ Email sent to {to_email}")
        else:
            print(f"❌ Failed to send email to {to_email}")
    except Exception as e:
        print(f"❌ Exception in email thread: {e}")

# ===== EMAIL TRIGGERS =====

def send_admin_cancellation_email(order, site_url):
    """Sends an email to admin when a user cancels an order."""
    subject = f"❌ Order Cancelled: #{order.order_number}"
    
    html_content = render_to_string('emails/admin_order_cancellation.html', {
        'order': order,
        'site_url': site_url
    })
    
    # Debug Logging
    print(f"DEBUG: Order Number: {getattr(order, 'order_number', 'MISSING')}")
    
    # Recipient: Verified Sender/Admin or from settings
    admin_email = 'bhoganadhunichetan@gmail.com' 
    
    # Send directly (admin alerts are critical)
    return send_sendgrid_email(subject, admin_email, html_content, from_email=admin_email)


def send_welcome_email(user):
    """Send welcome email to new user"""
    try:
        if not user.email_notifications:
            return

        subject = '🧺 Welcome to FarmBasket!'
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'site_url': settings.SITE_URL
        })
        
        threading.Thread(target=_send_email_thread, args=(subject, user.email, html_message)).start()
    except Exception as e:
        print(f"❌ Failed to initiate welcome email: {e}")


def send_order_confirmation_email(order):
    """Send order confirmation email"""
    try:
        if not order.user.email_notifications:
            return

        subject = f'📦 Order Confirmed - #{order.order_number}'
        html_message = render_to_string('emails/order_confirmation.html', {
            'order': order,
            'site_url': settings.SITE_URL
        })
        
        threading.Thread(target=_send_email_thread, args=(subject, order.user.email, html_message)).start()
    except Exception as e:
        print(f"❌ Failed to initiate order confirmation: {e}")


def send_password_reset_email(user, reset_url):
    """Send password reset email"""
    try:
        subject = '🔐 FarmBasket Password Reset'
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url
        })
        
        threading.Thread(target=_send_email_thread, args=(subject, user.email, html_message)).start()
    except Exception as e:
        print(f"❌ Failed to initiate password reset email: {e}")


def send_order_status_email(order):
    """Send order status update email"""
    try:
        if not order.user.email_notifications:
            return

        status_messages = {
            'CONFIRMED': '✅ Order Confirmed',
            'PROCESSING': '📦 Order Processing',
            'SHIPPED': '🚚 Order Shipped',
            'DELIVERED': '🎉 Order Delivered',
            'CANCELLED': '❌ Order Cancelled', 
        }
        
        subject = f"{status_messages.get(order.status, 'Order Update')} - #{order.order_number}"
        
        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'site_url': settings.SITE_URL
        })
        
        threading.Thread(target=_send_email_thread, args=(subject, order.user.email, html_message)).start()
    except Exception as e:
        print(f"❌ Failed to initiate status update email: {e}")


def send_payment_status_email(order):
    """Send payment status update email"""
    try:
        subject = f'💳 Payment Update for Order #{order.order_number}'
        
        html_message = render_to_string('emails/order_status_update.html', {
            'order': order,
            'title': 'Payment Status Update',
            'message': f'Payment status: {order.get_payment_status_display()}',
            'site_url': settings.SITE_URL
        })
        
        threading.Thread(target=_send_email_thread, args=(subject, order.user.email, html_message)).start()
    except Exception as e:
        print(f"❌ Failed to initiate payment status email: {e}")

def send_account_status_email(user, is_active):
    """Send account activation/deactivation email"""
    try:
        if is_active:
            subject = '🎉 Welcome Back! Your Account is Active'
            html_content = render_to_string('emails/account_activated.html', {
                'user': user,
                'site_url': settings.SITE_URL
            })
        else:
            subject = '👋 Account Deactivated'
            html_content = render_to_string('emails/account_deactivated.html', {
                'user': user,
                'site_url': settings.SITE_URL
            })

        threading.Thread(target=_send_email_thread, args=(subject, user.email, html_content)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate account status email: {e}")

def send_account_deletion_email(user):
    """Send account deletion email"""
    try:
        subject = '⚠️ Account Deletion Notification - FarmBasket'
        
        html_content = render_to_string('emails/account_deletion.html', {
            'user': user,
            'site_url': settings.SITE_URL
        })
        
        threading.Thread(target=_send_email_thread, args=(subject, user.email, html_content)).start()
        
    except Exception as e:
        print(f"❌ Failed to initiate account deletion email: {e}")
