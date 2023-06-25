from django.db import models
from django.contrib.auth.models import User


class Currency(models.Model):
    currency = models.CharField(primary_key=True, max_length=3, verbose_name="devise")
    name = models.CharField(max_length=50, verbose_name="nom")
    propagation = models.TextField(blank=True)
    active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_currencies",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="updated_currencies",
    )

    def __str__(self):
        return f"{self.currency}"

    def save(self, *args, **kwargs):
        self.currency = self.currency.strip().upper()
        self.name = self.name.strip()
        self.propagation = self.propagation.strip()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "currencies"


class Rate(models.Model):
    date = models.DateField()
    rate = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="cours")
    currency = models.ForeignKey(
        Currency, on_delete=models.CASCADE, related_name="rates", verbose_name="devise"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_rates",
    )
    updated_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="updated_rates",
    )

    def __str__(self):
        return f"{self.currency} {self.date} {self.rate}"

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["currency", "date"], name="currency_rate")
        ]
