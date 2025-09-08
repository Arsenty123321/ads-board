from django.contrib import admin

from ads.models import Advertisement, Feedback


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "owner", "created_at")
    search_fields = ("title", "owner")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("id", "ad", "owner", "created_at")
    search_fields = ("title", "owner")
