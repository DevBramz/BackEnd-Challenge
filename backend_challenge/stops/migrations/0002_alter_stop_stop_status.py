# Generated by Django 4.1.8 on 2023-07-08 22:54

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("stops", "0001_initial"),
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
                    ("EN", "In Progress"),
                    ("CL", "Cancel"),
                    ("C", "Completed"),
                ],
                default="P",
                max_length=2,
            ),
        ),
    ]
