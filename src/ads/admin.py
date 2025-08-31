from django.contrib import admin

from ads.models import Advertisement


@admin.register(Advertisement)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "author", "price", "created_at")
    search_fields = ("title", "author", "created_at")
