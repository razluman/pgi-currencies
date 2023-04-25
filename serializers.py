from rest_framework import serializers
from .models import Rate, Currency


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = ["currency", "name", "propagation"]


class RateSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    def get_name(self, obj):
        return obj.currency.name

    class Meta:
        model = Rate
        fields = ["id", "currency", "name", "date", "rate"]
