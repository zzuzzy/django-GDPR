# Generated by Django 2.1.5 on 2019-02-08 09:38

from django.db import migrations, models
import django.db.models.deletion
import gdpr.mixins


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('tests', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('note', models.TextField()),
                ('object_id', models.PositiveIntegerField()),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
            options={
                'abstract': False,
            },
            bases=(gdpr.mixins.AnonymizationModelMixin, models.Model),
        ),
    ]
