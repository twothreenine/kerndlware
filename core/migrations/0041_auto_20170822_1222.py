# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-22 10:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0040_membershipfee_mode'),
    ]

    operations = [
        migrations.AddField(
            model_name='membershipfee',
            name='last_edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.User'),
        ),
        migrations.AddField(
            model_name='membershipfee',
            name='last_edited_on',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
