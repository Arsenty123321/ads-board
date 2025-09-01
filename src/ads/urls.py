from django.urls import path

from ads.apps import AdsConfig
from ads.views import AdsCreateAPIView, AdsListAPIView, AdsRetrieveAPIView, AdsUpdateAPIView, AdsDestroyAPIView

app_name = AdsConfig.name

urlpatterns = [
    path("create/", AdsCreateAPIView.as_view(), name="ad_create"),
    path("list/", AdsListAPIView.as_view(), name="ad_list"),
    path("<int:pk>/", AdsRetrieveAPIView.as_view(), name="ad_retrieve"),
    path("<int:pk>/update/", AdsUpdateAPIView.as_view(), name="ad_update"),
    path("<int:pk>/delete/", AdsDestroyAPIView.as_view(), name="ad_delete"),
]
