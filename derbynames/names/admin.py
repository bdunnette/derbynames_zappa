from django.contrib import admin
from import_export.admin import ImportExportMixin
from .models import DerbyName, DerbyJersey


@admin.register(DerbyName)
class DerbyNameAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


# Allow filtering of jerseys based on whether they have an image
class HasImageFilter(admin.SimpleListFilter):
    title = "Has Image"
    parameter_name = "has_image"

    def lookups(self, request, model_admin):
        return (
            ("Yes", "Yes"),
            ("No", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "Yes":
            return queryset.filter(image__isnull=False)
        elif self.value() == "No":
            return queryset.filter(image__isnull=True)
        return queryset


@admin.register(DerbyJersey)
class DerbyJerseyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = ("created_at", "updated_at", HasImageFilter)
    search_fields = ("name",)
    ordering = ("name",)
