# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-23 22:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0049_auto_20170823_2326'),
    ]

    operations = [
        migrations.AddField(
            model_name='custommembershipfeephase',
            name='label',
            field=models.CharField(default=' ', max_length=100),
            preserve_default=False,
        ),
    ]
