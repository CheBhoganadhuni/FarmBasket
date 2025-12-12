from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.orders.models import Order
from apps.accounts.emails import send_order_status_email

@receiver(post_save, sender=Order)
def order_status_changed(sender, instance, created, **kwargs):
    """Send email when order status changes"""
    if not created:  # Only for updates, not creation
        # Check if status actually changed
        if instance.status in ['CONFIRMED', 'PROCESSING', 'SHIPPED', 'DELIVERED', 'CANCELLED']:
            try:
                if instance.user.email_notifications:
                    send_order_status_email(instance)
            except Exception as e:
                print(f"Failed to send status update email: {e}")
