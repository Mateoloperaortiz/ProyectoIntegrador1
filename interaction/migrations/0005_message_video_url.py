# Generated by Django 5.1.7 on 2025-04-21 04:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("interaction", "0004_message_file_type_message_pdf_url"),
    ]

    operations = [
        migrations.AddField(
            model_name="message",
            name="video_url",
            field=models.TextField(blank=True, null=True),
        ),
    ]
