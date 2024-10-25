from rest_framework import viewsets, serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import User
from .serializers import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action == 'create':
            self.permission_classes = []
        return super().get_permissions()
    


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims, if any
        token['phone_number'] = user.phone_number
        return token

    def validate(self, attrs):
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = User.objects.filter(phone_number=phone_number).first()

        if user and user.check_password(password):
            return super().validate(attrs)
        raise serializers.ValidationError('Invalid credentials')

class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer