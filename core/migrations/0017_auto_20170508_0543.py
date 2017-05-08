# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-08 03:43
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_auto_20170508_0402'),
    ]

    operations = [
        migrations.AddField(
            model_name='generaloffer',
            name='original_active',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='offer',
            name='original_active',
            field=models.NullBooleanField(),
        ),
        migrations.AddField(
            model_name='offer',
            name='original_total_price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
