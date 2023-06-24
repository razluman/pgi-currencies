from django.urls import reverse
from django.db.models import Q
from django.utils.html import format_html
import django_tables2 as tables
from django_filters import FilterSet, CharFilter, ChoiceFilter
from .models import Currency


class CurrencyTable(tables.Table):
    in_rate = tables.Column(empty_values=(), orderable=False)

    class Meta:
        model = Currency
        fields = ["currency", "name", "propagation", "in_rate"]

    def render_in_rate(self, record):
        if record.currency in self.request.session.get("mycurrencies", []):
            checked = "checked=" "checked" ""
        else:
            checked = ""
        div = """
        <div class="field">
                <input id="switch{}"
                        type="checkbox"
                        name="switchcurrency"
                        class="switch is-rounded is-small"
                        hx-post="{}"
                        hx-target="#none"
                        {}>
                <label for="switch{}"></label>
            </div>
        """
        return format_html(
            div,
            record.currency,
            reverse("pgi_currencies:toggle-currency-display", args=[record.currency]),
            checked,
            record.currency,
        )


class CurrencyFilter(FilterSet):
    search = CharFilter(method="search_filter", label="Search")
    in_rate = ChoiceFilter(
        method="in_rate_filter",
        choices=(
            (1, "Toutes les devises"),
            (2, "Devises dans les cours"),
            (3, "Devises hors des cours"),
        ),
    )

    class Meta:
        model = Currency
        fields = ["search", "in_rate"]

    def search_filter(self, queryset, name, value):
        return queryset.filter(
            Q(currency__icontains=value)
            | Q(name__icontains=value)
            | Q(propagation__icontains=value)
        )

    def in_rate_filter(self, queryset, name, value):
        mycurrencies = self.request.session.get("mycurrencies")
        if not mycurrencies:
            active_currencies = Currency.objects.filter(active=True)
            mycurrencies = [currency.currency for currency in active_currencies]
            self.request.session["mycurrencies"] = mycurrencies
        if value == "2":
            queryset = queryset.filter(currency__in=mycurrencies)
        if value == "3":
            queryset = queryset.exclude(currency__in=mycurrencies)
        return queryset
