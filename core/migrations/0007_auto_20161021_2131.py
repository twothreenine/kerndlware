# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-21 21:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20161021_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='date_of_expiry',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='batch',
            name='production_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='batch',
            name='purchase_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]