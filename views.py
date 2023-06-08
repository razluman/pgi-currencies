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
