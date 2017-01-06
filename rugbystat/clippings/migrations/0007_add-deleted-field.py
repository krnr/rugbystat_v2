# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-06 14:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0006_rename-source-object-link'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='is_deleted',
            field=models.BooleanField(default=False, verbose_name='Файл удален?'),
        ),
        migrations.AlterField(
            model_name='document',
            name='is_image',
            field=models.BooleanField(default=False, verbose_name='Этот файл изображение?'),
        ),
    ]
