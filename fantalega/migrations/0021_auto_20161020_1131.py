# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-20 09:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantalega', '0020_auto_20161020_1131'),
    ]

    operations = [
        migrations.AlterField(
            model_name='player',
            name='season',
            field=models.CharField(default='2016-2017', max_length=9),
        ),
    ]
