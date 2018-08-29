# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-25 05:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0018_add_group_model'),
        ('matches', '0006_add_group_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='teams',
            field=models.ManyToManyField(blank=True, null=True, related_name='groups', to='teams.TeamSeason'),
        ),
    ]