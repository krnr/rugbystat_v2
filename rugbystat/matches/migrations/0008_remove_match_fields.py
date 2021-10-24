# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-28 05:20
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0007_add_group_teamseason_relatition'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'ordering': ('season', 'date_end')},
        ),
        migrations.RemoveField(
            model_name='match',
            name='ref',
        ),
        migrations.RemoveField(
            model_name='match',
            name='stadium',
        ),
        migrations.AddField(
            model_name='match',
            name='away_halfscore',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Счёт 1т гостей'),
        ),
        migrations.AddField(
            model_name='match',
            name='home_halfscore',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='Счёт 1т хозяев'),
        ),
        migrations.AlterField(
            model_name='group',
            name='teams',
            field=models.ManyToManyField(blank=True, related_name='groups', to='teams.TeamSeason'),
        ),
    ]