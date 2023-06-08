from django.urls import path, include
from rest_framework import routers
from .views import CurrencyViewSet, RateViewSet, RateAdminViewSet, RatesTable, RatePage
from .models import Currency


router = routers.SimpleRouter()
router.register("currency", CurrencyViewSet, basename="currency")
router.register("rate", RateViewSet, basename="rate")
router.register("admin/rate", RateAdminViewSet, basename="admin-rate")

app_name = "pgi_currencies"
urlpatterns = [
    path("api/", include(router.urls)),
    path("rate/", RatesTable().as_view()),
    # path("rate/", RatePage().as_view()),
]
