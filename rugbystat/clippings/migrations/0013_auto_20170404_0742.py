# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-04-04 04:42
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0012_rename-clippings-fields-real'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='document',
            options={'ordering': ('year', 'month', 'title')},
        ),
        migrations.AddField(
            model_name='document',
            name='kind',
            field=models.CharField(blank=True, choices=[('photo', 'фото'), ('newspaper', 'газета'), ('magazine', 'журнал'), ('protocol', 'протокол'), ('program', 'программка'), ('book', 'книга'), ('other', 'прочее')], max_length=127, verbose_name='Тип'),
        ),
        migrations.AlterField(
            model_name='document',
            name='year',
            field=models.PositiveSmallIntegerField(blank=True, null=True, validators=(django.core.validators.MinValueValidator(1800), django.core.validators.MaxValueValidator(2100)), verbose_name='Год создания'),
        ),
        migrations.AlterField(
            model_name='source',
            name='type',
            field=models.CharField(choices=[('photo', 'фото'), ('newspaper', 'газета'), ('magazine', 'журнал'), ('protocol', 'протокол'), ('program', 'программка'), ('book', 'книга'), ('other', 'прочее')], default='photo', max_length=127, verbose_name='Тип'),
        ),
    ]