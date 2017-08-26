# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-22 18:02
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0042_remove_membershipfee_mode'),
    ]

    operations = [
        migrations.CreateModel(
            name='MembershipFeeMode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('no', models.IntegerField()),
                ('abbr', models.CharField(max_length=30)),
                ('label', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='membershipfee',
            name='period',
        ),
        migrations.CreateModel(
            name='RegularFee',
            fields=[
                ('membershipfeemode_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.MembershipFeeMode')),
                ('period', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.TimePeriod')),
            ],
            bases=('core.membershipfeemode',),
        ),
        migrations.AddField(
            model_name='membershipfee',
            name='mode',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='core.MembershipFeeMode'),
            preserve_default=False,
        ),
    ]