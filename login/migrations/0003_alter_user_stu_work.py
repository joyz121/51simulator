# Generated by Django 4.0.2 on 2022-05-10 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('login', '0002_user_stu_work'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='stu_work',
            field=models.CharField(max_length=500),
        ),
    ]
