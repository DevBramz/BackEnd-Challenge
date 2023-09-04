# Generated by Django 4.1.8 on 2023-06-05 00:25

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0006_alter_location_cords"),
        ("routeplanning", "0001_initial"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="routesettings",
            name="end_address",
        ),
        migrations.RemoveField(
            model_name="routesettings",
            name="start_address",
        ),
        migrations.AddField(
            model_name="routesettings",
            name="end_point",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="route_end",
                to="locations.location",
                verbose_name="end point",
            ),
        ),
        migrations.AddField(
            model_name="routesettings",
            name="start_point",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.PROTECT,
                to="locations.location",
                verbose_name="start point",
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name="routesettings",
            name="departure_time",
            field=models.TimeField(blank=True, default=django.utils.timezone.now),
        ),
    ]
