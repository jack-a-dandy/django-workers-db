# Generated by Django 3.0.8 on 2020-07-17 16:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True, verbose_name='Position')),
            ],
            options={
                'db_table': 'positions',
                'ordering': ('name',),
            },
        ),
        migrations.CreateModel(
            name='Worker',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50, verbose_name='First name')),
                ('last_name', models.CharField(max_length=50, verbose_name='Last name')),
                ('patronymic', models.CharField(max_length=55, verbose_name='Patronymic')),
                ('recruitment_date', models.DateField(verbose_name='Recruitment date')),
                ('salary', models.IntegerField(verbose_name='Salary')),
                ('photo', models.ImageField(blank=True, null=True, upload_to='photos', verbose_name='Photo')),
                ('head', models.ForeignKey(null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='subordinate', to='app.Worker', verbose_name='Head')),
                ('position', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='workers', to='app.Position', verbose_name='Position')),
            ],
            options={
                'db_table': 'workers',
            },
        ),
    ]
