from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from ads.models import Advertisement, Feedback
from ads.paginators import CustomPagination
from ads.serilazers import AdSerializer, AdsListSerializer, FeedbackSerializer
from users.permissions import IsOwner, IsAdmin


class AdsCreateAPIView(generics.CreateAPIView):
    """Контроллер создания объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]


class AdsListAPIView(generics.ListAPIView):
    """Контроллер просмотра списка всех объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdsListSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


class AdsRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для просмотра объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = [IsAuthenticated]


class AdsUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для изменения объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class AdsDestroyAPIView(generics.DestroyAPIView):
    """Контроллер удаления объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class FeedbackCreateAPIView(generics.CreateAPIView):
    """Контроллер создания отзыва."""
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
    """Контроллер для просмотра всех отзывов объявления."""
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination

    def get_queryset(self):
        # Получаем id объявления из URL
        ad_id = self.kwargs['ad_id']
        # Фильтруем отзывы по объявлению
        return Feedback.objects.filter(ad=ad_id)


class FeedbackRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для просмотра одного отзыва."""

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = [IsAuthenticated]


class FeedbackUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для изменения отзыва"""

    serializer_class = FeedbackSerializer
    queryset = Feedback.objects.all()
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)


class FeedbackDestroyAPIView(generics.DestroyAPIView):
    """Контроллер для удаления отзыва"""

    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (IsAuthenticated, IsOwner | IsAdmin,)
