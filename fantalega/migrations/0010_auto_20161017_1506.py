# -*- coding: utf-8 -*-
# Generated by Django 1.10.1 on 2016-10-17 13:06
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('fantalega', '0009_auto_20160928_1536'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='leaguesteams',
            options={'verbose_name_plural': 'League-Team Associations'},
        ),
        migrations.AlterModelOptions(
            name='lineupsplayers',
            options={'verbose_name_plural': 'Lineup-Player Associations'},
        ),
        migrations.AlterModelOptions(
            name='match',
            options={'verbose_name_plural': 'Matches'},
        ),
        migrations.AddField(
            model_name='team',
            name='user',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='team', to=settings.AUTH_USER_MODEL),
        ),
    ]
