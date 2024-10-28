from decimal import Decimal

from django.db import models, transaction as db_transaction
from django.utils import timezone

from user.models import User

TRANSACTION_TYPES = (
    ('deposit', 'Deposit'),
    ('withdrawal', 'Withdrawal'),
)

TRANSACTION_STATUS = (
    ('pending', 'Pending'),
    ('completed', 'Completed'),
    ('canceled', 'Canceled'),
)

class Asset(models.Model):
    """Represents a tradable asset."""
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=10, unique=True)
    buy_price = models.DecimalField(max_digits=20, decimal_places=10)
    sell_price = models.DecimalField(max_digits=20, decimal_places=10)
    order_volume = models.DecimalField(max_digits=20, decimal_places=10)

    def __str__(self):
        return f"{self.name} ({self.symbol})"


class Wallet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    balance = models.DecimalField(max_digits=20, decimal_places=10, default=Decimal('0.0'), null=False)
    blocked = models.DecimalField(max_digits=40, decimal_places=20, default=Decimal('0.0'),null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user}'s Wallet"

    def update_balance(self, commit=True):
        """Updates the wallet's balance by a given amount. Uses select_for_update for concurrency."""
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            wallet.blocked = 0
            wallet.modified_at = timezone.now()
            if commit:
                wallet.save()
            return wallet

    def block_funds(self, amount):
        """Block funds for pending transactions."""
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            if amount > wallet.balance:
                raise ValueError("Insufficient available funds")
            wallet.blocked += amount
            wallet.balance -= amount
            wallet.save()
        return wallet

    def unblock_funds(self, amount):
        """Unblock funds if a transaction is canceled or completed."""
        with db_transaction.atomic():
            wallet = Wallet.objects.select_for_update().get(pk=self.pk)
            if amount > wallet.blocked:
                raise ValueError("Insufficient blocked funds")
            wallet.blocked -= amount
            wallet.balance += amount
            wallet.save()

        return wallet


class TransactionEvent(models.Model):
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, null=False)
    initial_balance = models.DecimalField(max_digits=20, decimal_places=10, null=False)
    amount = models.DecimalField(max_digits=20, decimal_places=10, null=False)
    end_balance = models.DecimalField(max_digits=20, decimal_places=10, null=False)
    transaction_type = models.CharField(choices=TRANSACTION_TYPES, max_length=10)
    status = models.CharField(choices=TRANSACTION_STATUS, max_length=10, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.transaction_type} of {self.amount} ({self.status}) on {self.timestamp}"

    # def save(self, *args, **kwargs):
    #     """Override save method to block/unblock/apply funds based on transaction status."""
    #     with db_transaction.atomic():
    #         wallet = Wallet.objects.select_for_update().get(pk=self.wallet.pk)
            
    #         if self.pk is None and self.status == 'pending':
    #             self.initial_balance = wallet.balance
    #             if self.transaction_type == 'withdrawal':
    #                 wallet.block_funds(self.amount)
    #                 self.change = -self.amount
    #             elif self.transaction_type == 'deposit':
    #                 wallet.update_balance(self.amount, commit=False)
    #                 self.change = self.amount

    #         if self.status == 'completed':
    #             if self.transaction_type == 'withdrawal':
    #                 wallet.update_balance(-self.amount)
    #             self.end_balance = wallet.balance

    #         if self.status == 'canceled':
    #             if self.transaction_type == 'withdrawal':
    #                 wallet.unblock_funds(self.amount)
    #             self.end_balance = wallet.balance

    #         super().save(*args, **kwargs)
    
    def finalize_transaction(self, success: bool):
        """Finalize the transaction based on the exchange result."""
        wallet = self.wallet
        with db_transaction.atomic():
            if success:
                # Deduct blocked funds and update wallet quantity
                wallet = wallet.update_balance(-self.amount)
                self.status = 'completed'
            else:
                # Unblock funds if transaction failed
                wallet = wallet.unblock_funds(self.amount)
                self.status = 'canceled'
            
            self.end_balance = wallet.balance
        self.save()
        wallet.save()

    @classmethod
    def get_pending_volume(cls, asset):
        """Calculate the total volume of pending buy transactions for a given asset."""
        return cls.objects.filter(transaction_type='buy', status='pending', wallet__asset=asset).aggregate(
            total_volume=models.Sum('amount')
        )['total_volume'] or Decimal('0.0')