# Generated by Django 3.2.18 on 2023-07-09 06:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pgi_currencies', '0004_alter_rate_currency'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='currency',
            field=models.CharField(max_length=3, primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name='currency',
            name='name',
            field=models.CharField(max_length=50),
        ),
        migrations.AlterField(
            model_name='rate',
            name='currency',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='rates', to='pgi_currencies.currency'),
        ),
        migrations.AlterField(
            model_name='rate',
            name='rate',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
