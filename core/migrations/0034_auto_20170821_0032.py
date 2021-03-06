# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-20 22:32
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0033_auto_20170816_1946'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='person',
            name='telephone',
        ),
        migrations.AddField(
            model_name='person',
            name='country',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='person',
            name='notice',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='person',
            name='telephone1',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='person',
            name='telephone2',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='person',
            name='streetnumber',
            field=models.CharField(blank=True, default='', max_length=10),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='person',
            name='website',
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name='person',
            name='zipcode',
            field=models.CharField(blank=True, default='', max_length=10),
            preserve_default=False,
        ),
    ]
