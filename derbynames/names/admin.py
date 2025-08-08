from django.contrib import admin
from import_export.admin import ImportExportMixin
from .models import DerbyName, DerbyJersey


@admin.register(DerbyName)
class DerbyNameAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(DerbyJersey)
class DerbyJerseyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)
