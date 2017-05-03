# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-26 17:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20170426_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='account',
            name='original_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='batch',
            name='original_id',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='original_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]