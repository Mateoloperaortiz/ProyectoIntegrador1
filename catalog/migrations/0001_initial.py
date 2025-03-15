# Generated by Django 5.1.7 on 2025-03-15 22:00

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AITool',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('slug', models.SlugField(blank=True, max_length=100, unique=True)),
                ('description', models.TextField()),
                ('provider', models.CharField(max_length=100)),
                ('website_url', models.URLField()),
                ('category', models.CharField(choices=[('TEXT', 'Text Generation'), ('IMAGE', 'Image Generation'), ('VIDEO', 'Video Generation'), ('AUDIO', 'Audio Generation'), ('CODE', 'Code Generation'), ('CHAT', 'Conversational'), ('SEARCH', 'Search & Research'), ('DATA', 'Data Analysis'), ('TRANS', 'Translation'), ('SUM', 'Summarization'), ('OTHER', 'Other')], max_length=20)),
                ('image', models.ImageField(blank=True, null=True, upload_to='tool_images/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('is_featured', models.BooleanField(default=False)),
                ('popularity', models.IntegerField(default=0)),
                ('api_type', models.CharField(choices=[('OPENAI', 'OpenAI API'), ('HUGGINGFACE', 'Hugging Face API'), ('ANTHROPIC', 'Anthropic API'), ('GOOGLE', 'Google AI API'), ('CUSTOM', 'Custom API'), ('NONE', 'No API Integration')], default='NONE', max_length=20)),
                ('api_endpoint', models.CharField(blank=True, max_length=255, null=True)),
                ('api_model', models.CharField(blank=True, max_length=100, null=True)),
            ],
            options={
                'ordering': ['-popularity', 'name'],
            },
        ),
        migrations.CreateModel(
            name='Rating',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stars', models.IntegerField(choices=[(1, '1 - Poor'), (2, '2 - Fair'), (3, '3 - Good'), (4, '4 - Very Good'), (5, '5 - Excellent')])),
                ('review', models.TextField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('tool', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='catalog.aitool')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
