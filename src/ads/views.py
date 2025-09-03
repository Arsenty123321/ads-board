from rest_framework import generics
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated, AllowAny

from ads.models import Advertisement, Feedback
from ads.paginators import CustomPagination
from ads.serilazers import AdSerializer, AdListSerializer, FeedbackSerializer
from users.permissions import IsOwner, IsAdmin


class AdCreateAPIView(generics.CreateAPIView):
    """Создание объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]


class AdListAPIView(generics.ListAPIView):
    """Просмотр списка всех объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title']
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


class AdRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр одного объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]


class AdUpdateAPIView(generics.UpdateAPIView):
    """Изменение объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class AdDestroyAPIView(generics.DestroyAPIView):
    """Удаление объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class MyAdListAPIView(generics.ListAPIView):
    """Просмотр списка своих объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = (IsAuthenticated, IsOwner,)
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(owner=user)


class FeedbackCreateAPIView(generics.CreateAPIView):
    """Создание отзыва."""
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        # Передаем ad_id в контекст сериализатора
        context = super().get_serializer_context()
        # Добавляем ad_id в контекст, если это не фейковый вызов Swagger
        if not getattr(self, 'swagger_fake_view', False):
            context['ad_id'] = self.kwargs['ad_id']
        return context


class FeedbackListAPIView(generics.ListAPIView):
    """Просмотр всех отзывов из определенного объявления."""
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        # Получаем id объявления из URL
        ad_id = self.kwargs['ad_id']
        # Фильтруем отзывы по объявлению
        return Feedback.objects.filter(ad=ad_id)


class FeedbackRetrieveAPIView(generics.RetrieveAPIView):
    """Просмотр одного отзыва."""

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]


class FeedbackUpdateAPIView(generics.UpdateAPIView):
    """Изменение отзыва."""

    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class FeedbackDestroyAPIView(generics.DestroyAPIView):
    """Удаление отзыва."""

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class MyFeedbackListAPIView(generics.ListAPIView):
    """Просмотр списка своих отзывов."""

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (IsAuthenticated, IsOwner)
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(owner=user)
