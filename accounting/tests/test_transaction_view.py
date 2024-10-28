import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from decimal import Decimal
from accounting.models import Wallet, TransactionEvent, Asset


#TODO must mock respose of buy_from_exchange
@pytest.mark.django_db
def test_create_transaction(api_client, user, asset):
    
    # Define the transaction data
    transaction_data = {
        'asset_id':Asset.objects.all().first().id,
        "quantity": 5.0,
        "transaction_type": "buy",
    }

    # Make the API request to create a transaction
    url = reverse('create-transaction')
    api_client.force_authenticate(user=user)
    response = api_client.post(url, data=transaction_data, format='json')

    # Assertions
    assert response.status_code == status.HTTP_200_OK
    assert TransactionEvent.objects.count() == 1
    transaction = TransactionEvent.objects.first()
    assert transaction.amount == Decimal(5*10)
    assert transaction.transaction_type == "buy"
    assert transaction.status in ["canceled", "completed"]