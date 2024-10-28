from decimal import Decimal

from rest_framework import serializers
from django.db import transaction as db_transaction
from .models import Wallet, Asset, TransactionEvent
from .services import buy_from_exchange

class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['balance', 'blocked']


class TransactionSerializer(serializers.Serializer):
    asset_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=20, decimal_places=10)
    transaction_type = serializers.ChoiceField(choices=['buy', 'sell'])

    def validate_quantity(self, quantity):
        if quantity <= 0:
            raise serializers.ValidationError("Quantity must be greater than zero.")
        return quantity

    def validate(self, data):
        user = self.context['request'].user
        asset_id = data.get('asset_id')
        transaction_type = data.get('transaction_type')
        quantity = data.get('quantity')
        
        # Ensure asset exists and wallet is available
        try:
            asset = Asset.objects.get(id=asset_id)
            wallet= Wallet.objects.select_for_update().get(user=user)
        except Asset.DoesNotExist:
            raise serializers.ValidationError("Asset not found.")
        except Wallet.DoesNotExist:
            raise serializers.ValidationError("Wallet for this asset not found.")

        # Check balance and holdings based on transaction type
        if transaction_type == 'buy':
            total_cost = asset.buy_price * quantity
            if wallet.balance < total_cost:
                raise serializers.ValidationError("Insufficient balance for this purchase.")
            data['total_cost'] = total_cost

        elif transaction_type == 'sell':
            if wallet.quantity < quantity:
                raise serializers.ValidationError("Insufficient quantity of asset to sell.")
            data['total_sale'] = asset.sell_price * quantity

        # Attach validated asset and wallet to data
        data['asset'] = asset
        data['wallet'] = wallet
        return data

    def create(self, validated_data):
        transaction_type = validated_data['transaction_type']
        quantity = validated_data['quantity']
        asset = validated_data['asset']
        wallet = validated_data['wallet']
        total_cost = validated_data.get('total_cost')
        total_sale = validated_data.get('total_sale')

        with db_transaction.atomic():
            if transaction_type == 'buy':
                transaction_event = TransactionEvent.objects.create(
                    wallet=wallet,
                    initial_balance=wallet.balance,
                    amount=total_cost,
                    end_balance = wallet.balance - total_cost,
                    status='pending',
                    transaction_type='buy',
                    description=f"Purchase of {quantity} {asset.symbol}"
                )
                wallet = wallet.block_funds(total_cost)
                if total_cost > Decimal('10.0'):
                    result = buy_from_exchange(asset.symbol, total_cost)
                    transaction_event.finalize_transaction(result)

            elif transaction_type == 'sell':
                wallet.quantity -= quantity
                wallet.update_balance(total_sale)
                transaction_event = TransactionEvent.objects.create(
                    wallet=wallet,
                    initial_balance=wallet.balance,
                    amount=total_sale,
                    end_balance=wallet.balance,
                    transaction_type='sell',
                    status='completed',
                    description=f"Sale of {quantity} {asset.symbol}"
                )
                wallet.save()
                transaction_event.save()
            
            return transaction_event
        
