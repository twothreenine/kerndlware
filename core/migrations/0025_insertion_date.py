# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-09 20:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_auto_20170808_0508'),
    ]

    operations = [
        migrations.AddField(
            model_name='insertion',
            name='date',
            field=models.DateField(default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
