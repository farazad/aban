import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from user.models import User
from accounting.models import Wallet, Asset

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(username='testuser', password='testpass')

@pytest.fixture
def asset(db):
    return Asset.objects.create(name='TestAsset', symbol='TA', buy_price=10, sell_price=9)

@pytest.fixture
def wallet(user, asset, db):
    return Wallet.objects.create(user=user, asset=asset, quantity=10, balance=100)

@pytest.mark.django_db
def test_authenticated_user_can_access_wallet(api_client, user, wallet):
    # Log in the user and authenticate
    api_client.force_authenticate(user=user)
    
    # Retrieve wallet data
    url = reverse('wallet-view')  # Assuming 'wallet-view' is the name in urls.py
    response = api_client.get(url)
    
    # Check response status and data
    assert response.status_code == status.HTTP_200_OK
    assert response.data['balance'] == str(wallet.balance)
    assert response.data['quantity'] == wallet.quantity


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_wallet(api_client):
    url = reverse('wallet-view')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_authenticated_user_without_wallet(api_client, user):
    # Authenticate the user without a wallet
    api_client.force_authenticate(user=user)
    
    url = reverse('wallet-view')
    response = api_client.get(url)
    
    # Adjust error handling as per your logic; assuming it raises a 404
    assert response.status_code == status.HTTP_404_NOT_FOUND