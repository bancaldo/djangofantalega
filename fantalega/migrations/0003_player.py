# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-09-26 10:33
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('fantalega', '0002_auto_20160926_0854'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.IntegerField()),
                ('name', models.CharField(max_length=32)),
                ('real_team', models.CharField(max_length=3)),
                ('cost', models.IntegerField()),
                ('auction_value', models.IntegerField()),
                ('role', models.CharField(max_length=16)),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='fantalega.Team')),
            ],
        ),
    ]
