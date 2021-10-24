# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-25 09:15
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0023_auto_20190804_1141'),
    ]

    operations = [
        migrations.AddField(
            model_name='team',
            name='team_type',
            field=models.CharField(choices=[('club', 'club'), ('youth', 'youth'), ('nation', 'nation'), ('foreign', 'foreign')], default='club', max_length=32, verbose_name='Короткое название'),
        ),
    ]