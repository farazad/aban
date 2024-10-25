from celery import shared_task
from .models import TransactionEvent, Wallet, Asset
from decimal import Decimal

@shared_task
def process_pending_transactions():
    assets = Asset.objects.all()
    for asset in assets:
        # Calculate pending volume
        pending_volume = TransactionEvent.get_pending_volume(asset)
        
        if pending_volume >= Decimal('10.0'):
            # Call exchange API to buy assets
            # Example: exchange_api.buy(asset.symbol, pending_volume)
            
            # If successful, distribute the purchased assets to each pending transaction
            pending_transactions = TransactionEvent.objects.filter(
                transaction_type='buy', status='pending', wallet__asset=asset
            )
            for transaction in pending_transactions:
                wallet = transaction.wallet
                wallet.quantity += transaction.amount / asset.buy_price  # Distribute assets
                wallet.update_balance(-transaction.amount)
                transaction.status = 'completed'
                transaction.end_balance = wallet.balance
                wallet.save()
                transaction.save()