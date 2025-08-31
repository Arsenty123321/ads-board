from django.urls import path
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenRefreshView

from users.apps import UsersConfig
from users.views import UserCreateAPIView, UserListAPIView, UserRetrieveAPIView, UserUpdateAPIView, \
    UserDestroyAPIView, UserActivationView, CustomTokenObtainPairView, PasswordResetRequestView, \
    PasswordResetConfirmView

app_name = UsersConfig.name

urlpatterns = [
    path('users/register/', UserCreateAPIView.as_view(), name='register'),
    path('users/activate/<str:activation_code>/', UserActivationView.as_view(), name='activate'),
    path('users/', UserListAPIView.as_view(), name='user-list'),
    path('users/<int:pk>/', UserRetrieveAPIView.as_view(), name='user-get'),
    path('users/update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),
    path('users/delete/<int:pk>/', UserDestroyAPIView.as_view(), name='user-destroy'),
    path("login/", CustomTokenObtainPairView.as_view(permission_classes=(AllowAny,)), name="login"),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),
    path('reset-password/', PasswordResetRequestView.as_view(), name='reset-password'),
    path('reset-password-confirm/', PasswordResetConfirmView.as_view(), name='reset-password-confirm'),
]
