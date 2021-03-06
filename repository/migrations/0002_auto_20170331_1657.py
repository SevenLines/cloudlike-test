# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-03-31 16:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileHashedUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.TextField(editable=False, verbose_name='file name')),
            ],
        ),
        migrations.AlterField(
            model_name='file',
            name='hash',
            field=models.TextField(editable=False, verbose_name='file name'),
        ),
        migrations.AddField(
            model_name='filehashedurl',
            name='file',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='repository.File'),
        ),
    ]
