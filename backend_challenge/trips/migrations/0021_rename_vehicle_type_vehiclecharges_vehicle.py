# Generated by Django 4.1.8 on 2023-07-25 17:57

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0020_ordervehicle_vehiclecharges_delete_ordercharges"),
    ]

    operations = [
        migrations.RenameField(
            model_name="vehiclecharges",
            old_name="vehicle_type",
            new_name="vehicle",
        ),
    ]
