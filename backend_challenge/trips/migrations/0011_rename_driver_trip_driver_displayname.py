# Generated by Django 4.1.8 on 2023-06-17 21:19

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("trips", "0010_trip_estimated_completion_time"),
    ]

    operations = [
        migrations.RenameField(
            model_name="trip",
            old_name="driver",
            new_name="driver_displayName",
        ),
    ]
