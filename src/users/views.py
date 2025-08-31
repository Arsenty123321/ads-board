from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from config import settings
from users.models import User
from users.permissions import IsStaffOrSelf, IsStaff
from users.serializers import UserSerializer, EmptySerializer, PasswordResetRequestSerializer, \
    PasswordResetConfirmSerializer, CustomTokenObtainPairSerializer
from users.tasks import send_activation_email


class UserCreateAPIView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(user.password)
        user.generate_activation_code()

        user.save()
        self.send_activation_email(user)

    def send_activation_email(self, user):
        """Отправка активации на email через Celery."""

        activation_url = f'{self.request.scheme}://{self.request.get_host()}/users/activate/{user.activation_code}/'
        send_activation_email.delay(user.email, activation_url)  # Вызов задачи Celery
        if settings.DEBUG:
            print(f"#### DEBUG: Send Activate link: {activation_url} to {user.email}")


class UserActivationView(generics.GenericAPIView):
    serializer_class = EmptySerializer  # Calm down swagger
    permission_classes = [AllowAny]

    def get(self, request, activation_code):
        try:
            user = User.objects.get(activation_code=activation_code)
            user.is_active = True
            user.activation_code = ''
            user.save()
            return Response({'message': 'Пользователь успешно активирован'}, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'Неверный код активации'}, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(generics.GenericAPIView):
    def post(self, request):
        serializer = CustomTokenObtainPairSerializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data)
        return Response(serializer.errors, status=400)


class UserListAPIView(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsStaff]


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsStaffOrSelf]


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    permission_classes = [IsStaffOrSelf]


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = User.objects.all()
    permission_classes = [IsStaff]


class PasswordResetRequestView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Ссылка для сброса пароля отправлена на вашу почту.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Пароль успешно изменен.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
