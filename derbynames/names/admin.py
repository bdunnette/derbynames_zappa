from django.contrib import admin

from .models import DerbyName


@admin.register(DerbyName)
class DerbyNameAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
