import pytest
from rest_framework.test import APIClient
from user.models import User
from accounting.models import Wallet, Asset

@pytest.fixture
def api_client():
    return APIClient()

@pytest.fixture
def user(db):
    return User.objects.create_user(phone_number='09121111111', name='testuser', password='testpass')

@pytest.fixture
def asset(db):
    return Asset.objects.create(name='TestAsset', symbol='TA', buy_price=10, sell_price=9, order_volume=10000)

@pytest.fixture
def wallet(user, db):
    return Wallet.objects.get(user=user)