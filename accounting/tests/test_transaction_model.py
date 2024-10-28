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

@pytest.mark.django_db
def test_finalize_transaction_failure(user, wallet):
    # Setup wallet and transaction
    transaction = TransactionEvent.objects.create(
        wallet=wallet,
        initial_balance=wallet.balance,
        amount=Decimal("20.00"),
        end_balance = wallet.balance - Decimal("20.00"),
        transaction_type="withdrawal"
    )
    wallet.block_funds(Decimal("20.00"))

    # Finalize the transaction as failed
    transaction.finalize_transaction(success=False)
    
    # Assertions
    transaction.refresh_from_db()
    wallet.refresh_from_db()
    assert transaction.status == "canceled"
    assert wallet.balance == Decimal("100.0")

@pytest.mark.django_db
def test_get_pending_volume(wallet):
    # Setup wallet and transactions
    TransactionEvent.objects.create(wallet=wallet,initial_balance= wallet.balance, amount=Decimal("150.00"), end_balance=wallet.balance - Decimal(150.0), transaction_type="buy", status="pending")
    TransactionEvent.objects.create(wallet=wallet,initial_balance= wallet.balance, amount=Decimal("100.00"), end_balance=wallet.balance - Decimal(100.0), transaction_type="buy", status="pending")
    TransactionEvent.objects.create(wallet=wallet,initial_balance= wallet.balance, amount=Decimal("50.00"), end_balance=wallet.balance - Decimal(50.0), transaction_type="sell", status="pending")

    # Assertions
    total_pending = TransactionEvent.get_pending_volume(wallet)
    assert total_pending == Decimal("250.00") 