# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-09-25 04:45
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0005_remove_tournament_from_personseason'),
    ]

    operations = [
        migrations.CreateModel(
            name='Group',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Название')),
                ('date_start', models.DateField(verbose_name='Дата начала')),
                ('date_end', models.DateField(verbose_name='Дата окончания')),
                ('comment', models.TextField(blank=True, verbose_name='Комментарий')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='matches.Season', verbose_name='Розыгрыш')),
            ],
            options={
                'ordering': ('season', 'date_start'),
            },
        ),
    ]
