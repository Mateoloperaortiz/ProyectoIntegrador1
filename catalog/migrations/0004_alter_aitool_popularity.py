# Generated by Django 5.1.7 on 2025-03-16 06:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("catalog", "0003_alter_rating_options_rename_review_rating_comment_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="aitool",
            name="popularity",
            field=models.FloatField(default=0),
        ),
    ]
