# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-03 10:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_auto_20170103_1051'),
    ]

    operations = [
        migrations.AddField(
            model_name='charge',
            name='date',
            field=models.DateField(default='2014-01-01'),
            preserve_default=False,
        ),
    ]
