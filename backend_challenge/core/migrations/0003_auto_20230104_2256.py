# Generated by Django 3.1.1 on 2023-01-04 22:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20230104_2215'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='delivery',
            name='city',
        ),
        migrations.AlterField(
            model_name='delivery',
            name='address',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]