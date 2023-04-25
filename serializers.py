from rest_framework import serializers
from .models import Rate, Currency


class RateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rate
        fields = ["id", "currency", "date", "rate"]


class CurrencySerializer(serializers.ModelSerializer):
    rates = serializers.SerializerMethodField()

    class Meta:
        model = Currency
        fields = ["currency", "name", "propagation", "rates"]

    def get_rates(self, instance):
        queryset = instance.rates.order_by("-date")[:10]
        serializer = RateSerializer(queryset, many=True)
        return serializer.data
