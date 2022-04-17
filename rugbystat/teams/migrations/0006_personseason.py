# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-07-13 05:13
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('teams', '0005_new-source-type'),
    ]

    operations = [
        migrations.CreateModel(
            name='PersonSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=(django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2100)), verbose_name='Год')),
                ('role', models.CharField(choices=[('player', 'игрок'), ('prop', '1/3'), ('hooker', '2'), ('lock', '4/5'), ('backrow', '6-8'), ('scrum-half', '9'), ('fly-half', '10'), ('center', '12/13'), ('winger', '11/14'), ('fullback', '15'), ('referee', 'судья'), ('coach', 'тренер')], default='player', max_length=127, verbose_name='Тип')),
                ('story', models.TextField(blank=True, verbose_name='История')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='seasons', to='teams.Person', verbose_name='Персона')),
            ],
        ),
    ]