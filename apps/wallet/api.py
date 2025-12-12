from ninja import Router
from apps.accounts.api import auth

wallet_router = Router(tags=['Wallet'])

@wallet_router.get("/balance", response=dict, auth=auth)
def get_wallet_balance(request):
    """Get user wallet balance"""
    return {"balance": float(request.auth.wallet_balance)}
