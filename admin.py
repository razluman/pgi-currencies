from typing import Any
import datetime
from django.contrib import admin
from import_export.resources import ModelResource
from import_export.admin import ImportExportMixin
from .models import Currency, Rate


class CreatedUpdatedModelAdmin(ImportExportMixin, admin.ModelAdmin):
    exclude = ["created_by", "updated_by"]

    def save_model(self, request: Any, obj: Any, form: Any, change: Any) -> None:
        user = request.user
        obj.updated_by = user
        if not change:
            obj.created_by = user
        return super().save_model(request, obj, form, change)


@admin.register(Currency)
class CurrencyAdmin(CreatedUpdatedModelAdmin):
    list_display = (
        "currency",
        "name",
        "propagation",
        "active",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    )
    ordering = ("currency",)
    list_filter = ["active"]
    search_fields = ["currency"]

    class CurrencyResource(ModelResource):
        def before_import_row(self, row, row_number=None, **kwargs):
            row["created_by"] = kwargs["user"].id
            row["updated_by"] = kwargs["user"].id
            return super().before_import_row(row, row_number, **kwargs)

        class Meta:
            model = Currency
            skip_unchanged = True
            report_skipped = True
            exclude = ("id",)
            import_id_fields = ("currency", "name", "propagation")

    resource_class = CurrencyResource


@admin.register(Rate)
class RateAdmin(CreatedUpdatedModelAdmin):
    list_display = (
        "date",
        "currency",
        "rate",
        "created_by",
        "created_at",
        "updated_by",
        "updated_at",
    )
    ordering = ["-date", "currency"]
    search_fields = ["date", "currency__currency"]
    list_filter = ["currency__active"]
    autocomplete_fields = ["currency"]

    class RateResource(ModelResource):
        def before_import_row(self, row, row_number=None, **kwargs):
            row["created_by"] = kwargs["user"].id
            row["updated_by"] = kwargs["user"].id
            return super().before_import_row(row, row_number, **kwargs)

        def skip_row(self, instance, original, row, import_validation_errors=None):
            date = instance.date
            if isinstance(date, datetime.datetime):
                date = date.date()
            if Rate.objects.filter(  # pylint:disable=no-member
                currency=instance.currency, date=date
            ).exists():
                return True
            return super().skip_row(instance, original, row, import_validation_errors)

        class Meta:
            model = Rate
            skip_unchanged = True
            report_skipped = True

    resource_class = RateResource
