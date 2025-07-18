# Generated by Django 5.2.1 on 2025-07-12 08:56

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donations', '0004_alter_donation_creation_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='donation',
            name='creation_date',
            field=models.DateTimeField(default=datetime.datetime(2025, 7, 12, 8, 56, 23, 535321, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='donation',
            name='donation_status',
            field=models.CharField(choices=[('APP', 'Approval'), ('PEN', 'Pending'), ('REJ', 'Rejected'), ('CMP', 'Completed')], default='PEN', max_length=3),
        ),
    ]
