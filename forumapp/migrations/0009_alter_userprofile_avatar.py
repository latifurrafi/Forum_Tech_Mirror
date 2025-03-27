# Generated by Django 5.1.7 on 2025-03-27 19:33

import forumapp.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('forumapp', '0008_alter_userprofile_avatar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='avatar',
            field=models.ImageField(default='avatars/default.jpg', upload_to='avatars/', validators=[forumapp.models.validate_image_format]),
        ),
    ]
