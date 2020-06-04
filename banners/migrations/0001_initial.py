# Generated by Django 2.2.1 on 2020-03-01 22:09

from django.conf import settings
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import helpers.fields
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Banner',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('priority', models.SmallIntegerField(default=10)),
                ('countries', helpers.fields.ChoiceArrayField(base_field=models.CharField(choices=[('FI', 'FI'), ('DE', 'DE'), ('UK', 'UK')], max_length=2), blank=True, default=list, help_text='Leave empty to support all countries', size=None)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('dismissible', models.BooleanField(default=True)),
                ('stopped', models.BooleanField(default=False)),
                ('body', models.TextField()),
                ('languages', helpers.fields.ChoiceArrayField(base_field=models.CharField(choices=[('en', 'en'), ('fi', 'fi'), ('de', 'de')], max_length=3), blank=True, default=list, size=None)),
                ('hash_base64', models.TextField(max_length=256, unique=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('segments', helpers.fields.ChoiceArrayField(base_field=models.CharField(max_length=256), blank=True, default=list, size=None)),
                ('published_at', models.DateTimeField(blank=True, null=True)),
                ('active', models.BooleanField(default=True)),
            ],
            options={
                'ordering': ('-create_time',),
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Page',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('description', models.TextField()),
            ],
            options={
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='Slot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=256, unique=True)),
                ('description', models.TextField()),
                ('hidden', models.BooleanField(default=False)),
                ('page', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='banners.Page')),
            ],
            options={
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('state', models.CharField(choices=[('deactivated', 'Deactivated'), ('live', 'Live (published)')], max_length=128)),
                ('published_at', models.DateTimeField()),
                ('published_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ('-create_time',),
            },
        ),
        migrations.CreateModel(
            name='BannerSnapshot',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ('create_time', models.DateTimeField(auto_now_add=True)),
                ('update_time', models.DateTimeField(auto_now=True)),
                ('priority', models.SmallIntegerField(default=10)),
                ('countries', helpers.fields.ChoiceArrayField(base_field=models.CharField(choices=[('FI', 'FI'), ('DE', 'DE'), ('UK', 'UK')], max_length=2), blank=True, default=list, help_text='Leave empty to support all countries', size=None)),
                ('start_time', models.DateTimeField(blank=True, null=True)),
                ('end_time', models.DateTimeField(blank=True, null=True)),
                ('dismissible', models.BooleanField(default=True)),
                ('stopped', models.BooleanField(default=False)),
                ('body', models.TextField()),
                ('languages', helpers.fields.ChoiceArrayField(base_field=models.CharField(choices=[('en', 'en'), ('fi', 'fi'), ('de', 'de')], max_length=3), blank=True, default=list, size=None)),
                ('hash_base64', models.TextField(max_length=256, unique=True)),
                ('name', models.CharField(max_length=256)),
                ('slot', django.contrib.postgres.fields.jsonb.JSONField()),
                ('segments', django.contrib.postgres.fields.jsonb.JSONField()),
                ('original_banner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='snapshots', to='banners.Banner')),
                ('publication', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='banners', to='banners.Publication')),
                ('publications_log', models.ManyToManyField(blank=True, related_name='snapshots_log', to='banners.Publication')),
            ],
            options={
                'ordering': ('-create_time',),
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='banner',
            name='slot',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='banners.Slot'),
        ),
        migrations.AddConstraint(
            model_name='publication',
            constraint=models.UniqueConstraint(condition=models.Q(state='live'), fields=('state',), name='unique_live_publication'),
        ),
    ]
