'''
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.conf import settings
from django.http import HttpResponse, JsonResponse
import razorpay
import json
from .models import Order
from apps.accounts.emails import send_payment_status_email
import threading

# Initialize Razorpay client
razorpay_client = razorpay.Client(
    auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)
)

def _update_order_status(order, payment_id):
    """Helper to update order and send email async"""
    if order.payment_status == 'PAID':
        return # Idempotency check

    order.payment_status = 'PAID'
    order.status = 'CONFIRMED' # Or PROCESSING
    order.razorpay_payment_id = payment_id
    order.save()
    
    # Send email async
    try:
        if order.user.email_notifications:
            threading.Thread(target=send_payment_status_email, args=(order,)).start()
    except Exception as e:
        print(f"Webhook email failed: {e}")

@csrf_exempt
def razorpay_webhook(request):
    """Handle Razorpay Webhooks"""
    if request.method == "POST":
        try:
            # Get signature
            webhook_signature = request.headers.get('X-Razorpay-Signature')
            webhook_secret = settings.RAZORPAY_WEBHOOK_SECRET
            
            if not webhook_secret:
                return JsonResponse({'error': 'Webhook secret not configured'}, status=500)

            # Verify signature
            # Razorpay SDK verify_webhook_signature expects raw body as string/bytes
            request_body = request.body.decode('utf-8')
            
            razorpay_client.utility.verify_webhook_signature(
                request_body,
                webhook_signature,
                webhook_secret
            )
            
            # Process Event
            data = json.loads(request_body)
            event = data.get('event')
            
            if event == 'payment.captured':
                payment = data['payload']['payment']['entity']
                order_id = payment['notes'].get('order_id') # We stored this in notes
                payment_id = payment['id']
                
                if order_id:
                    try:
                        order = Order.objects.get(id=order_id)
                        _update_order_status(order, payment_id)
                        return HttpResponse("OK", status=200)
                    except Order.DoesNotExist:
                        return JsonResponse({'error': 'Order not found'}, status=404)
            
            return HttpResponse("Event ignored", status=200)
            
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({'error': 'Invalid Signature'}, status=400)
        except Exception as e:
            print(f"Webhook Error: {e}")
            return JsonResponse({'error': str(e)}, status=500)
            
    return HttpResponse("Method not allowed", status=405)
'''