# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-17 05:27
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0002_auto_20170104_1313'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tournament',
            options={'ordering': ('level',)},
        ),
        migrations.AddField(
            model_name='tournament',
            name='level',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='Уровень'),
        ),
    ]