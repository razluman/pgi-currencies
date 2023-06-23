from django.utils.html import format_html
import django_tables2 as tables
from django_filters import FilterSet
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
                        {}>
                <label for="switch{}"></label>
            </div>
        """
        return format_html(div, record.currency, checked, record.currency)


class CurrencyFilter(FilterSet):
    class Meta:
        model = Currency
        fields = {"propagation": ["icontains"]}
