from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework import status
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from unittest.mock import patch

User = get_user_model()


class UserTests(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create(
            email='testuser@test.com',
            password='testpassword',
            first_name='Test',
            last_name='User',
            role='user',
            is_active=True
        )

        self.admin = User.objects.create(
            email='admin@test.com',
            password='adminpassword',
            first_name='Admin',
            last_name='User',
            role='admin',
            is_active=True,
            is_staff=True
        )

        self.user.token = RefreshToken.for_user(self.user)
        self.admin_token = RefreshToken.for_user(self.admin)

    def test_user_registration(self):
        """Тест регистрации нового пользователя."""
        url = reverse('users:register')
        data = {
            "first_name": "NewUser",
            "email": "newuser@test.com",
            "password": "newpassword123",
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='newuser@test.com').exists())

    # def test_user_login(self):
    #     """Тест входа пользователя."""
    #     url = reverse('users:login')
    #     data = {
    #         "email": "testuser@test.com",
    #         "password": "testpassword"
    #     }
    #     user_auth = authenticate(email='testuser@test.com', password='testpassword')
    #
    #     response = self.client.post(url, data, format='json')
    #     print(f"XXXXXXXXXXXXXXXXXX {user_auth} Response data: {response.data}")
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     self.assertIn('access', response.data)
    #     self.assertIn('refresh', response.data)

    def test_user_activation(self):
        """Тест активации пользователя."""
        user = User.objects.create(
            email='inactiveuser@test.com',
            password='testpassword',
            first_name='Inactive',
            last_name='User',
            is_active=False,
            activation_code='testcode'
        )
        url = reverse('users:activate', kwargs={'activation_code': 'testcode'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_user_list(self):
        """Тест получения списка пользователей."""
        url = reverse('users:user-list')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_user_retrieve(self):
        """Тест получения информации о конкретном пользователе."""
        url = reverse('users:user-get', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.token.access_token}')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], 'testuser@test.com')

    def test_user_update(self):
        """Тест обновления информации о пользователе."""
        url = reverse('users:user-update', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.user.token.access_token}')
        data = {"first_name": "Updated"}
        response = self.client.patch(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_user_delete(self):
        """Тест удаления пользователя."""
        url = reverse('users:user-destroy', kwargs={'pk': self.user.pk})
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.admin_token.access_token}')
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(pk=self.user.pk).exists())

    def test_password_reset_request(self):
        """Тест запроса на сброс пароля."""
        url = reverse('users:reset-password')
        with patch('users.tasks.send_password_reset_link_email.delay') as mock_send_email:
            data = {"email": "testuser@test.com"}
            response = self.client.post(url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(response.data['message'], 'Ссылка для сброса пароля отправлена на вашу почту.')
            mock_send_email.assert_called_once()

    def test_password_reset_confirm(self):
        """Тест подтверждения сброса пароля."""
        user = User.objects.create(
            email='resettest@test.com',
            password='oldpassword',
            first_name='Reset',
            last_name='User',
            is_active=True
        )
        token_generator = PasswordResetTokenGenerator()
        token = token_generator.make_token(user)
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

        url = reverse('users:reset-password-confirm')
        data = {
            "uid": uidb64,
            "token": token,
            "new_password": "newpassword123"
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['message'], 'Пароль успешно изменен.')
        user.refresh_from_db()
        self.assertTrue(user.check_password('newpassword123'))

    def test_token_refresh(self):
        """Тест обновления токена."""
        url = reverse('users:token_refresh')
        data = {"refresh": str(self.user.token)}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
