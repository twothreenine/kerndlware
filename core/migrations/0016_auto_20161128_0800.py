# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-28 07:00
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_auto_20161120_1722'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='AccPayPhases',
            new_name='AccPayPhase',
        ),
    ]