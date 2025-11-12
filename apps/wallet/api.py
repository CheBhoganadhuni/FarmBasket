from ninja import Router
from ninja.security import django_auth
from apps.accounts.models import Wallet
from apps.accounts.auth import AuthBearer

wallet_router = Router(tags=['wallet'])
auth = AuthBearer()

import logging

logger = logging.getLogger(__name__)

@wallet_router.get("/balance", auth=auth)
def wallet_balance(request):
    wallet, _ = Wallet.objects.get_or_create(user=request.auth)
    logger.info(f"Wallet API accessed by user {request.user.email} returning balance {wallet.balance}")
    print(f"Wallet API accessed by user {request.user.email} returning balance {wallet.balance}")
    print("Authorization header:", request.headers.get('Authorization'))
    
    return {'balance': float(wallet.balance)}
