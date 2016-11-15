# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-13 18:10
from __future__ import unicode_literals

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_auto_20161110_1150'),
    ]

    operations = [
        migrations.CreateModel(
            name='ConsumptionEstimation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('comment', models.TextField()),
                ('relevant', models.BooleanField(default=True)),
                ('entry_date', models.DateField(default=datetime.date.today)),
                ('account', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
                ('consumable', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Consumable')),
            ],
        ),
    ]
