# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-04 13:52
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_account_active'),
    ]

    operations = [
        migrations.CreateModel(
            name='TimePeriod',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('singular', models.CharField(max_length=30)),
                ('plural', models.CharField(max_length=30)),
                ('days', models.FloatField()),
                ('decimals_shown', models.IntegerField()),
            ],
        ),
    ]
