# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-05-07 16:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_auto_20170506_1645'),
    ]

    operations = [
        migrations.CreateModel(
            name='OfferAvailability',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('available', models.BooleanField(default=True)),
                ('start', models.DateField(blank=True, null=True)),
                ('end', models.DateField(blank=True, null=True)),
                ('season_start', models.DateField(blank=True, null=True)),
                ('season_end', models.DateField(blank=True, null=True)),
                ('comment', models.TextField(blank=True)),
                ('general_offers', models.ManyToManyField(to='core.GeneralOffer')),
            ],
        ),
        migrations.RemoveField(
            model_name='offer',
            name='available',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='available_from',
        ),
        migrations.RemoveField(
            model_name='offer',
            name='available_until',
        ),
        migrations.AddField(
            model_name='product',
            name='season_end',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='season_start',
            field=models.DateField(blank=True, null=True),
        ),
    ]
