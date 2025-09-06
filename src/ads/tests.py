from django.urls import reverse
from rest_framework import status

from ads.models import Advertisement, Feedback
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

        # Создаем отзыв
        self.feedback = Feedback.objects.create(
            text='Test Feedback',
            owner=self.other_user,
            ad=self.ad
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

    def test_my_ad_list(self):
        """Тест просмотра списка своих объявлений."""
        url = reverse('ads:ad_my_list')
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_search_advertisements(self):
        """Тест поиска объявлений по названию."""
        # Создаем дополнительные объявления для проверки поиска
        self.ad1 = Advertisement.objects.create(
            title='Test Ad 1',
            price=100,
            description='Test Description 1',
            owner=self.user
        )
        self.ad2 = Advertisement.objects.create(
            title='Another Ad',
            price=200,
            description='Test Description 2',
            owner=self.user
        )
        self.ad3 = Advertisement.objects.create(
            title='New Ad',
            price=300,
            description='Test Description 3',
            owner=self.user
        )

        url = reverse('ads:ad_list')
        # Ищем по части названия объявления
        response = self.client.get(url, {'search': 'Test'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)

        # Ищем по точному названию объявления
        response = self.client.get(url, {'search': 'Another'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Ищем по названию из другого объявления
        response = self.client.get(url, {'search': 'New'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

        # Ищем по несуществующему названию объявления
        response = self.client.get(url, {'search': 'NonExistent'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

    def test_create_feedback(self):
        """Тест создания отзыва."""
        url = reverse('ads:feedback_create', kwargs={'ad_id': self.ad.pk})
        data = {'text': 'New Feedback'}
        response = self.client_other.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Feedback.objects.count(), 2)

    def test_list_feedbacks(self):
        """Тест просмотра всех отзывов из определенного объявления."""
        url = reverse('ads:feedbacks_for_ad', kwargs={'ad_id': self.ad.pk})
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_feedback(self):
        """Тест просмотра одного отзыва."""
        url = reverse('ads:feedback_retrieve', kwargs={'pk': self.feedback.pk})
        response = self.client_user.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'Test Feedback')

    def test_update_feedback_owner(self):
        """Тест обновления отзыва владельцем."""
        url = reverse('ads:feedback_update', kwargs={'pk': self.feedback.pk})
        data = {'text': 'Updated Feedback'}
        response = self.client_other.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feedback.refresh_from_db()
        self.assertEqual(self.feedback.text, 'Updated Feedback')

    def test_update_feedback_not_owner(self):
        """Тест обновления отзыва не владельцем."""
        url = reverse('ads:feedback_update', kwargs={'pk': self.feedback.pk})
        data = {'text': 'Updated Feedback'}
        response = self.client_user.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_feedback_owner(self):
        """Тест удаления отзыва владельцем."""
        url = reverse('ads:feedback_delete', kwargs={'pk': self.feedback.pk})
        response = self.client_other.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_delete_feedback_admin(self):
        """Тест удаления отзыва администратором."""
        url = reverse('ads:feedback_delete', kwargs={'pk': self.feedback.pk})
        response = self.client_admin.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Feedback.objects.count(), 0)

    def test_delete_feedback_not_owner(self):
        """Тест удаления отзыва не владельцем."""
        url = reverse('ads:feedback_delete', kwargs={'pk': self.feedback.pk})
        response = self.client_user.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_my_feedback_list(self):
        """Тест просмотра списка своих отзывов."""
        url = reverse('ads:feedback_my_list')
        response = self.client_other.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
