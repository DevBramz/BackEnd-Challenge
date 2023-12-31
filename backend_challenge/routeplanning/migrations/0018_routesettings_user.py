# Generated by Django 4.1.8 on 2023-06-15 02:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0009_alter_organization_short_name"),
        ("routeplanning", "0017_routesettings_departure_time"),
    ]

    operations = [
        migrations.AddField(
            model_name="routesettings",
            name="user",
            field=models.ForeignKey(
                default=1,
                on_delete=django.db.models.deletion.CASCADE,
                to="organization.orguser",
            ),
            preserve_default=False,
        ),
    ]
