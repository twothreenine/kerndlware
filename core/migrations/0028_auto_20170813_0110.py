# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-12 23:10
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0027_auto_20170810_2310'),
    ]

    operations = [
        migrations.CreateModel(
            name='Inventory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('entry_date', models.DateField(auto_now_add=True)),
                ('comment', models.TextField(blank=True)),
                ('entered_by_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.User')),
            ],
        ),
        migrations.CreateModel(
            name='StockCorrection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Batch')),
                ('status', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TransactionStatus')),
            ],
        ),
        migrations.CreateModel(
            name='Stocktaking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.FloatField()),
                ('additional_tara', models.FloatField(blank=True, null=True)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Batch')),
            ],
        ),
        migrations.CreateModel(
            name='Tare',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=80)),
                ('weight', models.FloatField()),
                ('comment', models.TextField(blank=True)),
                ('entry_date', models.DateField(auto_now_add=True)),
            ],
        ),
        migrations.RenameModel(
            old_name='Insertion',
            new_name='Purchase',
        ),
        migrations.RenameModel(
            old_name='SpecificInsertion',
            new_name='SpecificPurchase',
        ),
        migrations.RenameField(
            model_name='credit',
            old_name='insertion',
            new_name='purchase',
        ),
        migrations.RenameField(
            model_name='specificpurchase',
            old_name='insertion',
            new_name='purchase',
        ),
        migrations.RemoveField(
            model_name='container',
            name='amount_defective',
        ),
        migrations.RemoveField(
            model_name='container',
            name='amount_loaned',
        ),
        migrations.RemoveField(
            model_name='container',
            name='amount_new',
        ),
        migrations.RemoveField(
            model_name='container',
            name='amount_occupied',
        ),
        migrations.RemoveField(
            model_name='container',
            name='amount_ready',
        ),
        migrations.RemoveField(
            model_name='container',
            name='amount_unclean',
        ),
        migrations.RemoveField(
            model_name='container',
            name='buyable',
        ),
        migrations.RemoveField(
            model_name='container',
            name='capability_liquid',
        ),
        migrations.RemoveField(
            model_name='container',
            name='capability_oil',
        ),
        migrations.RemoveField(
            model_name='container',
            name='circular',
        ),
        migrations.RemoveField(
            model_name='container',
            name='cleanability',
        ),
        migrations.RemoveField(
            model_name='container',
            name='cleanness',
        ),
        migrations.RemoveField(
            model_name='container',
            name='depth',
        ),
        migrations.RemoveField(
            model_name='container',
            name='foodsave',
        ),
        migrations.RemoveField(
            model_name='container',
            name='height',
        ),
        migrations.RemoveField(
            model_name='container',
            name='loanable',
        ),
        migrations.RemoveField(
            model_name='container',
            name='mothfree',
        ),
        migrations.RemoveField(
            model_name='container',
            name='reachability',
        ),
        migrations.RemoveField(
            model_name='container',
            name='resistance_humidity',
        ),
        migrations.RemoveField(
            model_name='container',
            name='resistance_light',
        ),
        migrations.RemoveField(
            model_name='container',
            name='resistance_smell',
        ),
        migrations.RemoveField(
            model_name='container',
            name='rodentfree',
        ),
        migrations.RemoveField(
            model_name='container',
            name='smelliness',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare3',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare3_name',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare4',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare4_name',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare5',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare5_name',
        ),
        migrations.RemoveField(
            model_name='container',
            name='tare_without_lid',
        ),
        migrations.RemoveField(
            model_name='container',
            name='ventilation',
        ),
        migrations.RemoveField(
            model_name='container',
            name='volume_easy',
        ),
        migrations.RemoveField(
            model_name='container',
            name='volume_max',
        ),
        migrations.RemoveField(
            model_name='container',
            name='width',
        ),
        migrations.AddField(
            model_name='tare',
            name='container',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Container'),
        ),
        migrations.AddField(
            model_name='stocktaking',
            name='tare',
            field=models.ManyToManyField(blank=True, to='core.Tare'),
        ),
        migrations.AddField(
            model_name='stockcorrection',
            name='stocktaking',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Stocktaking'),
        ),
    ]
