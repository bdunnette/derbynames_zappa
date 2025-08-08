from django.contrib import admin
from django.db.models import Q
from import_export.admin import ImportExportMixin
from .models import DerbyName, DerbyJersey


@admin.register(DerbyName)
class DerbyNameAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    search_fields = ("name",)
    ordering = ("name",)


class HasImageFilter(admin.SimpleListFilter):
    title = "Has Image"
    parameter_name = "has_image"

    def lookups(self, request, model_admin):
        return (
            ("yes", "Yes"),
            ("no", "No"),
        )

    def queryset(self, request, queryset):
        if self.value() == "yes":
            return queryset.filter(Q(image__isnull=False) & ~Q(image__exact=""))
        elif self.value() == "no":
            return queryset.filter(Q(image__isnull=True) | Q(image__exact=""))
        return queryset


@admin.register(DerbyJersey)
class DerbyJerseyAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ("name", "created_at", "updated_at")
    list_filter = (HasImageFilter,)
    search_fields = ("name",)
    ordering = ("name",)
