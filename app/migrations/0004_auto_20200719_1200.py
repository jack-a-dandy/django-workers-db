# Generated by Django 3.0.8 on 2020-07-19 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_auto_20200719_1140'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='worker',
            name='worker_head_not_self',
        ),
    ]