from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Wallet
from .serializers import WalletSerializer, TransactionSerializer



class WalletView(RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletSerializer

    def get_object(self):
        # Return only the wallet associated with the authenticated user
        return Wallet.objects.get(user=self.request.user)
    
class AssetTransactionView(CreateAPIView):
    """Handles asset transactions (buy/sell) with minimal view logic."""
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def post(self, request):
        serializer = TransactionSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            transaction_event = serializer.save()
            return Response(
                {"message": f"Transaction {transaction_event.transaction_type} completed successfully"},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
