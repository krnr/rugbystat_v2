# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-25 06:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0010_group_city'),
    ]

    operations = [
        migrations.AddField(
            model_name='group',
            name='round_type',
            field=models.CharField(default='round-robin', max_length=127, verbose_name='Тип игр'),
        ),
    ]
