# Generated by Django 4.1.8 on 2023-06-15 19:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0009_alter_organization_short_name"),
        ("routeplanning", "0021_alter_routesettings_org_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="routesettings",
            name="org_user",
            field=models.OneToOneField(
                blank=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="routesettings",
                to="organization.orguser",
            ),
        ),
    ]
