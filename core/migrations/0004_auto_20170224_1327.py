# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-24 12:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_costsharing_donation_proceedssharing_recovery'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sharetransaction',
            name='originator_charge',
        ),
        migrations.AddField(
            model_name='sharetransaction',
            name='originator_share',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='originator_share', to='core.Charge'),
        ),
    ]
