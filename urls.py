from django.urls import path, include
from rest_framework import routers
from .views import (
    CurrencyViewSet,
    RateViewSet,
    RateAdminViewSet,
    CurrencyListView,
    RateListView,
    toggle_currency_display,
    CurrencyTableView,
)

router = routers.SimpleRouter()
router.register("currency", CurrencyViewSet, basename="currency")
router.register("rate", RateViewSet, basename="rate")
router.register("admin/rate", RateAdminViewSet, basename="admin-rate")

app_name = "pgi_currencies"
urlpatterns = [
    path("api/", include(router.urls)),
    path("devise/", CurrencyListView.as_view(), name="currencies-list"),
    path(
        "toggle-currency-display/<str:currency>/",
        toggle_currency_display,
        name="toggle-currency-display",
    ),
    path("cours/", RateListView.as_view(), name="rates-list"),
    path("currency/", CurrencyTableView.as_view(), name="cur-list"),
]
