from typing import List
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from datetime import timedelta
from ninja import Router, File
from ninja.errors import HttpError
from ninja.files import UploadedFile

from rest_framework_simplejwt.tokens import RefreshToken

from .models import User, Address, PasswordResetToken
from .schemas import (
    UserRegisterSchema, 
    UserLoginSchema,
    UserSchema, 
    TokenSchema,
    PasswordResetRequestSchema, 
    PasswordResetConfirmSchema,
    UserUpdateSchema, 
    AddressCreateSchema, 
    AddressSchema, 
    MessageSchema, 
    ChangePasswordSchema,
    AuthSchema  # ✅ Added
)
from .auth import (
    authenticate_user, create_access_token, create_refresh_token,
    get_password_hash, AuthBearer
)
from .emails import send_welcome_email, send_password_reset_email  # ✅ Changed from tasks to emails
from django.conf import settings
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

from .schemas import GoogleLoginSchema

router = Router(tags=['Authentication'])
auth = AuthBearer()


@router.post("/register", response=AuthSchema)
def register(request, data: UserRegisterSchema):
    """Register new user"""
    # Check if email already exists
    if User.objects.filter(email=data.email).exists():
        raise HttpError(400, "Email already registered")
    
    # Create user
    user = User.objects.create_user(
        email=data.email,
        password=data.password,
        first_name=data.first_name,
        last_name=data.last_name,
        phone=data.phone
    )
    
    # ✅ Generate JWT tokens
    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    
    # Send welcome email
    try:
        send_welcome_email(user)
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
    
    # ✅ Convert user to UserSchema
    user_data = UserSchema.from_orm(user)
    
    return {
        'access': str(access),
        'refresh': str(refresh),
        'user': user_data
    }

from django.shortcuts import redirect
import requests

@router.get("/google/login")
def google_login_init(request):
    """Start Google OAuth2 Flow"""
    scope = "email profile openid"
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?response_type=code"
        f"&client_id={settings.GOOGLE_CLIENT_ID}"
        f"&redirect_uri={settings.GOOGLE_REDIRECT_URI}"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&prompt=select_account"
    )
    return redirect(auth_url)


@router.get("/google/callback")
def google_callback(request, code: str):
    """Handle Google OAuth2 Callback"""
    
    # 1. Exchange code for tokens
    token_url = "https://oauth2.googleapis.com/token"
    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
    }
    
    res = requests.post(token_url, data=token_data)
    if not res.ok:
        raise HttpError(400, f"Failed to get token from Google: {res.text}")
    
    tokens = res.json()
    id_token_str = tokens.get("id_token")
    access_token_google = tokens.get("access_token")
    
    # 2. Get User Info
    user_info_res = requests.get(
        "https://www.googleapis.com/oauth2/v3/userinfo",
        headers={"Authorization": f"Bearer {access_token_google}"}
    )
    
    if not user_info_res.ok:
         raise HttpError(400, "Failed to fetch user info from Google")
         
    user_info = user_info_res.json()
    email = user_info.get("email")
    email_verified = user_info.get("email_verified")
    
    if not email_verified:
        raise HttpError(400, "Google email not verified")

    # Name fields
    given_name = user_info.get("given_name", "")
    family_name = user_info.get("family_name", "")

    # 3. Find or Create User
    try:
        user = User.objects.get(email=email, is_active=True)
        created = False
    except User.DoesNotExist:
        user = User.objects.create_user(
            email=email,
            password=None,
            first_name=given_name,
            last_name=family_name,
        )
        user.set_unusable_password()
        created = True
    
    # Update social avatar if provided
    picture = user_info.get("picture")
    if picture and not user.social_avatar_url:
        user.social_avatar_url = picture
        
    user.save()
    
    # Send welcome email if new user
    if created:
        try:
            from apps.accounts.emails import send_welcome_email
            send_welcome_email(user)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")

    # 4. Generate App Tokens (JWT)
    from django.utils import timezone
    user.last_login = timezone.now()
    user.save(update_fields=["last_login"])

    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    # 5. Redirect to Success Page with Tokens
    # We redirect to a simple HTML page that saves tokens to localStorage and forwards to profile
    return redirect(f"/google-success/?access={access_token}&refresh={refresh_token}&superuser={str(user.is_superuser).lower()}")


@router.post("/login", response=TokenSchema)
def login(request, data: UserLoginSchema):
    """User login"""

    user = authenticate_user(data.email, data.password)
    
    if not user:
        raise HttpError(401, "Invalid email or password")
    
    # Update last login
    user.last_login = timezone.now()
    user.save(update_fields=['last_login'])
    
    # Generate tokens
    access_token = create_access_token(data={"sub": str(user.id)})
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "is_staff": user.is_staff,
        "is_superuser": user.is_superuser,
        "email": user.email,  # optional extras
        "full_name": user.get_full_name(),  # optional
    }


@router.get("/me", response=UserSchema, auth=auth)
def get_current_user(request):
    """Get current user profile"""
    try:
        user = request.auth
        # print(f"Authenticated user: {user.email}")
        return user
    except Exception as e:
        print(f"Error in /me endpoint: {e}")
        import traceback
        traceback.print_exc()
        raise


@router.put("/me", response=UserSchema, auth=auth)
def update_current_user(request, data: UserUpdateSchema):
    """Update current user profile"""
    
    user = request.auth
    
    for field, value in data.dict(exclude_unset=True).items():
        setattr(user, field, value)
    
    user.save()
    return user


@router.post("/password-reset/request", response=MessageSchema)
def request_password_reset(request, data: PasswordResetRequestSchema):
    """Request password reset"""
    
    try:
        user = User.objects.get(email=data.email, is_active=True)
        
        # Check if social user (don't send reset email)
        if user.social_avatar_url:
            raise HttpError(400, "You are logged in via Google. You do not need to reset your password.")
        else:
            # Create reset token
            reset_token = PasswordResetToken.objects.create(
                user=user,
                expires_at=timezone.now() + timedelta(hours=1)
            )
            
            # Generate reset URL (Dynamic)
            # Remove trailing slash from SITE_URL if present to avoid double slash
            site_url = settings.SITE_URL.rstrip('/')
            
            # Construct the FULL frontend URL that handles the reset
            # Matching urls.py: path('auth/password-reset/confirm/', ...)
            # Matching views.py: token = request.GET.get('token')
            reset_url = f"{site_url}/auth/password-reset/confirm/?token={reset_token.token}"
            
            # Send reset email
            send_password_reset_email(user, reset_url)
        
    except User.DoesNotExist:
        pass  # Don't reveal if email exists
    
    return {
        "message": "If your email is registered, you will receive a password reset link",
        "success": True
    }


@router.post("/password-reset/confirm", response=MessageSchema)
def confirm_password_reset(request, data: PasswordResetConfirmSchema):
    """Confirm password reset"""
    
    try:
        reset_token = PasswordResetToken.objects.get(token=data.token)
        
        if not reset_token.is_valid:
            raise HttpError(400, "Invalid or expired reset token")
        
        # Update password
        user = reset_token.user
        user.set_password(data.new_password)
        user.save()
        
        # Mark token as used
        reset_token.used = True
        reset_token.save()
        
        return {"message": "Password reset successful", "success": True}
        
    except PasswordResetToken.DoesNotExist:
        raise HttpError(400, "Invalid or expired reset token")


# ===== ADDRESS ENDPOINTS =====

@router.get("/addresses", response=List[AddressSchema], auth=auth)
def get_addresses(request):
    """Get all addresses for logged-in user"""
    user = request.auth
    addresses = Address.objects.filter(user=user).order_by('-is_default', '-created_at')
    
    return [
        {
            'id': str(addr.id),
            'label': addr.label,
            'address_type': addr.address_type,
            'street_address': addr.street_address,
            'apartment': addr.apartment or '',
            'city': addr.city,
            'state': addr.state,
            'postal_code': addr.postal_code,
            'landmark': addr.landmark or '',
            'phone': addr.phone,
            'is_default': addr.is_default,
            'created_at': addr.created_at
        }
        for addr in addresses
    ]


@router.post("/addresses", response=AddressSchema, auth=auth)
def create_address(request, data: AddressCreateSchema):
    """Create a new address"""
    
    # If this is set as default, unset other defaults
    if data.is_default:
        Address.objects.filter(user=request.auth).update(is_default=False)
    
    address = Address.objects.create(
        user=request.auth,
        **data.dict()
    )
    return address


@router.put("/addresses/{address_id}", response=AddressSchema, auth=auth)
def update_address(request, address_id: str, data: AddressCreateSchema):
    """Update an address"""
    
    address = get_object_or_404(Address, id=address_id, user=request.auth)
    
    # If this is set as default, unset other defaults
    if data.is_default:
        Address.objects.filter(user=request.auth).exclude(id=address_id).update(is_default=False)
    
    for field, value in data.dict().items():
        setattr(address, field, value)
    
    address.save()
    return address


@router.delete("/addresses/{address_id}", response=MessageSchema, auth=auth)
def delete_address(request, address_id: str):
    """Delete address"""
    user = request.auth
    
    try:
        address = Address.objects.get(id=address_id, user=user)
        address.delete()
        
        return MessageSchema(
            success=True,
            message="Address deleted successfully"
        )
    except Address.DoesNotExist:
        return MessageSchema(
            success=False,
            message="Address not found"
        )


@router.post("/change-password", response=MessageSchema, auth=auth)
def change_password(request, data: ChangePasswordSchema):
    """Change password for logged-in user"""
    user = request.auth
    
    # Verify old password
    if not user.check_password(data.old_password):
        return MessageSchema(
            success=False,
            message="Current password is incorrect"
        )
    
    # Set new password
    user.set_password(data.new_password)
    user.save()
    
    return MessageSchema(
        success=True,
        message="Password changed successfully"
    )


@router.delete("/account", response=MessageSchema, auth=auth)
def delete_account(request):
    """Delete user account and all related data"""
    user = request.auth
    
    # This will cascade delete:
    # - Orders, OrderItems
    # - Cart, CartItems
    # - Wishlist
    # - Addresses
    # - Reviews
    user.delete()
    
    return MessageSchema(
        success=True,
        message="Account deleted successfully"
    )


import cloudinary
import cloudinary.uploader

@router.post("/upload-avatar", response=MessageSchema, auth=auth)
def upload_avatar(request, avatar: UploadedFile = File(...)):
    """Upload user avatar"""
    user = request.auth
    
    # Validate file type
    if not avatar.content_type.startswith('image/'):
        return MessageSchema(
            success=False,
            message="Invalid file type. Please upload an image."
        )
    
    # Validate file size (5MB max)
    if avatar.size > 5 * 1024 * 1024:
        return MessageSchema(
            success=False,
            message="File too large. Maximum size is 5MB."
        )
    
    try:
        # Generate unique filename (public_id)
        ext = avatar.name.split('.')[-1]
        public_id_name = f"{user.id}_{int(timezone.now().timestamp())}"
        
        # Direct upload to Cloudinary (like seed_products.py)
        upload_result = cloudinary.uploader.upload(
            avatar.file,
            folder="avatars",
            public_id=public_id_name,
            overwrite=True,
            resource_type="image"
        )
        
        # Save the public_id to the model field
        # The ImageField (with CloudinaryStorage) knows how to handle this
        user.avatar = upload_result['public_id']
        user.save()
        
        return MessageSchema(
            success=True,
            message="Avatar uploaded successfully",
            avatar_url=upload_result['secure_url']
        )
        
    except Exception as e:
        print(f"Avatar upload failed: {e}")
        return MessageSchema(
            success=False, 
            message="Failed to upload avatar. Please try again."
        )
    




@router.get("/wallet/balance", response=dict, auth=auth)
def get_wallet_balance(request):
    """Get user wallet balance"""
    return {"balance": float(request.auth.wallet_balance)}
