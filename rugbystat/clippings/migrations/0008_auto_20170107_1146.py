# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-07 08:46
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0007_add-deleted-field'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='dropbox_thumb',
            field=models.URLField(blank=True, max_length=127, null=True, verbose_name='Прямая ссылка на превью'),
        ),
    ]