# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-01-14 03:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Restitution',
            fields=[
                ('batchtransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.BatchTransaction')),
                ('approval_comment', models.TextField(blank=True)),
                ('approved_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.User')),
            ],
            bases=('core.batchtransaction',),
        ),
        migrations.CreateModel(
            name='Taking',
            fields=[
                ('batchtransaction_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.BatchTransaction')),
            ],
            bases=('core.batchtransaction',),
        ),
        migrations.AddField(
            model_name='restitution',
            name='original_taking',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Taking'),
        ),
    ]