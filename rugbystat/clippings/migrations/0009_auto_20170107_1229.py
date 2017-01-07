# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-07 09:29
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0008_auto_20170107_1146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='tag',
            field=models.ManyToManyField(blank=True, to='teams.TagObject', verbose_name='Содержит сведения о'),
        ),
        migrations.AlterField(
            model_name='document',
            name='versions',
            field=models.ManyToManyField(blank=True, related_name='_document_versions_+', to='clippings.Document', verbose_name='Версии файла'),
        ),
    ]
