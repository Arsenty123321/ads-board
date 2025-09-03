from django.urls import reverse
from rest_framework import status

from ads.models import Advertisement
from rest_framework.test import APITestCase, APIClient
from users.models import User


class AdvertisementTests(APITestCase):

    def setUp(self):
        # Создаем пользователей
        self.user = User.objects.create(email='testuser@test.test', password='testpassword')
        self.admin = User.objects.create(email='admin@test.test', password='adminpassword', role='admin')
        self.other_user = User.objects.create(email='otheruser@test.test', password='otherpassword')

        # Создаем объявление
        self.ad = Advertisement.objects.create(
            title='Test Ad',
            price=100,
            description='Test Description',
            owner=self.user
        )

        # Клиенты для каждого пользователя
        self.client_user = APIClient()
        self.client_admin = APIClient()
        self.client_other = APIClient()

        # Авторизация клиентов
        self.client_user.force_authenticate(user=self.user)
        self.client_admin.force_authenticate(user=self.admin)
        self.client_other.force_authenticate(user=self.other_user)

    def test_create_advertisement(self):
        """Тест создания объявления."""
        url = reverse('ads:ad_create')
        data = {'title': 'New Ad', 'price': 200, 'description': 'New Description'}
        response = self.client_user.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Advertisement.objects.count(), 2)

    def test_create_advertisement_unauthorized(self):
        """Тест создания объявления без авторизации."""
        url = reverse('ads:ad_create')
        data = {'title': 'New Ad', 'price': 200, 'description': 'New Description'}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_advertisements(self):
        """Тест получения списка объявлений."""
        url = reverse('ads:ad_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_advertisement(self):
        """Тест получения конкретного объявления."""
        url = reverse('ads:ad_retrieve', kwargs={'pk': self.ad.pk})
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Test Ad')

    def test_retrieve_advertisement_unauthorized(self):
        """Тест получения объявления без авторизации."""
        url = reverse('ads:ad_retrieve', kwargs={'pk': self.ad.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_advertisement_owner(self):
        """Тест обновления объявления владельцем."""
        url = reverse('ads:ad_update', kwargs={'pk': self.ad.pk})
        data = {'title': 'Updated Ad', 'price': 150, 'description': 'Updated Description'}
        response = self.client_user.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Ad')

    def test_update_advertisement_admin(self):
        """Тест обновления объявления администратором."""
        url = reverse('ads:ad_update', kwargs={'pk': self.ad.pk})
        data = {'title': 'Updated Ad', 'price': 150, 'description': 'Updated Description'}
        response = self.client_admin.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.title, 'Updated Ad')

    def test_update_advertisement_not_owner(self):
        """Тест обновления объявления не владельцем."""
        url = reverse('ads:ad_update', kwargs={'pk': self.ad.pk})
        data = {'title': 'Updated Ad', 'price': 150, 'description': 'Updated Description'}
        response = self.client_other.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_advertisement_owner(self):
        """Тест удаления объявления владельцем."""
        url = reverse('ads:ad_delete', kwargs={'pk': self.ad.pk})
        response = self.client_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Advertisement.objects.count(), 0)

    def test_delete_advertisement_admin(self):
        """Тест удаления объявления администратором."""
        url = reverse('ads:ad_delete', kwargs={'pk': self.ad.pk})
        response = self.client_admin.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Advertisement.objects.count(), 0)

    def test_delete_advertisement_not_owner(self):
        """Тест удаления объявления не владельцем."""
        url = reverse('ads:ad_delete', kwargs={'pk': self.ad.pk})
        response = self.client_other.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
