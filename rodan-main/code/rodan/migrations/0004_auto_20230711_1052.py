# Generated by Django 2.0.13 on 2023-07-11 14:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rodan', '0003_auto_20230627_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='connection',
            name='offset_x',
            field=models.FloatField(null=True),
        ),
        migrations.AddField(
            model_name='connection',
            name='offset_y',
            field=models.FloatField(null=True),
        ),
    ]
