# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-06 00:21
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_timeperiod'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supplier',
            name='is_container_provider',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='is_device_provider',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='is_grower',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='is_packaging_provider',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='is_processor',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='is_retailer',
        ),
        migrations.RemoveField(
            model_name='supplier',
            name='is_wholesale',
        ),
    ]