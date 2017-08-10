# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-10 21:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_account_comment'),
    ]

    operations = [
        migrations.AddField(
            model_name='insertion',
            name='entered_by_user',
            field=models.ForeignKey(default=235, on_delete=django.db.models.deletion.CASCADE, to='core.User'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='insertion',
            name='entry_date',
            field=models.DateField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
