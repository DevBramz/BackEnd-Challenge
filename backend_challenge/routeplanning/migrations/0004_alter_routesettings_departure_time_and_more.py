# Generated by Django 4.1.8 on 2023-06-06 23:59

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):
    dependencies = [
        ("locations", "0006_alter_location_cords"),
        ("routeplanning", "0003_remove_routesettings_selection"),
    ]

    operations = [
        migrations.AlterField(
            model_name="routesettings",
            name="departure_time",
            field=models.TimeField(
                blank=True,
                default=django.utils.timezone.now,
                help_text="set future time, will default to now, for eta calculation purposes",
            ),
        ),
        migrations.AlterField(
            model_name="routesettings",
            name="end_point",
            field=models.ForeignKey(
                blank=True,
                help_text="optional",
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="route_end",
                to="locations.location",
                verbose_name="end point",
            ),
        ),
        migrations.AlterField(
            model_name="routesettings",
            name="finish_time",
            field=models.TimeField(
                blank=True,
                help_text="optional, will default to now, for route oprimization purposes",
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name="routesettings",
            name="service_time",
            field=models.PositiveIntegerField(
                help_text="Time taken to complete a certain tas"
            ),
        ),
        migrations.AlterField(
            model_name="routesettings",
            name="start_point",
            field=models.ForeignKey(
                help_text="Route Origin",
                on_delete=django.db.models.deletion.PROTECT,
                to="locations.location",
                verbose_name="start point",
            ),
        ),
    ]