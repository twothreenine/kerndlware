# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2017-08-22 18:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0044_auto_20170822_2004'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='MembershipFee',
            new_name='AccountMembershipFeePhase',
        ),
    ]
