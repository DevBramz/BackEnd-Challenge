# Generated by Django 4.1.8 on 2023-06-15 04:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("organization", "0009_alter_organization_short_name"),
        ("routeplanning", "0019_rename_user_routesettings_org_user"),
    ]

    operations = [
        migrations.AlterField(
            model_name="routesettings",
            name="org_user",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="organization.orguser"
            ),
        ),
    ]
