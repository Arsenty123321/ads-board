from django.urls import path

from ads.apps import AdsConfig
from ads.views import AdsCreateAPIView, AdsListAPIView, AdsRetrieveAPIView, AdsUpdateAPIView, AdsDestroyAPIView, \
    FeedbackListAPIView, FeedbackCreateAPIView, FeedbackRetrieveAPIView, FeedbackUpdateAPIView, FeedbackDestroyAPIView

app_name = AdsConfig.name

urlpatterns = [
    # Ads
    path("create/", AdsCreateAPIView.as_view(), name="ad_create"),
    path("list/", AdsListAPIView.as_view(), name="ad_list"),
    path("<int:pk>/", AdsRetrieveAPIView.as_view(), name="ad_retrieve"),
    path("<int:pk>/update/", AdsUpdateAPIView.as_view(), name="ad_update"),
    path("<int:pk>/delete/", AdsDestroyAPIView.as_view(), name="ad_delete"),
    # Feedbacks
    path("<int:ad_id>/feedbacks/", FeedbackListAPIView.as_view(), name="feedbacks_for_ad"),
    path("<int:ad_id>/feedback/create/", FeedbackCreateAPIView.as_view(), name="feedback_create"),
    path("feedback/<int:pk>/", FeedbackRetrieveAPIView.as_view(), name="feedback_retrieve"),
    path("feedback/<int:pk>/update/", FeedbackUpdateAPIView.as_view(), name="feedback_update"),
    path("feedback/<int:pk>/delete/", FeedbackDestroyAPIView.as_view(), name="feedback_delete"),
]
