# -*- coding: utf-8 -*-
# Generated by Django 1.11.27 on 2020-01-06 07:25
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0015_auto_20190908_1353'),
    ]

    operations = [
        migrations.AlterField(
            model_name='match',
            name='display_name',
            field=models.CharField(blank=True, max_length=255, verbose_name='Отображение'),
        ),
    ]