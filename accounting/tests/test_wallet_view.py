import pytest
from django.urls import reverse
from rest_framework import status



@pytest.mark.django_db
def test_authenticated_user_can_access_wallet(api_client, user, wallet):
    # Log in the user and authenticate
    api_client.force_authenticate(user=user)
    
    # Retrieve wallet data
    url = reverse('wallet')  # Assuming 'wallet-view' is the name in urls.py
    response = api_client.get(url)
    
    # Check response status and data
    assert response.status_code == status.HTTP_200_OK
    assert response.data['balance'] == str(wallet.balance)


@pytest.mark.django_db
def test_unauthenticated_user_cannot_access_wallet(api_client):
    url = reverse('wallet')
    response = api_client.get(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


