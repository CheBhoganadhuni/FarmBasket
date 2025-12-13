import os
import django
from django.conf import settings
from django.core.mail import send_mail

# Configure Django settings manually if not configured (for standalone run)
if not settings.configured:
    # Attempt to read from env or use defaults/user input for debugging
    import sys
    
    # Simulating the settings needed for email
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    try:
        from django.core.management import execute_from_command_line
        django.setup()
    except Exception as e:
        print(f"Setup Error: {e}")

def list_email_settings():
    print("--- Current Email Configuration ---")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_USE_SSL: {settings.EMAIL_USE_SSL}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print("-----------------------------------")

def test_send():
    recipient = 'bhoganadhunichetan@gmail.com' # Sending to self
    print(f"\nAttempting to send test email to {recipient}...")
    try:
        send_mail(
            subject='FarmBasket Debug Email',
            message='If you see this, SendGrid is working perfectly! 🚀',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient],
            fail_silently=False,
        )
        print("\n✅ SUCCESS! Email sent successfully.")
    except Exception as e:
        print(f"\n❌ FAILED! Error details:\n{e}")
        print("\n💡 Troubleshooting Tips:")
        if "Sender address rejected" in str(e):
            print("- The 'DEFAULT_FROM_EMAIL' does not match your Verified Sender in SendGrid.")
        elif "Authentication failed" in str(e):
            print("- Check your API Key (Password).")

if __name__ == "__main__":
    list_email_settings()
    test_send()
