# Generated by Django 5.1.5 on 2025-03-06 18:39

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0003_aitool_context_length_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='aitool',
            name='input_price_per_million_tokens',
        ),
        migrations.RemoveField(
            model_name='aitool',
            name='output_price_per_million_tokens',
        ),
        migrations.RemoveField(
            model_name='aitool',
            name='supports_json_mode',
        ),
        migrations.RemoveField(
            model_name='aitool',
            name='supports_tools',
        ),
        migrations.RemoveField(
            model_name='aitool',
            name='supports_vision',
        ),
        migrations.RemoveField(
            model_name='aitool',
            name='version',
        ),
        migrations.AddField(
            model_name='aitool',
            name='completion_pricing',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='aitool',
            name='latency',
            field=models.IntegerField(default=500),
        ),
        migrations.AddField(
            model_name='aitool',
            name='prompt_pricing',
            field=models.DecimalField(decimal_places=4, default=0, max_digits=10),
        ),
        migrations.AddField(
            model_name='aitool',
            name='supported_parameters',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='aitool',
            name='throughput',
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='aitool',
            name='api_type',
            field=models.CharField(choices=[('openai', 'OpenAI API'), ('huggingface', 'Hugging Face API'), ('custom', 'Custom Integration'), ('none', 'No Integration')], default='none', max_length=50),
        ),
        migrations.AlterField(
            model_name='aitool',
            name='category',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='aitool',
            name='context_length',
            field=models.IntegerField(default=4096),
        ),
        migrations.AlterField(
            model_name='aitool',
            name='modality',
            field=models.CharField(choices=[('text-to-text', 'Text to Text'), ('text-image-to-text', 'Text & Image to Text'), ('other', 'Other')], default='text-to-text', max_length=50),
        ),
        migrations.AlterField(
            model_name='aitool',
            name='release_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='aitool',
            name='series',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
