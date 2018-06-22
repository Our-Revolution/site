# -*- coding: utf-8 -*-
# Generated by Django 1.10.2 on 2018-06-20 21:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='EventPromotion',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_sent', models.DateTimeField(null=True)),
                ('date_submitted', models.DateTimeField(auto_now_add=True, null=True)),
                ('event_external_id', models.CharField(db_index=True, max_length=128)),
                ('event_name', models.CharField(blank=True, max_length=128, null=True)),
                ('max_recipients', models.IntegerField()),
                ('message', models.CharField(max_length=2048)),
                ('sender_display_name', models.CharField(default=b'Our Revolution', max_length=128)),
                ('status', models.IntegerField(choices=[(1, 'New'), (2, 'Approved'), (3, 'Sent'), (4, 'Skipped')], default=1)),
                ('subject', models.CharField(default=b'Please come to my Volunteer event', max_length=128)),
                ('user_external_id', models.CharField(db_index=True, max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='EventPromotionRecipient',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_external_id', models.CharField(max_length=128, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='eventpromotion',
            name='recipients',
            field=models.ManyToManyField(blank=True, to='events.EventPromotionRecipient'),
        ),
    ]