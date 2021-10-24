# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-10-28 09:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0008_remove_match_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='away_halfscore',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='1 тайм гостей'),
        ),
        migrations.AlterField(
            model_name='match',
            name='home_halfscore',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='1 тайм хозяев'),
        ),
    ]