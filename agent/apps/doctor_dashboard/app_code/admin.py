from django.contrib import admin
from .models import ExampleEntity


@admin.register(ExampleEntity)
class ExampleEntityAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("created_at",)