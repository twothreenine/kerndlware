# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-04-26 16:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='costsharing',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='costsharing',
            name='participating_accounts',
        ),
        migrations.RemoveField(
            model_name='costsharing',
            name='transaction_ptr',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='participating_accounts',
        ),
        migrations.RemoveField(
            model_name='donation',
            name='transaction_ptr',
        ),
        migrations.RemoveField(
            model_name='proceedssharing',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='proceedssharing',
            name='participating_accounts',
        ),
        migrations.RemoveField(
            model_name='proceedssharing',
            name='transaction_ptr',
        ),
        migrations.RemoveField(
            model_name='recovery',
            name='approved_by',
        ),
        migrations.RemoveField(
            model_name='recovery',
            name='participating_accounts',
        ),
        migrations.RemoveField(
            model_name='recovery',
            name='transaction_ptr',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='basic_price',
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='distance_add',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='distance_total',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='grower',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='grower', to='core.Supplier'),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='orderpos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='processor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='processor', to='core.Supplier'),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='supply_stock',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='generaloffer',
            name='variety',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='offer',
            name='available',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='available_from',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='available_until',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='favorite',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='offer',
            name='official',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='offer',
            name='orderpos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='offer',
            name='supply_stock',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.DeleteModel(
            name='CostSharing',
        ),
        migrations.DeleteModel(
            name='Donation',
        ),
        migrations.DeleteModel(
            name='ProceedsSharing',
        ),
        migrations.DeleteModel(
            name='Recovery',
        ),
    ]