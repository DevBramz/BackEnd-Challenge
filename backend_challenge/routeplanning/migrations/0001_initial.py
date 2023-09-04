# Generated by Django 4.1.8 on 2023-06-01 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("organization", "0006_branch_members"),
        ("locations", "0006_alter_location_cords"),
    ]

    operations = [
        migrations.CreateModel(
            name="RouteSettings",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="created at"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="updated at"),
                ),
                (
                    "selection",
                    models.CharField(
                        choices=[
                            (
                                "Min_Veh",
                                "Maximize Available Fleet   Capacity(Minimum Vehicle)",
                            ),
                            (
                                "Min_Distance",
                                "Balance Fleet Capacity  and Driving Time",
                            ),
                            ("MU", "Manual Vehicle Selection"),
                        ],
                        default="Min_Veh",
                        max_length=255,
                        verbose_name="Vehicle Selection",
                    ),
                ),
                ("departure_time", models.TimeField(blank=True, null=True)),
                ("finish_time", models.TimeField(blank=True, null=True)),
                ("service_time", models.PositiveIntegerField()),
                ("avoid_tolls", models.BooleanField(default=True)),
                ("avoid_highways", models.BooleanField(default=True)),
                (
                    "end_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="route_end",
                        to="locations.location",
                        verbose_name="end adress",
                    ),
                ),
                (
                    "organization",
                    models.ForeignKey(
                        help_text="Organization",
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="%(class)ss",
                        related_query_name="%(class)s",
                        to="organization.organization",
                        verbose_name="Organization",
                    ),
                ),
                (
                    "start_address",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="locations.location",
                        verbose_name="start adress",
                    ),
                ),
            ],
            options={
                "verbose_name": "RouteSettings",
                "verbose_name_plural": "RouteSettings",
            },
        ),
    ]
