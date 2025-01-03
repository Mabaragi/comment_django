# Generated by Django 5.1.3 on 2024-12-07 20:43

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='series',
            old_name='series_id',
            new_name='id',
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('category', models.CharField(max_length=10)),
                ('subcategory', models.CharField(max_length=20)),
                ('series', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='crawler.series')),
            ],
        ),
    ]
