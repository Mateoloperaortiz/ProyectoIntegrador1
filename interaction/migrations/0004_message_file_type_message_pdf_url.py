# Generated by Django 5.1.7 on 2025-04-21 03:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interaction", "0003_message_image_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="file_type",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="message",
            name="pdf_url",
            field=models.TextField(blank=True, null=True),
        ),
    ]
