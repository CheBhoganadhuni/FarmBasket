from django.urls import path
from . import views
from .api import user_wallet_view

app_name = 'accounts'

urlpatterns = [
    # Authentication pages
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    
    # Profile
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    
    # Password reset
    path('auth/password-reset/', views.password_reset_request_view, name='password_reset_request'),
    path('auth/password-reset/confirm/', views.password_reset_confirm_view, name='password_reset_confirm'),
    
    
    # Address management
    path('profile/addresses/', views.addresses_view, name='addresses'),
    
    # Legal pages
    path('terms/', views.terms_of_service, name='terms'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('wishlist/', views.wishlist_view, name='wishlist'),
    path('contact/', views.contact_view, name='contact'),
    path('user/wallet/', user_wallet_view, name='user_wallet'),

    
    path('', views.home_view, name='home'),  # ✅ Add this


]
