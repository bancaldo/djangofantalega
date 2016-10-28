# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-28 11:48
from __future__ import unicode_literals
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantalega', '0031_auto_20161028_1239'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='dead_line',
            field=models.DateField(null=True),
        ),
        migrations.AlterField(
            model_name='league',
            name='season',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='leagues', to='fantalega.Season'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='player',
            name='season',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='fantalega.Season'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='evaluation',
            name='season',
            field=models.ForeignKey(default=4, on_delete=django.db.models.deletion.CASCADE, related_name='evaluations', to='fantalega.Season'),
            preserve_default=False,
        ),
    ]
