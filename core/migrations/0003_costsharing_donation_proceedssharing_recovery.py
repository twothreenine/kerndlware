# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-02-24 12:25
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_20170224_1323'),
    ]

    operations = [
        migrations.CreateModel(
            name='CostSharing',
            fields=[
                ('sharetransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ShareTransaction')),
            ],
            bases=('core.sharetransaction',),
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('sharetransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ShareTransaction')),
            ],
            bases=('core.sharetransaction',),
        ),
        migrations.CreateModel(
            name='ProceedsSharing',
            fields=[
                ('sharetransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ShareTransaction')),
            ],
            bases=('core.sharetransaction',),
        ),
        migrations.CreateModel(
            name='Recovery',
            fields=[
                ('sharetransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.ShareTransaction')),
            ],
            bases=('core.sharetransaction',),
        ),
    ]
