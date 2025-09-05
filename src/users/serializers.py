from django.contrib.auth import authenticate
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from config import settings
from config.settings import FRONTEND_SITE_URL
from users.models import User
from users.tasks import send_password_reset_link_email


class EmptySerializer(serializers.Serializer):
    pass


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор модели пользователя."""

    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "phone",
            "email",
            "password",
            "image",
        )
        extra_kwargs = {
            'password': {'write_only': True},
            'last_name': {'required': False},
            'phone': {'required': False},
        }

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен содержать минимум 8 символов.")
        return value


class CustomTokenObtainPairSerializer(serializers.Serializer):
    """Сериализатор кастомного представления работы с токеном авторизации."""
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        # Проверка существования пользователя
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Неверные учетные данные, повторите попытку.")

        # Проверка активации пользователя
        if not user.is_active:
            raise serializers.ValidationError(
                "Пользователь не активирован, пройдите активацию или воспользуйтесь функцией сброса пароля."
            )

        # Аутентификация пользователя
        user_auth = authenticate(email=email, password=password)
        if user_auth is None:
            raise serializers.ValidationError("Неверные учетные данные, повторите попытку.")

        # Генерация токенов
        refresh = RefreshToken.for_user(user_auth)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class PasswordResetRequestSerializer(serializers.Serializer):
    """Сериализатор запроса на сброс пароля."""
    email = serializers.EmailField(required=True)

    def validate_email(self, email):
        # Проверка, существует ли пользователь с таким email
        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError("Пользователь с таким email не найден.")
        return email

    def save(self):
        email = self.validated_data['email']
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.pk))

        request = self.context.get('request')

        # Формируем ссылку для сброса пароля и отправляем на email пользователя
        if settings.DEBUG:
            reset_link = f"{request.scheme}://{request.get_host()}/reset-password-confirm/{uidb64}/{token}/"
        else:
            reset_link = f"{FRONTEND_SITE_URL}/reset-password-confirm/{uidb64}/{token}/"

        send_password_reset_link_email.delay(email, reset_link)  # Вызов задачи Celery

        if settings.DEBUG:
            print(f"#### DEBUG: Send Reset link: {reset_link}")  # DEBUG


class PasswordResetConfirmSerializer(serializers.Serializer):
    """Сериализатор установки нового пароля после запроса сброса."""
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        """Проверка токена на сброс пароля"""
        uidb64 = attrs.get('uid')
        token = attrs.get('token')
        # new_password = attrs.get('new_password')

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            raise serializers.ValidationError({'error': 'Неверный UID или пользователь не найден.'})

        token_generator = PasswordResetTokenGenerator()
        if not token_generator.check_token(user, token):
            raise serializers.ValidationError({'error': 'Недействительный или просроченный токен.'})

        attrs['user'] = user
        return attrs

    def save(self):
        user = self.validated_data['user']
        new_password = self.validated_data['new_password']
        user.set_password(new_password)
        # На случай если ранее проходили регистрацию, но не активировали учетную запись
        user.is_active = True
        user.activation_code = ''
        user.save()
