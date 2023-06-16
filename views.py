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


class RateListView(ListView):
    model = Rate
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        object_list = Rate.objects.filter(currency__active=True).order_by(
            "-date", "-rate"
        )
        currency = self.request.GET.get("currency")
        if currency:
            object_list = object_list.filter(currency=currency)
        return object_list

    def get_context_data(self, **kwargs: Any) -> Dict[str, Any]:
        context = super().get_context_data(**kwargs)
        page_obj = context["page_obj"]
        get_copy = self.get_copy()
        context["page_first"] = f"?page=1&{get_copy}"
        if page_obj.has_previous():
            context[
                "page_previous"
            ] = f"?page={page_obj.previous_page_number()}&{get_copy}"
        if page_obj.has_next():
            context["page_next"] = f"?page={page_obj.next_page_number()}&{get_copy}"
        context["page_last"] = f"?page={page_obj.paginator.num_pages}&{get_copy}"
        # display = self.request.session.get("display")
        # if display is None:
        # display = Currency.objects.filter(active=True)
        # context["display"] = display
        # not_display = Currency.objects.all().exclude(currency__in=context["display"])
        # context["not_display"] = not_display
        # get_copy = self.request.GET.copy()
        # if get_copy.get("page"):
        # get_copy.pop("page")
        # context["get_copy"] = get_copy
        return context

    def get_template_names(self) -> List[str]:
        if self.request.htmx:
            return "pgi_currencies/rate_list_table.html"
        return super().get_template_names()

    def get_copy(self):
        get_copy = self.request.GET.copy()
        if get_copy.get("page"):
            get_copy.pop("page")
        return urlencode(get_copy)


@require_GET
def rates_list(request):
    page_number = request.GET.get("page", "1")
    object_list = Rate.objects.filter(currency__active=True).order_by("-date", "-rate")
    paginator = Paginator(object_list, 20)
    page_obj = paginator.get_page(page_number)
    if request.htmx:
        template_name = "pgi_currencies/rate_list_table.html"
    else:
        template_name = "pgi_currencies/rate_list.html"
    context = {"page_obj": page_obj}
    return render(request, template_name, context)


def rates_list_render(request, page_number, template_name):
    object_list = Rate.objects.filter(currency__active=True).order_by("-date", "-rate")
    currency = request.GET.get("currency")
    if currency:
        object_list = object_list.filter(currency=currency)
    paginator = Paginator(object_list, 20)
    page_obj = paginator.get_page(page_number)
    context = {"page_obj": page_obj}
    return render(request, template_name, context)


def get_context_data(request, context):
    get_copy = request.GET.copy()
    if get_copy.get("page"):
        get_copy.pop("page")
    context["get_copy"] = get_copy


def old_rates_list(request):
    request.session["mycurrencies"] = ["EUR", "USD"]
    mycurrencies = request.session.get("mycurrencies")
    object_list = Rate.objects.filter(currency__active=True).order_by("-date", "-rate")
    currency = request.GET.get("currency")
    if currency:
        object_list = object_list.filter(currency=currency)
    paginator = Paginator(object_list, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    return render(
        request,
        "pgi_currencies/rate_list.html",
        {"page_obj": page_obj, "mycurrencies": mycurrencies},
    )
