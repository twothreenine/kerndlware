# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-22 00:36
from __future__ import unicode_literals

import core.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_auto_20161022_0132'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='consumable',
            name='availability',
        ),
        migrations.RemoveField(
            model_name='consumable',
            name='vat',
        ),
        migrations.RemoveField(
            model_name='vat',
            name='description',
        ),
        migrations.AddField(
            model_name='consumable',
            name='presumed_vat',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.VAT'),
        ),
        migrations.AddField(
            model_name='vat',
            name='name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='average_consumption',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='estimated_consumption',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='on_order',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='orderpos',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='planning',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='stock',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='taken',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='consumable',
            name='unit',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Unit'),
        ),
        migrations.AlterField(
            model_name='device',
            name='active',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='devicebyinstalments',
            name='deducted',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='devicebyinstalments',
            name='interval_days',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='devicebyinstalments',
            name='interval_months',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='devicebyinstalments',
            name='number_of_instalments',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='devicecat',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='devicestatus',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='instalment',
            name='rate',
            field=models.FloatField(default=1),
        ),
        migrations.AlterField(
            model_name='material',
            name='capability_oil',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='cleanness',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='foodsave',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='reachability',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='resistance_humidity',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='resistance_light',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='resistance_smell',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='smelliness',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='material',
            name='ventilation',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.ProductCat'),
        ),
        migrations.AlterField(
            model_name='product',
            name='density',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='lossfactor',
            field=core.fields.PercentField(default=0),
        ),
        migrations.AlterField(
            model_name='product',
            name='official',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='sc_essential',
            field=models.CommaSeparatedIntegerField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='sc_favorable',
            field=models.CommaSeparatedIntegerField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='sc_intolerable',
            field=models.CommaSeparatedIntegerField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='sc_unfavorable',
            field=models.CommaSeparatedIntegerField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storability',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_brightness_max',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_brightness_min',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_height_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_height_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_height_optimal',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_humidity_max',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_humidity_min',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_humidity_optimal',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_reachability_min',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_smelliness_max',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_temperature_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_temperature_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_temperature_optimal',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_ventilation_max',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='storage_ventilation_min',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='usual_taking_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='usual_taking_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='productavail',
            name='color',
            field=models.CharField(blank=True, max_length=6),
        ),
        migrations.AlterField(
            model_name='productavail',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='productcat',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='qualityfeature',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='qualityfeature',
            name='conditions_0',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='qualityfeature',
            name='conditions_100',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='qualityfeature',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='qualityfeature',
            name='function',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.QualityFunction'),
        ),
        migrations.AlterField(
            model_name='qualityfeature',
            name='importance',
            field=core.fields.PercentField(default=100),
        ),
        migrations.AlterField(
            model_name='qualityfunction',
            name='a',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='qualityfunction',
            name='b',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='qualityfunction',
            name='c',
            field=models.FloatField(default=0),
        ),
        migrations.AlterField(
            model_name='qualityfunction',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='active_summer',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='active_winter',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='brightness_summer',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='brightness_winter',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='conditions',
            field=models.ManyToManyField(blank=True, null=True, to='core.StorageCondition'),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='depth',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='description',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='height',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='height_level',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='humidity_summer_max',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='humidity_summer_min',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='humidity_winter_max',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='humidity_winter_min',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='loadability',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='reachability_summer',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='reachability_winter',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='smelliness_summer',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='smelliness_winter',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='temperature_summer_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='temperature_summer_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='temperature_winter_max',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='temperature_winter_min',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='ventilation_summer',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='ventilation_winter',
            field=core.fields.PercentField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='storagespace',
            name='width',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supplierrating',
            name='comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='supplierrating',
            name='importance',
            field=core.fields.PercentField(default=100),
        ),
        migrations.AlterField(
            model_name='supplierrating',
            name='official',
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='supplierrating',
            name='reason',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='unit',
            name='weight',
            field=models.FloatField(blank=True, null=True),
        ),
    ]