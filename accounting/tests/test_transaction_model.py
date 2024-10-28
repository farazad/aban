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

@pytest.mark.django_db
def test_wallet_update_balance(user):
    wallet = Wallet.objects.create(user=user, balance=Decimal("1000.00"))
    
    # Update the balance
    updated_wallet = wallet.update_balance(commit=True)
    
    # Assertions
    updated_wallet.refresh_from_db()
    assert updated_wallet.balance == Decimal("1000.00")
    assert updated_wallet.blocked == Decimal("0.00")

@pytest.mark.django_db
def test_block_funds(user):
    wallet = Wallet.objects.create(user=user, balance=Decimal("1000.00"))
    
    # Block funds
    wallet.block_funds(Decimal("200.00"))
    
    # Assertions
    wallet.refresh_from_db()
    assert wallet.blocked == Decimal("200.00")
    assert wallet.balance == Decimal("800.00")

@pytest.mark.django_db
def test_unblock_funds(user):
    wallet = Wallet.objects.create(user=user, balance=Decimal("800.00"), blocked=Decimal("200.00"))
    
    # Unblock funds
    wallet.unblock_funds(Decimal("200.00"))
    
    # Assertions
    wallet.refresh_from_db()
    assert wallet.blocked == Decimal("0.00")
    assert wallet.balance == Decimal("1000.00")