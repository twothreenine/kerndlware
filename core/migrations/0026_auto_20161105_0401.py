# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-11-05 03:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0025_auto_20161103_0336'),
    ]

    operations = [
        migrations.CreateModel(
            name='PayOutcredit',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Transaction')),
                ('currency', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Currency')),
                ('moneybox', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.MoneyBox')),
            ],
            bases=('core.transaction',),
        ),
        migrations.RemoveField(
            model_name='payoutbalance',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='payoutbalance',
            name='moneybox',
        ),
        migrations.RemoveField(
            model_name='payoutbalance',
            name='transaction_ptr',
        ),
        migrations.RenameField(
            model_name='account',
            old_name='balance',
            new_name='credit',
        ),
        migrations.DeleteModel(
            name='PayOutBalance',
        ),
    ]