# Generated by Django 3.0.6 on 2020-05-27 16:17

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='requester',
            name='invite_token',
            field=models.CharField(default=uuid.uuid4, max_length=200),
        ),
    ]
