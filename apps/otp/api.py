from ninja import Router, Schema
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import FarmOTP
from apps.notifications.email import send_otp_email
import random
import string
from datetime import timedelta

router = Router()
User = get_user_model()

# --- SCHEMAS ---
class GenerateOTPRequest(Schema):
    email: str
    type: str = "forgotPwd"  # 'forgotPwd' or 'bypassPwd'

class VerifyOTPRequest(Schema):
    email: str
    otp: str
    type: str = "forgotPwd"

class ResetPasswordRequest(Schema):
    email: str
    otp: str
    new_password: str

# --- ENDPOINTS ---

@router.post("/generate", response={200: dict, 400: dict, 404: dict})
def generate_otp(request, data: GenerateOTPRequest):
    # 1. Check User validity
    try:
        user = User.objects.get(email=data.email)
    except User.DoesNotExist:
        return 404, {"detail": "You are not organic, wanna join our journey?"}

    # 2. Check if social login (Google users shouldn't use this)
    if user.social_avatar_url:
         return 400, {"detail": "You are logged in via Google. You do not need to reset your password."}

    # 3. Generate OTP
    otp_code = ''.join(random.choices(string.digits, k=6))

    # 4. Save to DB
    FarmOTP.objects.create(
        farmotp_email=data.email,
        farmotp_value=otp_code,
        farmotp_type=data.type,
        farmotp_usage=False
    )

    # 5. Send Email
    try:
        send_otp_email(user, otp_code, otp_type="Forgot Password" if data.type == "forgotPwd" else "Login Verification")
    except Exception as e:
        pass # Email fail shouldn't crash API

    return 200, {"success": True, "message": "OTP sent successfully! Check your inbox."}


@router.post("/verify", response={200: dict, 400: dict})
def verify_otp(request, data: VerifyOTPRequest):
    # 1. Fetch the MOST RECENT OTP for this email & type
    otp_record = FarmOTP.objects.filter(
        farmotp_email=data.email,
        farmotp_type=data.type
    ).order_by('farmotp_create_time').last()

    if not otp_record:
        return 400, {"detail": "No OTP found. Please generate one."}

    # 2. Check Expiry (30 mins)
    if otp_record.farmotp_create_time < timezone.now() - timedelta(minutes=30):
        return 400, {"detail": "OTP has expired. Please request a new one."}
    
    # 3. Check Usage
    if otp_record.farmotp_usage:
        return 400, {"detail": "This OTP has already been used."}

    # 4. Check Value Match
    if otp_record.farmotp_value != data.otp:
        return 400, {"detail": "Invalid OTP. Please ensure you are using the most recent code sent to your email."}

    return 200, {"success": True, "message": "OTP Verified"}


@router.post("/reset-password", response={200: dict, 400: dict})
def reset_password(request, data: ResetPasswordRequest):
    # 1. Fetch the MOST RECENT OTP again (Secure flow)
    otp_record = FarmOTP.objects.filter(
        farmotp_email=data.email,
        farmotp_type="forgotPwd"
    ).order_by('farmotp_create_time').last()
    
    if not otp_record:
        return 400, {"detail": "Invalid session. Please generate OTP again."}

    # 2. Re-verify everything (Time, Usage, Value)
    if otp_record.farmotp_create_time < timezone.now() - timedelta(minutes=30):
        return 400, {"detail": "OTP has expired. Please request a new one."}

    if otp_record.farmotp_usage:
         return 400, {"detail": "This OTP has already been used."}

    if otp_record.farmotp_value != data.otp:
        return 400, {"detail": "Invalid OTP. Please ensure you are using the most recent code."}

    # 3. Update User Password
    user = get_object_or_404(User, email=data.email)
    user.set_password(data.new_password)
    user.save()

    # 4. Mark OTP as used
    otp_record.farmotp_usage = True
    otp_record.save()

    return 200, {"success": True, "message": "Password reset successfully! Login with new password."}
