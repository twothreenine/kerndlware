# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-13 01:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0029_auto_20170813_0344'),
    ]

    operations = [
        migrations.AddField(
            model_name='purchasestatus',
            name='name',
            field=models.CharField(default='Test', max_length=100),
            preserve_default=False,
        ),
    ]