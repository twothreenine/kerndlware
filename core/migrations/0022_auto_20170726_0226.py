# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-07-26 00:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_remove_transactiontype_to_balance'),
    ]

    operations = [
        migrations.CreateModel(
            name='TranscriptionToBalance',
            fields=[
                ('transaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.Transaction')),
            ],
            bases=('core.transaction',),
        ),
        migrations.RenameModel(
            old_name='CreditToBalance',
            new_name='Credit',
        ),
        migrations.RenameModel(
            old_name='PayOutBalance',
            new_name='Payout',
        ),
        migrations.RemoveField(
            model_name='payoutdeposit',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='payoutdeposit',
            name='money_box',
        ),
        migrations.RemoveField(
            model_name='depositation',
            name='confirmation_comment',
        ),
        migrations.RemoveField(
            model_name='depositation',
            name='confirmed_by',
        ),
        migrations.RemoveField(
            model_name='depositation',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='depositation',
            name='money_box',
        ),
        migrations.DeleteModel(
            name='CreditToDeposit',
        ),
        migrations.DeleteModel(
            name='PayOutDeposit',
        ),
    ]
