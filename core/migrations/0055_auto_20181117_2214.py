# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2018-11-17 21:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0054_auto_20180502_1928'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='VirtualUser',
            new_name='VirtualProfile',
        ),
        migrations.RenameField(
            model_name='virtualprofile',
            old_name='user_ptr',
            new_name='profile_ptr',
        ),
    ]
