import sys
# print("=" * 50)
# print("Loading config/api.py")
# print("Python path:", sys.path[0])
# print("=" * 50)

from ninja import NinjaAPI
from apps.accounts.api import router as accounts_router
from apps.catalog.api import router as catalog_router
from apps.cart.api import router as cart_router
from apps.orders.api import router as orders_router  # ✅ Add this
from apps.products.api import router as products_router
# api.add_router("/wallet/", wallet_router)


from ninja.security import django_auth


# print("Creating NinjaAPI instance...")
api = NinjaAPI(
    title="🧺 FarmBasket API",
    version="1.0.0",
    description="Premium Organic Farm E-commerce Platform",
    docs_url="/docs",
)
# print("NinjaAPI created successfully!")
print(">>> LOADING NINJA API")

# Register app routers
api.add_router("/auth/", accounts_router)
api.add_router('/admin', products_router)
api.add_router("/catalog/", catalog_router)
api.add_router("/cart/", cart_router)
api.add_router("/", orders_router)  # ✅ Add this


# api.add_router("/wallet/", wallet_router)

# Health check endpoint
@api.get("/health", tags=["System"])
def health_check(request):
    return {
        "status": "healthy",
        "service": "FarmBasket API",
        "version": "1.0.0"
    }
