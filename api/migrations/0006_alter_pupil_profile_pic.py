# Generated by Django 4.1.5 on 2023-01-21 19:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_pupil_profile_pic'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pupil',
            name='profile_pic',
            field=models.ImageField(blank=True, default='profile2.png', null=True, upload_to=''),
        ),
    ]
