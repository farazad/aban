
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from .views import UserViewSet, CustomTokenObtainPairView
# Set up a router if you're using ViewSets
router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Add router URLs (for ViewSets)
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('', include(router.urls)),

    # Add more paths if necessary
    # path('profile/', UserProfileView.as_view(), name='user-profile'),
]