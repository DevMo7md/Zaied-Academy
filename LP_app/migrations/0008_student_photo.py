# Generated by Django 4.2.5 on 2024-08-13 20:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LP_app', '0007_alter_student_alsaf'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='photo',
            field=models.ImageField(blank=True, null=True, upload_to='student_photos'),
        ),
    ]