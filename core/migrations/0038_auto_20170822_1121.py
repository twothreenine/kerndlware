# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-22 09:21
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0037_auto_20170822_1021'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipfee',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='membershipfee',
            name='period',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TimePeriod'),
        ),
        migrations.AddField(
            model_name='timeperiod',
            name='adjective',
            field=models.CharField(default=' ', max_length=30),
            preserve_default=False,
        ),
    ]
