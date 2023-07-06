from django.urls import reverse
from django.db.models import Q
from django.utils.html import format_html
import django_tables2 as tables
from django_filters import FilterSet, CharFilter, ChoiceFilter, NumberFilter
from .models import Currency, Rate


class CurrencyTable(tables.Table):
    currency = tables.Column(verbose_name="Dev", attrs={"td": {"class": "text-center"}})
    in_rate = tables.Column(empty_values=(), orderable=False, verbose_name="Visible")

    class Meta:
        model = Currency
        fields = ["currency", "name", "propagation", "in_rate"]

    def render_in_rate(self, record):
        if record.currency in self.request.session.get("mycurrencies", []):
            checked = "checked=" "checked" ""
        else:
            checked = ""
        div = """
        <div class="form-check form-switch d-flex justify-content-center">
            <input id="switch{}"
                    type="checkbox"
                    name="switchcurrency"
                    class="form-check-input"
                    hx-post="{}"
                    hx-indicator="#switchindicator{}"
                    hx-target="#none"
                    {}>
            <label for="switch{}">
                <i class="fas fa-xs fa-spinner fa-pulse htmx-indicator float-end ms-2 mt-2" id="switchindicator{}"></i>
            </label>
        </div>
        """
        return format_html(
            div,
            record.currency,
            reverse("pgi_currencies:toggle-currency-display", args=[record.currency]),
            record.currency,
            checked,
            record.currency,
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


class RateTable(tables.Table):
    currency = tables.Column(verbose_name="Dev", attrs={"td": {"class": "text-center"}})
    date = tables.Column(attrs={"td": {"class": "text-center"}})

    class Meta:
        model = Rate
        fields = ["currency", "date", "rate"]
        row_attrs = {"class": "align-middle"}

    def render_date(self, value):
        return value.strftime("%d/%m/%y")

    def render_rate(self, value, record):
        div = """
        <div class="text-end">
            <span id="span{}">{}</span>
            <a class="link-success" onclick='document.querySelector("#rate{}").classList.toggle("d-none");document.querySelector("#span{}").classList.toggle("fw-bold");'>
                <i class="fa-solid fa-calculator float-end ms-3" aria-hidden="true"></i>
            </a>
        </div>
        <div id="rate{}" class="d-none">
            <div class="mb-1">
                <input type="text"
                    id="devise{}"
                    oninput='rateConvert("{}", {})'
                    onblur='amountFormatOnBlur("#devise{}")'
                    placeholder="{}"
                    class="form-control form-control-sm form-control-smaller text-end">
            </div>
            <input type="text"
                id="ariary{}"
                oninput='rateConvert("{}", {}, false)'
                onblur='amountFormatOnBlur("#ariary{}")'
                placeholder="MGA"
                class="form-control form-control-sm form-control-smaller text-end">
        </div>
        """
        return format_html(
            div,
            # rate
            record.id,
            f"{value:,.2f}".replace(",", " ").replace(".", ","),
            record.id,
            record.id,
            record.id,
            # devise
            record.id,
            record.id,
            value,
            record.id,
            record.currency,
            # ariary
            record.id,
            record.id,
            value,
            record.id,
        )

    def old_render_rate(self, value, record):
        div = """
        <div class="text-center fw-bold">{}</div>
        <div class="mb-1">
            <input type="text"
                    id="devise{}"
                    oninput='rateConvert("{}", {})'
                    onblur='amountFormatOnBlur("#devise{}")'
                    placeholder="{}"
                    class="form-control form-control-sm form-control-smaller text-end">
        </div>
        <input type="text"
                id="ariary{}"
                oninput='rateConvert("{}", {}, false)'
                onblur='amountFormatOnBlur("#ariary{}")'
                placeholder="MGA"
                class="form-control form-control-sm form-control-smaller text-end">
        """
        return format_html(
            div,
            f"{value:,.2f}".replace(",", " ").replace(".", ","),
            record.id,
            record.id,
            record.rate,
            record.id,
            record.currency,
            record.id,
            record.id,
            record.rate,
            record.id,
        )


class RateFilter(FilterSet):
    currency = CharFilter(field_name="currency__currency", lookup_expr="icontains")
    year = NumberFilter(field_name="date__year", lookup_expr="exact")
    month = NumberFilter(field_name="date__month", lookup_expr="exact")

    class Meta:
        model = Rate
        fields = ["currency", "year", "month"]
