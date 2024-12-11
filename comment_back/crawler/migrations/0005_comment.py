# Generated by Django 5.1.3 on 2024-12-11 05:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0004_episode_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('content', models.TextField()),
                ('created_at', models.DateTimeField()),
                ('is_best', models.BooleanField()),
                ('user_name', models.CharField(max_length=100)),
                ('user_thumbnail_url', models.TextField()),
                ('user_uid', models.IntegerField()),
                ('episode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.episode')),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.series')),
            ],
        ),
    ]
