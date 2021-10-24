# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-12-10 11:43
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('clippings', '0015_auto_20170404_0821'),
        ('teams', '0019_auto_20171028_1244'),
    ]

    operations = [
        migrations.CreateModel(
            name='TagThrough',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clippings.Document')),
                ('tag', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='teams.TagObject')),
            ],
        ),
    ]