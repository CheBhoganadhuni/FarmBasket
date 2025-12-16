import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from django.template.loader import render_to_string
from django.conf import settings # ensure settings is imported
import logging

logger = logging.getLogger(__name__)

def send_admin_cancellation_email(order, site_url):
    """
    Sends an email to admin when a user cancels an order.
    """
    subject = f"❌ Order Cancelled: #{order.order_number}"
    
    html_content = render_to_string('emails/admin_order_cancellation.html', {
        'order': order,
        'site_url': site_url
    })
    
    # Recipient: Verified Sender/Admin or from settings
    # User requested 'bhoganadhunichetan@gmail.com' explicitly
    admin_email = 'bhoganadhunichetan@gmail.com' 
    
    return send_sendgrid_email(subject, admin_email, html_content, from_email=admin_email)

def send_sendgrid_email(subject, to_email, html_content, from_email=None):
    """
    Sends an email using SendGrid Web API.
    
    Args:
        subject (str): The subject of the email.
        to_email (str): The recipient's email address.
        html_content (str): The HTML content of the email.
        from_email (str, optional): The sender's email address. Defaults to settings.DEFAULT_FROM_EMAIL.
    
    Returns:
        bool: True if successful, False otherwise.
    """
    api_key = os.environ.get('SENDGRID_API_KEY')
    if not api_key:
        logger.error("SENDGRID_API_KEY not found in environment variables.")
        return False

    # Default sender from settings or fallback
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
