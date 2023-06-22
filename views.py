from typing import Any, Dict, List
from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.http import require_GET
from django.utils.http import urlencode
from django.db.models.query import QuerySet
from django.views.generic.list import ListView
from django.db.models import Q
from rest_framework.viewsets import ReadOnlyModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin
from .serializers import CurrencySerializer, RateSerializer
from .models import Currency, Rate
from .permissions import IsRateAdmin


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


class CurrencyListView(ListView):
    model = Currency
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        object_list = Currency.objects.all().order_by("currency")
        active = self.request.GET.get("active")
        if active == "2":
            object_list = object_list.filter(active=True)
        if active == "3":
            object_list = object_list.filter(active=False)
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
        context["hx_target"] = self.get_hx_target()
        get_copy = self.request.GET.copy()
        if get_copy.get("page"):
            get_copy.pop("page")
        context["get_copy"] = get_copy
        return context

    def get_template_names(self) -> List[str]:
        if self.request.htmx:
            return "pgi_currencies/currency_list_table.html"
        return super().get_template_names()

    def get_hx_target(self):
        return "#currencylist"


class RateListView(ListView):
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
