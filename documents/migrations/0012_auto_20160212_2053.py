# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-02-12 20:53
from __future__ import unicode_literals

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0011_document_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='document',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(blank=True), blank=True, default=list, size=None),
        ),
    ]