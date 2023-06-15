from django.urls import path, include
from rest_framework import routers
from .views import (
    CurrencyViewSet,
    RateViewSet,
    RateAdminViewSet,
    RateListView,
    rates_list,
    rates_list_htmx,
)


router = routers.SimpleRouter()
router.register("currency", CurrencyViewSet, basename="currency")
router.register("rate", RateViewSet, basename="rate")
router.register("admin/rate", RateAdminViewSet, basename="admin-rate")

app_name = "pgi_currencies"
urlpatterns = [
    path("api/", include(router.urls)),
    # path("rate/", RateListView.as_view(), name="rate-list"),
    # path("test-htmx/", test_htmx, name="test-htmx"),
    path("rate/", rates_list, name="rates-list"),
    path("rate-list-htmx/<int:page_number>/", rates_list_htmx, name="rates-list-htmx"),
]
