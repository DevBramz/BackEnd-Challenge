# Generated by Django 4.1.8 on 2023-06-14 15:56

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0002_remove_trip_code_trip_trip_code"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="trip",
            name="fuel_consumption",
        ),
        migrations.AlterField(
            model_name="trip",
            name="duration",
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
