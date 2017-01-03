# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 07:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0002_auto_20170102_1722'),
    ]

    operations = [
        migrations.AddField(
            model_name='document',
            name='date',
            field=models.DateField(blank=True, null=True, verbose_name='Дата'),
        ),
        migrations.AddField(
            model_name='document',
            name='is_image',
            field=models.BooleanField(default=False, verbose_name='Этот файл изображение'),
        ),
        migrations.AddField(
            model_name='document',
            name='versions',
            field=models.ManyToManyField(related_name='_document_versions_+', to='clippings.Document', verbose_name='Версии файла'),
        ),
        migrations.AddField(
            model_name='document',
            name='year',
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name='Год'),
        ),
        migrations.AlterField(
            model_name='document',
            name='dropbox',
            field=models.FileField(blank=True, null=True, upload_to='', verbose_name='Путь в Dropbox'),
        ),
        migrations.AlterField(
            model_name='document',
            name='dropbox_path',
            field=models.URLField(blank=True, max_length=127, verbose_name='Прямая ссылка на файл'),
        ),
        migrations.AlterField(
            model_name='document',
            name='dropbox_thumb',
            field=models.URLField(blank=True, max_length=127, verbose_name='Прямая ссылка на превью'),
        ),
        migrations.AlterField(
            model_name='document',
            name='title',
            field=models.CharField(default='Archive', max_length=127, verbose_name='Заголовок'),
        ),
    ]
