# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-28 06:38
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0010_new-source-type'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='document',
            name='source',
        ),
        migrations.AddField(
            model_name='document',
            name='source_issue',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='clippings.SourceObject', verbose_name='Выпуск'),
        ),
        migrations.AddField(
            model_name='document',
            name='source_main',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scans', to='clippings.Source', verbose_name='Источник'),
        ),
    ]
