# Generated by Django 4.1.8 on 2023-07-15 03:17

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0013_trip_actual_departure_time"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="trip",
            options={"ordering": ["-created_at"]},
        ),
    ]
