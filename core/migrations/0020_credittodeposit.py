# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-09 01:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0019_auto_20170709_0259'),
    ]

    operations = [
        migrations.CreateModel(
            name='CreditToDeposit',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Transaction')),
                ('matter', models.TextField(blank=True)),
            ],
            bases=('core.transaction',),
        ),
    ]