# Generated by Django 3.2.7 on 2021-10-03 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0024_auto_20210302_0630'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='date_of_birth',
        ),
        migrations.RemoveField(
            model_name='author',
            name='date_of_death',
        ),
    ]
