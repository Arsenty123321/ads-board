from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from ads.models import Advertisement
from ads.paginators import CustomPagination
from ads.serilazers import AdsSerializer, AdsListSerializer
from users.permissions import IsOwner, IsAdmin


class AdsCreateAPIView(generics.CreateAPIView):
    """Контроллер создания объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdsSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        """Добавление автора объявления."""
        ad = serializer.save()
        ad.author = self.request.user
        ad.save()


class AdsListAPIView(generics.ListAPIView):
    """Контроллер просмотра списка всех объявлений."""

    queryset = Advertisement.objects.all()
    serializer_class = AdsListSerializer
    pagination_class = CustomPagination
    permission_classes = [AllowAny]


class AdsRetrieveAPIView(generics.RetrieveAPIView):
    """Контроллер для просмотра объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdsSerializer
    permission_classes = [IsAuthenticated]


class AdsUpdateAPIView(generics.UpdateAPIView):
    """Контроллер для изменения объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdsSerializer
    permission_classes = ( IsAuthenticated, IsOwner | IsAdmin,)


class AdsDestroyAPIView(generics.DestroyAPIView):
    """Контроллер удаления объявления."""

    queryset = Advertisement.objects.all()
    serializer_class = AdsSerializer
    permission_classes = ( IsAuthenticated, IsOwner | IsAdmin,)
