# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-04 10:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0002_add-city-name'),
    ]

    operations = [
        migrations.AddField(
            model_name='city',
            name='short_name',
            field=models.CharField(blank=True, max_length=4, verbose_name='Короткое название'),
        ),
    ]