# Generated by Django 4.1.8 on 2023-07-25 17:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stops", "0003_alter_stop_stop_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="stop",
            name="stop_status",
            field=models.CharField(
                choices=[
                    ("P", "Pending"),
                    ("IP", "In Progress"),
                    ("AR", "Arrived"),
                    ("EN", "En Route"),
                    ("CL", "Cancel"),
                    ("L", "Left"),
                ],
                default="P",
                max_length=2,
            ),
        ),
    ]
