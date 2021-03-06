# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-01-28 22:15
from __future__ import unicode_literals

from django.db import migrations, models
import documents.models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0004_auto_20160128_2053'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='file',
            field=models.FileField(upload_to=documents.models.document_file_upload_path),
        ),
        migrations.AlterField(
            model_name='document',
            name='other_pages',
            field=models.ManyToManyField(blank=True, related_name='_document_other_pages_+', to='documents.Document'),
        ),
    ]
