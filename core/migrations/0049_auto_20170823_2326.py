# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-23 21:26
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0048_auto_20170823_0028'),
    ]

    operations = [
        migrations.CreateModel(
            name='GeneralMembershipFee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('abbr', models.CharField(max_length=30)),
                ('label', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('total', models.BooleanField()),
                ('amount', models.FloatField()),
                ('time_period_multiplicator', models.FloatField(default=1)),
                ('day_specified', models.BooleanField()),
                ('start', models.DateField()),
                ('end', models.DateField(blank=True, null=True)),
                ('enabled', models.BooleanField(default=True)),
                ('previous_performance', models.DateTimeField(blank=True, null=True)),
                ('next_performance', models.DateTimeField(blank=True, null=True)),
                ('recipient_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
            ],
        ),
        migrations.CreateModel(
            name='MembershipPhase',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('end', models.DateField(blank=True, null=True)),
                ('rate', models.FloatField(default=1)),
                ('active', models.BooleanField(default=True)),
                ('comment', models.TextField(blank=True)),
                ('last_edited_on', models.DateField(auto_now=True)),
            ],
        ),
        migrations.AddField(
            model_name='timeperiod',
            name='is_day',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timeperiod',
            name='is_month',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timeperiod',
            name='is_week',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='timeperiod',
            name='is_year',
            field=models.BooleanField(default=False),
        ),
        migrations.CreateModel(
            name='CustomMembershipFeePhase',
            fields=[
                ('membershipphase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.MembershipPhase')),
                ('start', models.DateField()),
                ('time_period_multiplicator', models.FloatField(default=1)),
                ('previous_performance', models.DateTimeField(blank=True, null=True)),
                ('next_performance', models.DateTimeField(blank=True, null=True)),
                ('recipient_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Account')),
                ('time_period', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.TimePeriod')),
            ],
            bases=('core.membershipphase',),
        ),
        migrations.CreateModel(
            name='GeneralMembershipFeePhase',
            fields=[
                ('membershipphase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.MembershipPhase')),
                ('start', models.DateField(blank=True, null=True)),
            ],
            bases=('core.membershipphase',),
        ),
        migrations.CreateModel(
            name='SpecificSharingsMembershipPhase',
            fields=[
                ('membershipphase_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='core.MembershipPhase')),
                ('start', models.DateField(blank=True, null=True)),
            ],
            bases=('core.membershipphase',),
        ),
        migrations.AddField(
            model_name='membershipphase',
            name='account',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.Account'),
        ),
        migrations.AddField(
            model_name='membershipphase',
            name='last_edited_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.User'),
        ),
        migrations.AddField(
            model_name='generalmembershipfee',
            name='time_period',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.TimePeriod'),
        ),
        migrations.AddField(
            model_name='credit',
            name='fee_phase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.MembershipPhase'),
        ),
        migrations.AddField(
            model_name='transfer',
            name='fee_phase',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.MembershipPhase'),
        ),
        migrations.AddField(
            model_name='generalmembershipfeephase',
            name='fee',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.GeneralMembershipFee'),
        ),
    ]
