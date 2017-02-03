# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2017-02-03 09:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rssfeed', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='entry',
            options={'ordering': ['-published'], 'verbose_name_plural': 'entries'},
        ),
        migrations.RenameField(
            model_name='entry',
            old_name='published_time',
            new_name='published',
        ),
        migrations.RenameField(
            model_name='feed',
            old_name='last_polled_time',
            new_name='last_polled',
        ),
        migrations.RenameField(
            model_name='feed',
            old_name='published_time',
            new_name='published',
        ),
        migrations.RenameField(
            model_name='feed',
            old_name='xml_url',
            new_name='url',
        ),
        migrations.AlterField(
            model_name='entry',
            name='image',
            field=models.ImageField(max_length=255, null=True, upload_to=b''),
        ),
        migrations.AlterField(
            model_name='entry',
            name='link',
            field=models.CharField(db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='entry',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='feed',
            name='image',
            field=models.ImageField(max_length=255, null=True, upload_to=b''),
        ),
        migrations.AlterField(
            model_name='feed',
            name='link',
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='feed',
            name='title',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
