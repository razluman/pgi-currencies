from typing import Any, Dict, List
from django.shortcuts import HttpResponse, render
from django.views.decorators.http import require_POST
from django.db.models.query import QuerySet
from django.views.generic.list import ListView
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from django_tables2.views import SingleTableMixin
from django_filters.views import FilterView
from .serializers import CurrencySerializer, RateSerializer
from .models import Currency, Rate
from .permissions import IsRateAdmin
from .tables import CurrencyTable, CurrencyFilter, RateTable, RateFilter


class CurrencyViewSet(ReadOnlyModelViewSet):
    serializer_class = CurrencySerializer

    def get_queryset(self):
        queryset = Currency.objects.all().order_by("currency")

        active = self.request.GET.get("active")
        if active and active == "y":
            queryset = queryset.filter(active=True)
        if active and active == "n":
            queryset = queryset.filter(active=False)

        contains = self.request.GET.get("contains")
        if contains:
            queryset = queryset.filter(
                Q(currency__icontains=contains) | Q(name__icontains=contains)
            )
        return queryset


class RateViewSet(ReadOnlyModelViewSet):
    serializer_class = RateSerializer

    def get_queryset(self):
        queryset = Rate.objects.all().order_by("-date", "currency")
        currency = self.request.GET.get("currency")
        if currency:
            queryset = queryset.filter(currency__currency__iexact=currency)
        year = self.request.GET.get("year")
        if year:
            queryset = queryset.filter(date__year=year)
        month = self.request.GET.get("month")
        if month:
            queryset = queryset.filter(date__month=month)
        return queryset


class RateAdminViewSet(
    CreateModelMixin,
    RetrieveModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    permission_classes = [IsRateAdmin]
    serializer_class = RateSerializer

    def get_queryset(self):
        queryset = Rate.objects.all().order_by("-date", "currency")
        currency = self.request.GET.get("currency")
        if currency:
            queryset = queryset.filter(currency__currency__iexact=currency)
        year = self.request.GET.get("year")
        if year:
            queryset = queryset.filter(date__year=year)
        month = self.request.GET.get("month")
        if month:
            queryset = queryset.filter(date__month=month)
        return queryset

    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(created_by=user, updated_by=user)

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)


class Suppr_CurrencyListView(ListView):
    model = Currency
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        object_list = Currency.objects.all().order_by("currency")
        mycurrencies = self.request.session.get("mycurrencies")
        if not mycurrencies:
            active_currencies = Currency.objects.filter(active=True)
            mycurrencies = [currency.currency for currency in active_currencies]
            self.request.session["mycurrencies"] = mycurrencies
        active = self.request.GET.get("active")
        if active == "2":
            object_list = object_list.filter(currency__in=mycurrencies)
        if active == "3":
            object_list = object_list.exclude(currency__in=mycurrencies)
        currency = self.request.GET.get("currency")
        if currency:
            object_list = object_list.filter(
                Q(currency__icontains=currency)
                | Q(name__icontains=currency)
                | Q(propagation__icontains=currency)
            )
        return object_list

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hx_target"] = "#currencylist"
        get_copy = self.request.GET.copy()
        if get_copy.get("page"):
            get_copy.pop("page")
        context["get_copy"] = get_copy
        return context

    def get_template_names(self) -> List[str]:
        if self.request.htmx:
            return "pgi_currencies/currency_list_table.html"
        return super().get_template_names()


class Suppr_RateListView(ListView):
    model = Rate
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        mycurrencies = self.request.session.get("mycurrencies")
        if not mycurrencies:
            active_currencies = Currency.objects.filter(active=True)
            mycurrencies = [currency.currency for currency in active_currencies]
            self.request.session["mycurrencies"] = mycurrencies
        object_list = Rate.objects.filter(currency__in=mycurrencies).order_by(
            "-date", "currency"
        )
        currency = self.request.GET.get("currency")
        if currency:
            object_list = object_list.filter(currency=currency)
        year = self.request.GET.get("year")
        if year:
            object_list = object_list.filter(date__year=year)
        month = self.request.GET.get("month")
        if month:
            object_list = object_list.filter(date__month=month)
        return object_list

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hx_target"] = self.get_hx_target()
        get_copy = self.request.GET.copy()
        if get_copy.get("page"):
            get_copy.pop("page")
        context["get_copy"] = get_copy
        return context

    def get_template_names(self) -> List[str]:
        if self.request.htmx:
            return "pgi_currencies/rate_list_table.html"
        return super().get_template_names()

    def get_hx_target(self):
        return "#ratelist"


class CurrencyTableView(SingleTableMixin, FilterView):
    model = Currency
    table_class = CurrencyTable
    template_name = "pgi_currencies/currency_table_view.html"
    filterset_class = CurrencyFilter
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        object_list = Currency.objects.all().order_by("currency")
        mycurrencies = self.request.session.get("mycurrencies")
        if not mycurrencies:
            active_currencies = Currency.objects.filter(active=True)
            mycurrencies = [currency.currency for currency in active_currencies]
            self.request.session["mycurrencies"] = mycurrencies
        return object_list

    def get_template_names(self) -> List[str]:
        if self.request.htmx:
            return "pgi_currencies/bootstrap5_table2_htmx.html"
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hx_target"] = "#currency-table"
        return context


class RateTableView(SingleTableMixin, FilterView):
    model = Rate
    table_class = RateTable
    template_name = "pgi_currencies/rate_table_view.html"
    filterset_class = RateFilter
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        mycurrencies = self.request.session.get("mycurrencies")
        if not mycurrencies:
            active_currencies = Currency.objects.filter(active=True)
            mycurrencies = [currency.currency for currency in active_currencies]
            self.request.session["mycurrencies"] = mycurrencies
        object_list = Rate.objects.filter(currency__in=mycurrencies).order_by(
            "-date", "currency"
        )
        return object_list

    def get_template_names(self) -> List[str]:
        if self.request.htmx:
            return "pgi_currencies/bulma_table2_htmx.html"
        return super().get_template_names()

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context["hx_target"] = "#rate-table"
        return context


@require_POST
def toggle_currency_display(request, currency):
    currency = currency.upper()
    mycurrencies = request.session.get("mycurrencies")
    if not mycurrencies:
        active_currencies = Currency.objects.filter(active=True)
        mycurrencies = [currency.currency for currency in active_currencies]
    if currency in mycurrencies:
        mycurrencies.remove(currency)
    else:
        mycurrencies.append(currency)
    request.session["mycurrencies"] = mycurrencies
    return HttpResponse("")


def rate_exchange(request):
    if request.htmx:
        if request.GET.get("input") == "currency":
            datalist = None
            wizards = request.GET.get("currencyinput")
            if wizards:
                datalist = Currency.objects.filter(
                    currency__icontains=wizards
                ).order_by("currency")[:5]
            return render(
                request,
                "pgi_currencies/datalist.html",
                {"datalist": datalist},
            )
        if request.GET.get("input") == "form":
            return HttpResponse(
                f"<p>{request.GET.get('currencyinput')}</p><p>{request.GET.get('dateinput')}</p>"
            )
    return render(request, "pgi_currencies/rate_exchange.html", {})
