from django.urls import path, include
from rest_framework import routers
from .views import (
    CurrencyViewSet,
    RateViewSet,
    RateAdminViewSet,
    CurrencyTableView,
    RateTableView,
    rate_exchange,
    toggle_currency_display,
)

router = routers.SimpleRouter()
router.register("currency", CurrencyViewSet, basename="currency")
router.register("rate", RateViewSet, basename="rate")
router.register("admin/rate", RateAdminViewSet, basename="admin-rate")

app_name = "pgi_currencies"
urlpatterns = [
    path("api/", include(router.urls)),
    path("", rate_exchange, name="rates-list"),
    path("devise/", CurrencyTableView.as_view(), name="currencies-list"),
    path("cours/", RateTableView.as_view(), name="rates-list"),
    path(
        "toggle-currency-display/<str:currency>/",
        toggle_currency_display,
        name="toggle-currency-display",
    ),
]
