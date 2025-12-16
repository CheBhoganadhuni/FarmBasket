# Remove django_rq decorator
from apps.notifications.email import send_sendgrid_email
from django.template.loader import render_to_string
from django.conf import settings
from .models import User


def send_welcome_email(user_id):
    """Send welcome email to new user (runs synchronously)"""
    
    try:
        user = User.objects.get(id=user_id)
        
        subject = '🌱 Welcome to FarmBasket!'
        html_message = render_to_string('emails/welcome.html', {
            'user': user,
            'site_url': settings.SITE_URL
        })
        
        send_sendgrid_email(subject, user.email, html_message)
    except User.DoesNotExist:
        pass


def send_password_reset_email(user_id, token):
    """Send password reset email (runs synchronously)"""
    
    try:
        user = User.objects.get(id=user_id)
        
        reset_url = f"{settings.SITE_URL}/auth/reset-password?token={token}"
        
        subject = '🔒 Reset Your FarmBasket Password'
        html_message = render_to_string('emails/password_reset.html', {
            'user': user,
            'reset_url': reset_url
        })
        
        send_sendgrid_email(subject, user.email, html_message)
    except User.DoesNotExist:
        pass
