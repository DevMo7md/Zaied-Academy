# Generated by Django 4.2.5 on 2024-09-16 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LP_app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='lesson',
            name='video_1080p_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='video_240p_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='video_360p_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='video_480p_url',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lesson',
            name='video_720p_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]