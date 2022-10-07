# Generated by Django 3.2.13 on 2022-10-07 18:38

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Communication',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sent_time', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('creation_time', models.DateTimeField(default=datetime.datetime.now, null=True)),
                ('is_deleted', models.BooleanField(default=False)),
                ('subject', models.CharField(blank=True, max_length=250)),
                ('to_address', models.TextField()),
                ('cc_address', models.TextField(blank=True, null=True)),
                ('bcc_address', models.TextField(blank=True, null=True)),
                ('from_address', models.EmailField(max_length=250)),
                ('content', models.TextField(blank=True, null=True)),
                ('txt_content', models.TextField(blank=True, null=True)),
                ('is_attachment', models.BooleanField(default=False)),
                ('status', models.IntegerField()),
                ('conversations_flag', models.SmallIntegerField()),
                ('is_system_gen', models.BooleanField(default=False)),
                ('sentiment_type', models.IntegerField()),
            ],
            options={
                'db_table': 'tbl_communication',
            },
        ),
    ]