from ninja import NinjaAPI
from apps.accounts.api import router as accounts_router
from apps.catalog.api import router as catalog_router
from apps.cart.api import router as cart_router
from apps.orders.api import router as orders_router
from apps.products.api import router as products_router
from apps.wallet.api import wallet_router
from apps.otp.api import router as otp_router

# Handle Django Autoreload/Double-Import issue
# Monkey patch _validate to bypass the strict registry check in development
# This allows runserver to reload without crashing on "Already registered"
NinjaAPI._validate = lambda self: None

# Singleton NinjaAPI instance
api = NinjaAPI(
    title="🧺 FarmBasket API",
    version="1.0.0",
    description="Premium Organic Farm E-commerce Platform",
    docs_url="/docs",
    urls_namespace="farmbasket_api",
)

# Register routers
api.add_router("/auth/", accounts_router)
api.add_router('/admin', products_router)
api.add_router("/catalog/", catalog_router)
api.add_router("/cart/", cart_router)
api.add_router("/", orders_router)
api.add_router("/wallet/", wallet_router)
api.add_router("/otp/", otp_router)

# Health check
@api.get("/health", tags=["System"])
def health_check(request):
    return {
        "status": "healthy",
        "service": "FarmBasket API",
        "version": "1.0.0"
    }
