# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-03 08:56
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django_extensions.db.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', django_extensions.db.fields.CreationDateTimeField(auto_now_add=True, verbose_name='created')),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(auto_now=True, verbose_name='modified')),
                ('title', models.CharField(default='Archive', max_length=127, verbose_name='Заголовок')),
                ('dropbox', models.FileField(blank=True, null=True, upload_to='', verbose_name='Путь в Dropbox')),
                ('dropbox_path', models.URLField(blank=True, max_length=127, verbose_name='Прямая ссылка на файл')),
                ('dropbox_thumb', models.URLField(blank=True, max_length=127, verbose_name='Прямая ссылка на превью')),
                ('year', models.PositiveIntegerField(blank=True, null=True, verbose_name='Год')),
                ('month', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(12)], verbose_name='Месяц')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Дата')),
                ('is_image', models.BooleanField(default=False, verbose_name='Этот файл изображение')),
                ('versions', models.ManyToManyField(related_name='_document_versions_+', to='clippings.Document', verbose_name='Версии файла')),
            ],
            options={
                'abstract': False,
                'ordering': ('-modified', '-created'),
                'get_latest_by': 'modified',
            },
        ),
    ]