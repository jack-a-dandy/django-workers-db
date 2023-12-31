# Generated by Django 3.0.8 on 2020-07-19 11:40

from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200717_1623'),
    ]

    operations = [
        migrations.AlterField(
            model_name='worker',
            name='head',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='subordinates', to='app.Worker', verbose_name='Head'),
        ),
        migrations.AddConstraint(
            model_name='worker',
            constraint=models.CheckConstraint(check=models.Q(_negated=True, head=django.db.models.expressions.F('id')), name='worker_head_not_self'),
        ),
    ]
