import pytest
from decimal import Decimal
from accounting.models import TransactionEvent, Wallet

@pytest.mark.django_db
def test_finalize_transaction_success(user, wallet):
    # Setup wallet and transaction
    transaction = TransactionEvent.objects.create(
        wallet=wallet,
        initial_balance=wallet.balance,
        amount=Decimal("20.00"),
        end_balance = wallet.balance - Decimal("20.00"),
        transaction_type="withdrawal"
    )
    wallet.block_funds(Decimal("20.00"))

    # Finalize the transaction as successful
    transaction.finalize_transaction(success=True)
    
    # Assertions
    transaction.refresh_from_db()
    wallet.refresh_from_db()
    assert transaction.status == "completed"
    assert wallet.balance == Decimal("80.0")