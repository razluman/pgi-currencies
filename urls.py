from django.urls import path, include
from rest_framework import routers
from iommi import Form, Table
from .views import CurrencyViewSet, RateViewSet, RateAdminViewSet, CurrencyPage
from .models import Currency

router = routers.SimpleRouter()
router.register("currency", CurrencyViewSet, basename="currency")
router.register("rate", RateViewSet, basename="rate")
router.register("admin/rate", RateAdminViewSet, basename="admin-rate")

app_name = "pgi_currencies"
urlpatterns = [
    path("api/", include(router.urls)),
    path("iommi-form-test/", Form.create(auto__model=Currency).as_view()),
    path("iommi-table-test/", Table(auto__model=Currency).as_view()),
    path("currency/", CurrencyPage().as_view()),
]
