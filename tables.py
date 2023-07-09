from django.urls import reverse
from django.db.models import Q
from django.utils.html import format_html
from django.utils.translation import gettext as _
import django_tables2 as tables
from django_filters import FilterSet, CharFilter, ChoiceFilter, NumberFilter
from .models import Currency, Rate


class CurrencyTable(tables.Table):
    currency = tables.Column(
        verbose_name=_("Cur"), attrs={"td": {"class": "text-center"}}
    )
    in_rate = tables.Column(empty_values=(), orderable=False, verbose_name=_("Visible"))

    class Meta:
        model = Currency
        fields = ["currency", "name", "propagation", "in_rate"]

    def render_in_rate(self, record):
        if record.currency in self.request.session.get("mycurrencies", []):
            checked = "checked=" "checked" ""
        else:
            checked = ""
        div = f"""
        <div id="switch{record.currency}divinput" class="form-check form-switch d-flex justify-content-center">
            <input id="switch{record.currency}"
                    type="checkbox"
                    class="form-check-input"
                    hx-post="{reverse("pgi_currencies:toggle-currency-display", args=[record.currency])}"
                    hx-target="#none"
                    {checked}>
            <label for="switch{record.currency}">
            </label>
        </div>
        <div id="switch{record.currency}divspinner" class="form-check form-switch d-flex justify-content-center d-none">
            <i class="fas fa-spinner fa-spin form-check-input"></i>
        </div>
        """
        return format_html(div)


class CurrencyFilter(FilterSet):
    search = CharFilter(method="search_filter", label="Search")
    in_rate = ChoiceFilter(
        method="in_rate_filter",
        choices=(
            (1, "All currencies"),
            (2, "Visible in rates"),
            (3, "Hidden in rates"),
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


class RateTable(tables.Table):
    currency = tables.Column(
        verbose_name=_("Cur"), attrs={"td": {"class": "text-center"}}
    )
    date = tables.Column(attrs={"td": {"class": "text-center"}})

    class Meta:
        model = Rate
        fields = ["currency", "date", "rate"]
        row_attrs = {"class": "align-middle"}

    def render_date(self, value):
        return value.strftime("%d/%m/%y")

    def render_rate(self, value, record):
        div = f"""
        <div class="text-end">
            <span id="span{record.id}">{f"{value:,.2f}".replace(",", " ").replace(".", ",")}</span>
            <a class="link-success" onclick='document.querySelector("#rate{record.id}").classList.toggle("d-none");document.querySelector("#span{record.id}").classList.toggle("fw-bold");'>
                <i class="fa-solid fa-calculator float-end ms-3" aria-hidden="true"></i>
            </a>
        </div>
        <div id="rate{record.id}" class="d-none">
            <div class="mb-1">
                <input type="text"
                    id="devise{record.id}"
                    oninput='rateConvert("{record.id}", {value})'
                    onblur='amountFormatOnBlur("#devise{record.id}")'
                    placeholder="{record.currency}"
                    class="form-control form-control-sm form-control-smaller text-end">
            </div>
            <input type="text"
                id="ariary{record.id}"
                oninput='rateConvert("{record.id}", {value}, false)'
                onblur='amountFormatOnBlur("#ariary{record.id}")'
                placeholder="MGA"
                class="form-control form-control-sm form-control-smaller text-end">
        </div>
        """
        return format_html(div)


class RateFilter(FilterSet):
    currency = CharFilter(field_name="currency__currency", lookup_expr="icontains")
    year = NumberFilter(field_name="date__year", lookup_expr="exact")
    month = NumberFilter(field_name="date__month", lookup_expr="exact")

    class Meta:
        model = Rate
        fields = ["currency", "year", "month"]
