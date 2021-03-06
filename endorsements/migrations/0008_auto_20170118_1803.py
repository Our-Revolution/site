# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2017-01-18 18:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion



def create_election(apps, schema_editor):
    Election = apps.get_model('endorsements', 'Election')

    Election.objects.create(title='General Election 2016', is_active=False)
    Election.objects.create(title='Primary Election 2017', is_active=True)



class Migration(migrations.Migration):

    dependencies = [
        ('endorsements', '0007_auto_20161025_0022'),
    ]

    operations = [
        migrations.CreateModel(
            name='Election',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128)),
                ('is_active', models.BooleanField(default=False)),
            ],
        ),
        migrations.RunPython(create_election, reverse_code=migrations.RunPython.noop),
        migrations.AddField(
            model_name='candidate',
            name='election',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='endorsements.Election'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='initiative',
            name='election',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='endorsements.Election'),
            preserve_default=False,
        ),
    ]
