from django.urls import path

from .views import WalletView, AssetTransactionView


urlpatterns = [
    path('wallet/', WalletView.as_view(), name='wallet'),
    path('transactions/', AssetTransactionView.as_view(), name='create-transaction'),
]