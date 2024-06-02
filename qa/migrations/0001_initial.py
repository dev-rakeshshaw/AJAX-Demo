# Generated by Django 4.1.11 on 2024-06-01 15:07

from django.db import migrations, models
import django.db.models.deletion
import qa.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('number_of_pages', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Pages',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('raw_text', models.TextField()),
                ('date', models.DateField(default=qa.models.random_date)),
                ('is_duplicate', models.BooleanField(default=False)),
                ('file', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pages', to='qa.file')),
            ],
        ),
    ]
