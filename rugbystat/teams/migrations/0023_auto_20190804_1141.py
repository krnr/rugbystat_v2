# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-08-04 08:41
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('matches', '0010_group_city'),
        ('teams', '0022_auto_20190723_1342'),
    ]

    operations = [
        migrations.CreateModel(
            name='GroupSeason',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('place', models.CharField(blank=True, max_length=2, verbose_name='Место')),
                ('played', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='И')),
                ('wins', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='В')),
                ('draws', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Н')),
                ('losses', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='П')),
                ('points', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='О')),
                ('score', models.CharField(blank=True, max_length=10, verbose_name='Р/О')),
                ('order', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MaxValueValidator(40)], verbose_name='Сортировка')),
                ('name', models.CharField(blank=True, max_length=127, verbose_name='Название команды в группе')),
                ('year', models.PositiveSmallIntegerField(blank=True, null=True, validators=[django.core.validators.MinValueValidator(1900), django.core.validators.MaxValueValidator(2100)], verbose_name='Год')),
                ('story', models.TextField(blank=True, verbose_name='История')),
                ('group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='standings', to='matches.Group', verbose_name='Группа')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='groups', to='teams.Team', verbose_name='Команда')),
            ],
            options={
                'ordering': ('-year', 'team', 'order'),
            },
        ),
        migrations.AlterField(
            model_name='teamseason',
            name='name',
            field=models.CharField(blank=True, max_length=127, verbose_name='Название команды в турнире'),
        ),
        migrations.AlterUniqueTogether(
            name='groupseason',
            unique_together=set([('team', 'group')]),
        ),
    ]