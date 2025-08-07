from django.contrib import admin
from import_export.admin import ImportExportMixin
from .models import DerbyName


@admin.register(DerbyName)
class DerbyNameAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
